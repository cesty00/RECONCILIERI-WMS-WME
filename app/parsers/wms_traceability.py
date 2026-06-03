from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd

from app.models import WmsEvent
from app.normalization import canonical_document
from app.parsers.errors import EmptyWorkbookError, InvalidWorkbookFormatError, MissingRequiredColumnError, UnsupportedFileTypeError

REQUIRED_COLUMNS: dict[str, str] = {
    "data": "Data",
    "tipoperatiune": "Tip operatiune",
    "numarcomanda": "Numar comanda",
    "codarticol": "Cod articol",
    "denumirearticol": "Denumire articol",
    "locatiesursa": "Locatie sursa",
    "locatiedestinatie": "Locatie destinatie",
    "lot": "Lot",
    "cantitate": "Cantitate",
    "partener": "Partener",
}
OPTIONAL_DOCUMENT_COLUMNS: dict[str, str] = {
    "documentcomanda": "Document comanda",
    "documentintrare": "Document intrare",
}
SUPPORTED_EXTENSIONS = {".xlsx", ".xls"}


def parse_wms_traceability_excel(path: str | Path, *, sheet_name: str | int | None = None) -> list[WmsEvent]:
    workbook_path = Path(path)
    if workbook_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(f"Unsupported WMS traceability file type: {workbook_path.suffix}")
    excel_file = pd.ExcelFile(workbook_path)
    if not excel_file.sheet_names:
        raise EmptyWorkbookError("Workbook does not contain any sheets")
    if sheet_name is None:
        if len(excel_file.sheet_names) != 1:
            raise InvalidWorkbookFormatError("Multiple sheets found; explicit sheet_name is required")
        sheet_name = excel_file.sheet_names[0]
    return parse_wms_traceability_dataframe(pd.read_excel(excel_file, sheet_name=sheet_name))


def parse_wms_traceability_dataframe(dataframe: pd.DataFrame) -> list[WmsEvent]:
    if dataframe.empty:
        raise EmptyWorkbookError("WMS traceability has no data rows")
    column_map = _resolve_columns(dataframe.columns)
    events: list[WmsEvent] = []
    for _, raw_row in dataframe.iterrows():
        if _is_empty_row(raw_row):
            continue
        document_number = _first_text(raw_row, column_map, ["documentcomanda", "documentintrare", "numarcomanda"])
        if document_number is None:
            raise InvalidWorkbookFormatError("Missing document or order reference")
        normalized_document = canonical_document(document_number) or document_number
        events.append(WmsEvent(
            product_code=_required_text(raw_row[column_map["codarticol"]], "Cod articol"),
            product_name=_required_text(raw_row[column_map["denumirearticol"]], "Denumire articol"),
            event_datetime=_to_datetime(raw_row[column_map["data"]], "Data"),
            operation_type=_required_text(raw_row[column_map["tipoperatiune"]], "Tip operatiune"),
            document_number=document_number,
            normalized_document=normalized_document,
            source_location=_optional_text(raw_row[column_map["locatiesursa"]]),
            destination_location=_optional_text(raw_row[column_map["locatiedestinatie"]]),
            lot=_optional_text(raw_row[column_map["lot"]]),
            quantity=_to_decimal(raw_row[column_map["cantitate"]], "Cantitate"),
            partner=_optional_text(raw_row[column_map["partener"]]),
            raw=dict(raw_row),
        ))
    if not events:
        raise EmptyWorkbookError("WMS traceability has no valid data rows")
    return events


def _resolve_columns(columns: Any) -> dict[str, str]:
    resolved: dict[str, str] = {}
    seen: dict[str, str] = {}
    for column in columns:
        normalized = _normalize_column_name(column)
        if normalized in seen:
            raise InvalidWorkbookFormatError(f"Duplicate column after normalization: {column!r}")
        seen[normalized] = str(column)
        if normalized in REQUIRED_COLUMNS or normalized in OPTIONAL_DOCUMENT_COLUMNS:
            resolved[normalized] = column
    missing = [display for key, display in REQUIRED_COLUMNS.items() if key not in resolved]
    if missing:
        raise MissingRequiredColumnError("Missing required WMS traceability columns: " + ", ".join(missing))
    return resolved


def _normalize_column_name(value: Any) -> str:
    return "".join(str(value).strip().lower().split())


def _is_empty_row(row: pd.Series) -> bool:
    return all(pd.isna(value) or str(value).strip() == "" for value in row)


def _required_text(value: Any, field_name: str) -> str:
    text = _optional_text(value)
    if text is None:
        raise InvalidWorkbookFormatError(f"Missing required value for {field_name}")
    return text


def _optional_text(value: Any) -> str | None:
    if pd.isna(value) or str(value).strip() == "":
        return None
    return str(value).strip()


def _first_text(row: pd.Series, column_map: dict[str, str], keys: list[str]) -> str | None:
    for key in keys:
        column = column_map.get(key)
        if column is not None:
            value = _optional_text(row[column])
            if value is not None:
                return value
    return None


def _to_decimal(value: Any, field_name: str) -> Decimal:
    if pd.isna(value) or str(value).strip() == "":
        raise InvalidWorkbookFormatError(f"Missing numeric value for {field_name}")
    text = str(value).strip().replace("\u00a0", "").replace(" ", "")
    if "," in text and "." not in text:
        text = text.replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise InvalidWorkbookFormatError(f"Invalid numeric value for {field_name}: {value!r}") from exc


def _to_datetime(value: Any, field_name: str):
    if pd.isna(value) or str(value).strip() == "":
        raise InvalidWorkbookFormatError(f"Missing date/time value for {field_name}")
    parsed = pd.to_datetime(value, errors="coerce", dayfirst=True)
    if pd.isna(parsed):
        raise InvalidWorkbookFormatError(f"Invalid date/time value for {field_name}: {value!r}")
    return parsed.to_pydatetime()
