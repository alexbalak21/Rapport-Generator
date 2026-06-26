# Rapport-Generator

A desktop application for generating Word `.docx` reports from Excel data, driven by JSON mapping configurations and a Tkinter GUI.

---

## Features

- Select an Excel `.xlsx` data file, a Word `.docx` template, and a JSON mapping file from the GUI
- Generate fully populated Word reports with a single click
- Support for multiple mapping configurations (one per report type / template)
- Computed fields: today's date, text transformations, string formatting, concatenation, auto-incrementing report numbers
- Persistent GUI state — last used Excel file, template, mapping, and row number are restored on next launch
- Full audit trail: every generated report is logged to a local SQLite database

---

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`

```
et_xmlfile==2.0.0
lxml==6.1.1
openpyxl==3.1.5
python-docx==1.2.0
typing_extensions==4.15.0
```

---

## Installation

```powershell
# 1. Create and activate a virtual environment
python -m venv env
.\env\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt
```

---

## Running the application

```powershell
python app/app.py
```

---

## Project structure

```
Rapport-Generator/
├── app/
│   ├── app.py                        # Entry point
│   ├── core/
│   │   ├── excel_reader.py           # Reads rows from .xlsx
│   │   ├── mapping_loader.py         # Parses mapping.json
│   │   ├── processors.py             # Built-in field operations
│   │   ├── report_generator.py       # Orchestrates report creation
│   │   ├── state_manager.py          # Manages report_state.json (report numbering)
│   │   └── word_processor.py         # Fills placeholders in .docx template
│   ├── gui/
│   │   ├── file_dialogs.py           # File picker helpers
│   │   └── main_window.py            # Main Tkinter window
│   ├── mappings/
│   │   ├── data.json                 # Default mapping configuration
│   │   └── report_state.json         # Tracks last report number (auto-managed)
│   └── repository/
│       ├── config_repository.py      # SQLite persistence for GUI config
│       └── rapport_repository.py     # SQLite persistence for generated reports
├── app_data.db                       # SQLite database (auto-created on first run)
├── data.xlsx                         # Example Excel data file
├── template.docx                     # Example Word template
├── inspect_report.py                 # CLI utility to inspect generated reports
├── tests/
│   ├── test_report_generator.py
│   └── test_word_processor.py
├── requirements.txt
└── README.md
```

---

## How it works

### Data flow

```
Excel (.xlsx)  +  mapping.json  +  Word template (.docx)
                      ↓
             ReportGenerator
                      ↓
         Computed fields resolved
                      ↓
         Placeholders filled in template
                      ↓
           Output report saved (.docx)
                      ↓
         Metadata logged to SQLite
```

### Word template placeholders

Placeholders in the `.docx` template must use double-brace syntax:

```
{{date}}
{{species}}
{{report_number}}
{{today_date}}
```

---

## Mapping configuration (`mapping.json`)

The mapping file controls how Excel columns and computed fields are mapped to template placeholders. Each mapping file corresponds to one report type and one template.

### Simple column mapping

Maps an Excel column directly to a placeholder:

```json
{
  "date":      "{{date}}",
  "species":   "{{species}}",
  "address":   "{{address}}",
  "inspector": "{{inspector}}",
  "notes":     "{{notes}}"
}
```

The key is the Excel column header; the value is the placeholder in the Word template.

### Computed fields

Computed fields generate values that do not come directly from Excel:

```json
{
  "today_date": {
    "operation": "today",
    "format": "%d/%m/%Y"
  }
}
```

The key becomes the placeholder name (`{{today_date}}`).

---

## Supported operations

| Operation       | Description                                     | Parameters                        |
|-----------------|-------------------------------------------------|-----------------------------------|
| `today`         | Today's date                                    | `format` — strftime format string |
| `uppercase`     | Converts an Excel field to uppercase            | `input` — Excel column name       |
| `lowercase`     | Converts an Excel field to lowercase            | `input` — Excel column name       |
| `format`        | Formats a string using Excel column values      | `format` — Python format string   |
| `concat`        | Concatenates multiple Excel fields              | `parts` — list of column names    |
| `report_number` | Auto-incremented daily report number (`YYMMDD-XX`) | _(none)_                      |

### Examples

```json
{
  "today_date": {
    "operation": "today",
    "format": "%d/%m/%Y"
  },
  "species_upper": {
    "operation": "uppercase",
    "input": "species"
  },
  "full_line": {
    "operation": "format",
    "format": "{species} inspected on {date}"
  },
  "combined": {
    "operation": "concat",
    "parts": ["species", "address"]
  },
  "report_number": {
    "operation": "report_number"
  }
}
```

---

## Report numbering

Report numbers are generated automatically and follow the format:

```
YYMMDD-XX
```

For example: `260626-03` is the third report generated on 26 June 2026.

The counter resets to `01` each new day. The last generated number is stored in `app/mappings/report_state.json` and updated automatically — do not edit this file manually.

---

## Multiple mappings

The system supports multiple mapping files for different templates and report types. Place them in `app/mappings/` (or any folder):

```
app/mappings/
    data.json
    inspection.json
    animals.json
    vehicles.json
```

Use the **Select mapping.json** button in the GUI to switch between them. The last selected mapping is remembered across sessions.

---

## GUI — persistent state

The GUI automatically restores the last used files and row number on each launch. All settings are stored in `app_data.db` (SQLite, auto-created).

| Setting            | Stored key          |
|--------------------|---------------------|
| Excel file path    | `last_excel_path`   |
| Template path      | `last_docx_path`    |
| Mapping file path  | `last_mapping_path` |
| Last row number    | `last_line_number`  |

On startup, the row selector is initialised to `last_line_number + 1`, so you can generate reports sequentially without adjusting anything.

---

## SQLite database

`app_data.db` is created automatically in the project root on first run. It contains two tables:

### `config` — GUI settings

```
key   TEXT PRIMARY KEY
value TEXT
```

### `reports` — audit log

```
id            TEXT PRIMARY KEY   -- unique ID per report
created_at    TEXT               -- ISO 8601 timestamp
excel_path    TEXT
template_path TEXT
mapping_path  TEXT
row_number    INTEGER
data_json     TEXT               -- full JSON of all data used
```

Every successfully generated report is appended here, providing a complete audit trail.

---

## Adding a new operation

1. Add a function to `app/core/processors.py`:

```python
def op_my_operation(rule, row_data):
    input_col = rule.get("input", "")
    value = row_data.get(input_col, "")
    return value.title()  # example: title-case
```

2. Register it in `app/core/report_generator.py`:

```python
self.operations = {
    ...
    "my_operation": processors.op_my_operation,
}
```

3. Use it in a mapping file:

```json
"my_field": {
  "operation": "my_operation",
  "input": "species"
}
```

4. Add `{{my_field}}` to the Word template.

---

## Running tests

```powershell
pip install pytest
python -m pytest
```

---

## Utility script

`inspect_report.py` can be run directly to test report generation without the GUI:

```powershell
python inspect_report.py
```
