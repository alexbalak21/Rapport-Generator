# GUI Update – Mapping Selection + Config Persistence

This document explains the new GUI features related to:
- Selecting a mapping/configuration file
- Persisting the last selected mapping in SQLite
- Displaying and editing the line number using + / – buttons
- Automatically restoring the last used Excel, template, mapping, and line

---

# 1. New SQLite Table: `config`

The `config` table stores persistent GUI settings.

```
config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
)
```

## 1.1 Stored keys

| Key                  | Description                                  |
|----------------------|----------------------------------------------|
| `last_excel_path`    | Last selected `.xlsx` file                   |
| `last_docx_path`     | Last selected `.docx` template               |
| `last_mapping_path`  | Last selected `mapping.json` configuration   |
| `last_line_number`   | Last selected line number                    |

All values are stored as TEXT.

---

# 2. Mapping Selection in the GUI

A new button is added:

```
[ Select mapping.json ]
```

When clicked:
- A file dialog opens
- The user selects a JSON configuration file
- The path is saved to `config.last_mapping_path`
- The GUI displays the selected mapping file

On next launch:
- The GUI automatically reloads the last mapping file
- The user does not need to reselect it

---

# 3. Multiple Mappings for Multiple Templates

The system now supports multiple configurations:

```
/mappings/
    data.json
    inspection.json
    animals.json
    vehicles.json
    custom_template.json
```

Each mapping corresponds to:
- A specific Word template
- A specific report type
- A specific set of computed fields

The GUI allows selecting any of them.

---

# 4. Line Selector Widget

The line selector replaces the old dialog.

```
[ - ]   [  input field  ]   [ + ]
```

### Behavior

- The input always contains a positive integer
- Clicking **+** increments the value
- Clicking **–** decrements the value (minimum = 1)
- The user may type a number manually
- When a report is generated:
  - The current line is saved to `config.last_line_number`
  - On next launch, the GUI initializes the line to:

```
last_line_number + 1
```

If no previous value exists:
- The default is `1`

---

# 5. GUI Workflow With Mapping Persistence

## 5.1 On Application Start

1. Load `config` table
2. If `last_excel_path` exists → display it
3. If `last_docx_path` exists → display it
4. If `last_mapping_path` exists → display it
5. If `last_line_number` exists:
   - Set input to `last_line_number + 1`
6. Otherwise:
   - Set input to `1`

---

## 5.2 When User Selects a Mapping File

- Open file dialog
- Save path to `config.last_mapping_path`
- Update label in GUI
- The selected mapping is used for the next report generation

---

## 5.3 When User Generates a Report

1. Read current line number
2. Save it to `config.last_line_number`
3. Save Excel path, template path, mapping path
4. Generate the report using:
   - Excel file
   - Template file
   - Selected mapping.json
5. Save full report metadata to the `reports` table
6. Update line selector to:

```
last_line_number + 1
```

---

# 6. Example of Config Table Content

```
key                 | value
--------------------|-----------------------------------------------
last_excel_path     | S:/DEV/data/animals.xlsx
last_docx_path      | S:/DEV/templates/inspection.docx
last_mapping_path   | S:/DEV/mappings/inspection.json
last_line_number    | 12
```

On next launch:
- Excel path is restored
- Template path is restored
- Mapping path is restored
- Line selector shows `13`

---

# 7. Summary

- The GUI now supports selecting a mapping/configuration file
- The last mapping is saved in SQLite and restored automatically
- The line selector uses + / – buttons and auto-increments
- Excel, template, mapping, and line are all persisted
- The system supports multiple report types and templates

