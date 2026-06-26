# Plan.md — Python GUI Report Generator

## 1. Project Overview
This application allows the user to:

- Select an Excel (.xlsx) data file  
- Select a Word (.docx) template containing placeholders  
- Optionally load a mapping file defining correspondences between Excel columns and Word placeholders  
- Validate that all required fields exist  
- Select a row from Excel  
- Generate a Word report populated with the selected row’s data  

The app is GUI‑based and modular.

---

## 2. High‑Level Architecture

### Modules
- GUI Module  
- Excel Reader Module  
- Word Template Module  
- Mapping Manager Module  
- Validation Module  
- Report Generator Module  

---

## 3. Folder Structure

```
report_generator/
│
├── gui/
│   ├── main_window.py
│   ├── file_dialogs.py
│   └── mapping_editor.py
│
├── core/
│   ├── excel_reader.py
│   ├── word_processor.py
│   ├── mapping_manager.py
│   ├── validator.py
│   └── report_generator.py
│
├── data/
│   └── correspondence.json
│
├── assets/
│   └── icons/
│
└── app.py
```

---

## 4. Detailed Module Responsibilities

### 4.1 GUI Module
- Select Excel file  
- Select Word template  
- Optional: select mapping file  
- Display extracted Excel columns  
- Display extracted Word placeholders  
- Show validation results  
- Ask for Excel row number  
- Ask where to save the generated report  
- Display success/error messages  

### 4.2 Excel Reader Module
- Load .xlsx file  
- Extract column names  
- Read a specific row  
- Check if row is empty  
- Return row as a dictionary  

### 4.3 Word Template Module
- Load .docx template  
- Extract placeholders {{...}}  
- Replace placeholders with values  
- Save final .docx file  

### 4.4 Mapping Manager Module
- Load mapping JSON if it exists  
- Save mapping JSON  
- Provide mapping dictionary  
- Detect missing or extra fields  

Example mapping file:

```json
{
  "date": "{{date}}",
  "species": "{{species}}",
  "address": "{{address}}",
  "inspector": "{{inspector}}",
  "notes": "{{notes}}"
}
```

### 4.5 Validation Module
- Check mapping ↔ Excel columns  
- Check mapping ↔ Word placeholders  
- Detect missing fields  
- Detect extra fields  
- Check if selected Excel row is empty  

### 4.6 Report Generator Module
- Receive Excel row data, Word template, and mapping  
- Replace placeholders  
- Ask user for output location  
- Save .docx file  

---

## 5. Application Workflow

### Step 1 — User opens the app
GUI loads with empty state.

### Step 2 — User selects Excel file
- Load file  
- Extract column names  
- Display them  

### Step 3 — User selects Word template
- Load template  
- Extract placeholders  
- Display them  

### Step 4 — Load or skip mapping file
- If correspondence.json exists → load  
- If not → skip (v1)  

### Step 5 — Validate
- Mapping ↔ Excel columns  
- Mapping ↔ Word placeholders  
- Missing fields  
- Extra fields  

### Step 6 — Ask for Excel row number
- Read row  
- Check if empty  
- Convert to dictionary  

### Step 7 — Generate report
- Replace placeholders  
- Ask user where to save  
- Save .docx  

### Step 8 — Confirmation
Show success message.

---

## 6. Future Features (v2+)
- Mapping editor GUI  
- Batch generation for all rows  
- PDF export  
- Template preview  
- Excel row search  
- Auto‑detect placeholders  
- Auto‑detect mapping suggestions  

---

## 7. Notes
- The app must remain modular  
- Mapping file is optional in v1  
- Validation must be strict  
- GUI must guide the user step‑by‑step  
