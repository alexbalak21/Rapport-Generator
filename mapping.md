# Spreadsheet mapping for Report Generator

This file shows how the current `new_rapport_mapping.json` maps spreadsheet columns to report placeholders and operations.

| Spreadsheet Column | JSON Key | Placeholder | Operations / Type | Notes |
|---|---|---|---|---|
| date rapport | date rapport | {{date_rapport}} | date (input) | Matches `date rapport` column in data file |
| appellation produit | appellation produit | {{appellation_produit}} | text (input) | |
| nom entreprise client | nom entreprise client | {{nom_entreprise_client}} | text (input) | |
| adresse entreprise client | adresse entreprise client | {{adresse_entreprise_client}} | text (input) | |
| nom destinataire | nom destinataire | {{nom_destinataire}} | text (input) | |
| titre poste destinataire | titre poste destinataire | {{titre_poste_destinataire}} | text (input) | |
| Lieu de prelevment | Lieu de prelevment | {{Lieu_de_prelevment}} | text (input) | |
| date heure prelevment | date heure prelevment | {{date_heure_prelevment}} | datetime (input) | |
| adresse prelevement | adresse prelevement | {{adresse_prelevement}} | text (input) | |
| ville prelevement | ville prelevment | {{ville_prelevement}} | text (input) | |
| conditions coservation reception | conditions coservation reception | {{conditions_coservation_reception}} | text (input) | |
| date heure arrive labo | date heure arrive labo | {{date_heure_arrive_labo}} | datetime (input) | |
| temperature reception | temperature reception | {{temperature_reception}} | numeric/text (input) | |
| date heure mise en analyse | date heure mise en analyse | {{date_heure_mise_en_analyse}} | datetime (input) | |
| fournisseur fabricant | fournisseur fabricant | {{fournisseur_fabricant}} | text (input) | |
| nom produit | nom produit | {{nom_produit}} | text (input) | |
| conditionnement | conditionnement | {{conditionnement}} | text (input) | |
| espece | espece | {{espece}} | text (input) | |
| agrement | agrement | {{agrement}} | text (input) | |
| origine | origine | {{origine}} | text (input) | |
| lot | lot | {{lot}} | text (input) | |
| date emabalage | date emabalage | {{date_emabalage}} | date_format %d/%m/%Y | Convert from Excel date or text to target format |
| code article | code article | {{code_article}} | text (input) | |
| dlc | dlc | {{dlc}} | date_format %d/%m/%Y | Convert from Excel date or text to target format |
| lot precice | lot precice | {{lot_precice}} | text (input) | |
| imp | imp | {{imp}} | formula → *100 → round(0) → suffix "%" | Calculated value; source may be numeric or formula in sheet |
| k value | k value | {{k_value}} | formula → *100 → round(0) → suffix "%" | Calculated value |
| conformite | conformite | {{conformite}} | text (input) | |
| qualite | qualite | {{qualite}} | text (input) | |
| numero echantillon | numero echantillon | {{n_ech}} | text/number (input) | Used as sample identifier |
| (computed) date_du_jour | date_du_jour | {{date_du_jour}} | operation: today (format %d/%m/%Y) | Not an input column — generated at runtime |
| (computed) numero_rapport | numero_rapport | (no placeholder) | operation: excel_day_counter (depends on `date rapport` and `numero echantillon`) | Generated filename component/counter |
| (computed) file_name | file_name | (no column) | operation: format("{name} {numero_rapport}.docx") | Final filename template — not stored in sheet |

Notes:
- The sheet should include headers that exactly match the **Spreadsheet Column** values above.
- Fields marked "computed" are produced by the generator (no input column required).
- For date fields prefer ISO or Excel-native dates; the generator can apply `date_format`.

Recommendation: which spreadsheet format to use

- XLSX (recommended): supports typed cells (dates, numbers), formatting, and multi-sheet workbooks. Good for users who edit data in Excel and for preserving date types and formulas.
- CSV: simple and portable; use when users only need raw text/number rows. Loses type information (dates become text) and cannot store formulas or multiple sheets.
- XML: structured and verbose; useful if you need strict schema validation or interop with XML workflows, but less user-friendly for manual editing.

For this project `XLSX` is the best choice because the mapping contains dates, numeric operations and (possible) formulas; XLSX preserves types and is easy for users to edit in Excel. Use CSV only for simple, flat exports or automation pipelines where Excel features are not needed.

If you want, I can:
- generate a sample `mapping.csv` with headers matching the table,
- or create a small `mapping_example.xlsx` with a few example rows (keeps dates and formulas).

Files referenced: `new_rapport_mapping.json` and this `mapping.md`.
