import datetime


def op_today(rule, row_data):
    fmt = rule.get("format", "%Y-%m-%d")
    return datetime.date.today().strftime(fmt)


def op_uppercase(rule, row_data):
    field = rule.get("input")
    if field in row_data:
        return str(row_data[field]).upper()


def op_lowercase(rule, row_data):
    field = rule.get("input")
    if field in row_data:
        return str(row_data[field]).lower()


def op_format(rule, row_data):
    fmt = rule.get("format", "")
    try:
        return fmt.format(**row_data)
    except Exception:
        return ""


def op_concat(rule, row_data):
    parts = rule.get("parts", [])
    return "".join(str(row_data.get(p, "")) for p in parts)


# ── Lookup helpers ─────────────────────────────────────────────────────────────

def _find_row(excel_reader, sheet_name: str, key_column: str, key_value) -> dict | None:
    """Wrapper around ExcelReader.find_row with graceful error handling."""
    try:
        return excel_reader.find_row(sheet_name, key_column, key_value)
    except KeyError as e:
        raise LookupError(str(e))


def _normalize(value) -> str:
    return str(value).strip() if value is not None else ""


# ── op_lookup ─────────────────────────────────────────────────────────────────

def op_lookup(rule: dict, row_data: dict, excel_reader=None) -> str | None:
    """
    Simple single-sheet foreign-key lookup.

    rule keys:
      sheet  — sheet name to search in
      key    — column in the target sheet to match against
      match  — column in row_data that holds the foreign key value
      value  — column in the target sheet whose value to return
    """
    if excel_reader is None:
        return None

    sheet_name  = rule.get("sheet", "")
    key_column  = rule.get("key", "")
    match_field = rule.get("match", "")
    value_col   = rule.get("value", "")

    if not all([sheet_name, key_column, match_field, value_col]):
        return None

    foreign_key = row_data.get(match_field)
    if foreign_key is None:
        return None

    row = _find_row(excel_reader, sheet_name, key_column, foreign_key)
    if row is None:
        return None

    return _normalize(row.get(value_col))


# ── op_lookup_join ────────────────────────────────────────────────────────────

def op_lookup_join(rule: dict, row_data: dict, excel_reader=None) -> str | None:
    """
    Multi-step relational lookup (unlimited JOIN chain).

    rule keys:
      steps  — list of step dicts, each with:
                  sheet   sheet name to search in
                  key     column in the target sheet to match against
                  match   column in row_data (or "<previous>") with the FK value
                  value   column name or list of column names to return
      format — Python format string applied to the fields collected across all steps
               (uses the column names as keys, e.g. "{street}, {city}")

    "<previous>" in a step's match field uses the result returned by the previous step.
    When value is a list, all named columns are collected into the shared namespace
    and the last step's single-value result is also stored as "<previous>" for the
    next step (though multi-value steps are typically the last step).
    """
    if excel_reader is None:
        return None

    steps = rule.get("steps", [])
    fmt   = rule.get("format", "")

    if not steps:
        return None

    previous_value = None        # result carried between steps
    collected: dict[str, str] = {}  # all named fields gathered across steps

    for i, step in enumerate(steps):
        sheet_name  = step.get("sheet", "")
        key_column  = step.get("key", "")
        match_field = step.get("match", "")
        value_spec  = step.get("value")   # str or list[str]

        if not all([sheet_name, key_column, match_field, value_spec]):
            return None

        # Resolve the foreign key value
        if match_field == "<previous>":
            if previous_value is None:
                return None
            fk_value = previous_value
        else:
            fk_value = row_data.get(match_field)
            if fk_value is None:
                return None

        row = _find_row(excel_reader, sheet_name, key_column, fk_value)
        if row is None:
            return None

        # Collect requested columns
        if isinstance(value_spec, list):
            for col in value_spec:
                collected[col] = _normalize(row.get(col))
            # For chaining purposes, if there's a single-value next step it would
            # need an explicit match field — multi-value steps end the chain.
            previous_value = None
        else:
            # Single column — result becomes <previous> for the next step
            val = _normalize(row.get(value_spec))
            collected[value_spec] = val
            previous_value = val

    # Apply format string using all collected fields
    if fmt:
        try:
            return fmt.format(**collected)
        except KeyError as e:
            raise LookupError(
                f"lookup_join format references unknown field {e}. "
                f"Available: {list(collected.keys())}"
            )

    # No format string — return all collected values joined by ", "
    return ", ".join(v for v in collected.values() if v)