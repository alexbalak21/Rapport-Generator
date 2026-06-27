"""
Handles report generation logic triggered from the GUI.
"""
import os
import datetime

from app.core.report_generator import ReportGenerator
from app.repository.rapport_repository import save_report


def generate_report(excel: str, docx: str, mapping: str, row_number: int) -> str:
    """
    Run the report generator and return the final output path.
    Output directory and filename are resolved from the mapping's config/file_name.
    Raises on any error — caller is responsible for showing the error to the user.
    """
    generator = ReportGenerator(
        excel_path=excel,
        template_path=docx,
        mapping_path=mapping,
    )

    # Pass a fallback path — generator will override it with output_dir + file_name
    fallback_path = os.path.join(os.getcwd(), f"report_row_{row_number}.docx")
    final_path = generator.generate(row_number=row_number, output_path=fallback_path)

    _log_report(excel, docx, mapping, row_number)

    return final_path


def _log_report(excel: str, docx: str, mapping: str, row_number: int) -> None:
    """Append report metadata to SQLite — silently ignored on failure."""
    try:
        save_report(
            report_id=f"row_{row_number}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            created_at=datetime.datetime.now().isoformat(),
            excel_path=excel,
            template_path=docx,
            mapping_path=mapping,
            row_number=row_number,
            data={},
        )
    except Exception:
        pass