from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd

from app.models import WmeEvent
from app.normalization import document_key_from_type_and_number
from app.parsers.errors import EmptyWorkbookError, InvalidWorkbookFormatError, UnsupportedFileTypeError

SUPPORTED_EXTENSIONS = {".xlsx", ".xls"}
VALID_DOCUMENT_TYPES = {"StocInitial", "AE", "BC", "NT", "NP", "PV", "F", "FE"}

COLUMN_DOCUMENT_TYPE = 1
COLUMN_DOCUMENT_NUMBER = 2
COLUMN_DATE = 3
COLUMN_IN_QUANTITY = 4
COLUMN_OUT_QUANTITY = 5
COLUMN_STOCK_AFTER = 6
COLUMN_PARTNER = 9
COLUMN_PRODUCT_NAME = 10
COLUMN_INTERNAL_PRODUCT_CODE = 12
COLUMN_WAREHOUSE = 13
COLUMN_UNIT = 14
MIN_COLUMNS = 15


def parse_wme_stock_card_excel(path: str | Path, *, sheet_name: str | int | None = None) -> list[WmeEvent]:
    workbook_path = Path(path)
    if workbook_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(f"Unsupported WME stock card file type: {workbook_path.suffix}")
    excel_file = pd.ExcelFile(workbook_path)
    if not excel_file.sheet_names:
        raise EmptyWorkbookError("Workbook does not contain any sheets")
    if sheet_name is None:
        if len(excel_file.sheet_names) != 1:
            raise InvalidWorkbookFormatError("Multiple sheets found; explicit sheet_name is required")
        sheet_name = excel_file.sheet_names[0]
    dataframe = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
    return parse_wme_stock_card_dataframe(dataframe)


def parse_wme_stock_card_dataframe(dataframe: pd.DataFrame) -> list[WmeEvent]:
    if dataframe.empty:
        raise EmptyWorkbookError("WME stock card has no data rows")
    if dataframe.shape[1] < MIN_COLUMNS:
        raise InvalidWorkbookFormatError("WME stock card positional layout requires at least 15 columns")
    events: list[WmeEvent] = []
    for _, raw_row in dataframe.iterrows():
        if _is_empty_row(raw_row):
            continue
        document_type = _optional_text(raw_row.iloc[COLUMN_DOCUMENT_TYPE])
        if document_type is None:
            continue
        if document_type not in VALID_DOCUMENT_TYPES:
            continue
        document_number = _required_text(raw_row.iloc[COLUMN_DOCUMENT_NUMBER], "document number")
        normalized_document = document_key_from_type_and_number(document_type, document_number)
        if normalized_document is None:
            raise InvalidWorkbookFormatError("Invalid document type or number")
        events.append(WmeEvent(
            product_name=_required_text(raw_row.iloc[COLUMN_PRODUCT_NAME], "product name"),
            internal_product_code=_required_text(raw_row.iloc[COLUMN_INTERNAL_PRODUCT_CODE], "internal product code"),
            document_type=document_type,
            document_number=document_number,
            normalized_document=normalized_document,
            event_date=_to_date(raw_row.iloc[COLUMN_DATE], "date"),
            in_quantity=_to_decimal_or_zero(raw_row.iloc[COLUMN_IN_QUANTITY], "in quantity"),
            out_quantity=_to_decimal_or_zero(raw_row.iloc[COLUMN_OUT_QUANTITY], "out quantity"),
            stock_after=_to_optional_decimal(raw_row.iloc[COLUMN_STOCK_AFTER], "stock after"),
            warehouse=_required_text(raw_row.iloc[COLUMN_WAREHOUSE], "warehouse"),
            unit=_optional_text(raw_row.iloc[COLUMN_UNIT]),
            partner=_optional_text(raw_row.iloc[COLUMN_PARTNER]),
            raw=dict(raw_row),
        ))
    if not events:
        raise EmptyWorkbookError("WME stock card has no valid movement rows")
    return events


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


def _to_decimal_or_zero(value: Any, field_name: str) -> Decimal:
    if pd.isna(value) or str(value).strip() == "":
        return Decimal("0")
    return _to_decimal(value, field_name)


def _to_optional_decimal(value: Any, field_name: str) -> Decimal | None:
    if pd.isna(value) or str(value).strip() == "":
        return None
    return _to_decimal(value, field_name)


def _to_decimal(value: Any, field_name: str) -> Decimal:
    text = str(value).strip().replace("\u00a0", "").replace(" ", "")
    if "," in text and "." not in text:
        text = text.replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise InvalidWorkbookFormatError(f"Invalid numeric value for {field_name}: {value!r}") from exc


def _to_date(value: Any, field_name: str) -> date:
    if pd.isna(value) or str(value).strip() == "":
        raise InvalidWorkbookFormatError(f"Missing date value for {field_name}")
    parsed = pd.to_datetime(value, errors="coerce", dayfirst=True)
    if pd.isna(parsed):
        raise InvalidWorkbookFormatError(f"Invalid date value for {field_name}: {value!r}")
    return parsed.date()
