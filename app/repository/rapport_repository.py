import os
import re
from .excel_reader import ExcelReader
from .word_processor import WordProcessor
from .mapping_loader import MappingLoader
from .state_manager import ReportStateManager
from . import processors

# Characters illegal in Windows filenames
_ILLEGAL_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


class ReportGenerator:
    def __init__(self, excel_path, template_path, mapping_path):
        self.excel_path    = excel_path
        self.template_path = template_path
        self.mapping_path  = mapping_path

        self.mapping_loader = MappingLoader(mapping_path)
        self.state_manager  = ReportStateManager(
            os.path.join(os.path.dirname(mapping_path), "report_state.json")
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_header(value) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        sanitized = _ILLEGAL_FILENAME_CHARS.sub("_", name)
        sanitized = sanitized.strip(". ")
        return sanitized or "report"

    @staticmethod
    def _normalize_field_value(value) -> str:
        import datetime as dt
        if isinstance(value, (dt.datetime, dt.date)):
            return value.strftime("%Y-%m-%d")
        if value is None:
            return ""
        return str(value).strip()

    def _build_operations(self, excel_reader: ExcelReader) -> dict:
        """
        Return the operations map.
        Lookup operations receive the excel_reader via closure so they can
        access any sheet without changing the (rule, row_data) signature used
        by all other operations.
        """
        return {
            "today":         processors.op_today,
            "uppercase":     processors.op_uppercase,
            "lowercase":     processors.op_lowercase,
            "format":        processors.op_format,
            "concat":        processors.op_concat,
            "report_number": lambda rule, row: self.state_manager.generate_report_number(),
            "lookup":        lambda rule, row: processors.op_lookup(rule, row, excel_reader),
            "lookup_join":   lambda rule, row: processors.op_lookup_join(rule, row, excel_reader),
        }

    def compute_value(self, rule: dict, row_data: dict, operations: dict):
        operation = rule.get("operation")
        func = operations.get(operation)
        return func(rule, row_data) if func else None

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def generate(self, row_number: int, output_path: str) -> str:
        # ── Load Excel (all sheets) ───────────────────────────────────
        excel = ExcelReader(self.excel_path)
        excel.load()
        raw_row  = excel.get_row_as_dict(row_number)
        row_data = {k: self._normalize_field_value(v) for k, v in raw_row.items()}

        operations    = self._build_operations(excel)
        mapping       = self.mapping_loader.load()
        excel_columns = {self._normalize_header(c) for c in excel.get_columns()}

        word                  = WordProcessor(self.template_path)
        available_placeholders = set(word.extract_placeholders())

        filled:          dict[str, str] = {}
        computed_values: dict[str, str] = {}

        # ── Pass 1: simple column mappings ────────────────────────────
        for key, rule in mapping.items():
            if not isinstance(rule, str):
                continue
            normalized_key = self._normalize_header(key)
            if normalized_key not in excel_columns:
                continue
            if normalized_key not in row_data:
                continue
            match = re.search(r"\{\{(.*?)\}\}", rule)
            if not match:
                continue
            placeholder_name = match.group(1).strip()
            if placeholder_name not in available_placeholders:
                continue
            value = row_data[normalized_key]
            filled[rule] = value
            computed_values[key] = value

        # ── Pass 2: computed fields (excluding file_name) ─────────────
        # Iterates until no new values are resolved, supporting dependency chains.
        max_passes = len(mapping) + 1
        for _ in range(max_passes):
            resolved_any = False
            for key, rule in mapping.items():
                if not isinstance(rule, dict):
                    continue
                if key == "file_name":
                    continue
                if key in computed_values:
                    continue  # already resolved

                enriched = {**row_data, **computed_values}
                try:
                    value = self.compute_value(rule, enriched, operations)
                except Exception:
                    value = None

                if value is None:
                    continue

                computed_values[key] = str(value)
                resolved_any = True

                placeholder_full = f"{{{{{key}}}}}"
                if key in available_placeholders:
                    filled[placeholder_full] = str(value)

            if not resolved_any:
                break

        # ── Pass 3: file_name (resolved last so it can use report_number) ──
        file_name_rule    = mapping.get("file_name")
        resolved_filename = None
        if isinstance(file_name_rule, dict):
            enriched = {**row_data, **computed_values}
            try:
                raw_name = self.compute_value(file_name_rule, enriched, operations)
                if raw_name:
                    resolved_filename = self._sanitize_filename(raw_name)
            except Exception:
                pass

        # ── Write output ──────────────────────────────────────────────
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        word.fill_placeholders(filled, output_path)
        return output_path