import re
from docx import Document

PLACEHOLDER_PATTERN = r"\{\{(.*?)\}\}"


class WordProcessor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.document = Document(filepath)

    # ------------------------------------------------------------------
    # Iterate every paragraph in the document including tables
    # ------------------------------------------------------------------

    def _all_paragraphs(self):
        """
        Yield every paragraph in the document:
        - body paragraphs
        - paragraphs inside table cells (all rows, all cells, nested tables)
        """
        yield from self.document.paragraphs
        for table in self.document.tables:
            yield from self._paragraphs_in_table(table)

    def _paragraphs_in_table(self, table):
        for row in table.rows:
            for cell in row.cells:
                yield from cell.paragraphs
                for nested in cell.tables:
                    yield from self._paragraphs_in_table(nested)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_placeholders(self) -> list:
        """Return all placeholder names found anywhere in the document."""
        found = []
        for para in self._all_paragraphs():
            found.extend(re.findall(PLACEHOLDER_PATTERN, para.text))
        return found

    def fill_placeholders(self, mapping: dict, output_path: str) -> None:
        """
        Replace every {{placeholder}} in the document with its mapped value.
        Handles table cells and placeholders split across multiple runs.
        """
        for para in self._all_paragraphs():
            self._replace_in_paragraph(para, mapping)
        self.document.save(output_path)

    def _replace_in_paragraph(self, paragraph, mapping: dict) -> None:
        """
        Word splits placeholders across runs (e.g. '{{' | 'field' | '}}').
        Strategy: join all run text, replace, write back to first run.
        """
        if not paragraph.runs:
            return

        full_text = "".join(run.text for run in paragraph.runs)
        if "{{" not in full_text:
            return

        replaced = full_text
        for placeholder, value in mapping.items():
            if placeholder in replaced:
                replaced = replaced.replace(placeholder, str(value))

        if replaced == full_text:
            return

        paragraph.runs[0].text = replaced
        for run in paragraph.runs[1:]:
            run.text = ""
