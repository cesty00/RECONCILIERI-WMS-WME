from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd

from app.models import SourceSystem, StockSnapshotRow
from app.parsers.errors import (
    EmptyWorkbookError,
    InvalidWorkbookFormatError,
    MissingRequiredColumnError,
    UnsupportedFileTypeError,
)

REQUIRED_COLUMNS: dict[str, str] = {
    "codarticol": "CodArticol",
    "denumirearticol": "DenumireArticol",
    "quantityerp": "QuantityERP",
    "quantitywms": "QuantityWMS",
    "rezervat": "Rezervat",
    "quantitydifference": "QuantityDifference",
    "gestiune": "Gestiune",
}

QUANTITY_COLUMNS = {
    "quantityerp",
    "quantitywms",
    "rezervat",
    "quantitydifference",
}

SUPPORTED_EXTENSIONS = {".xlsx", ".xls"}


def parse_stock_report_excel(
    path: str | Path,
    *,
    sheet_name: str | int | None = None,
    source: SourceSystem = SourceSystem.STOCK_REPORT,
) -> list[StockSnapshotRow]:
    """Parse a current WMS/WME stock report workbook."""
    workbook_path = Path(path)
    if workbook_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(f"Unsupported stock report file type: {workbook_path.suffix}")

    excel_file = pd.ExcelFile(workbook_path)
    if not excel_file.sheet_names:
        raise EmptyWorkbookError("Workbook does not contain any sheets")

    selected_sheet: str | int
    if sheet_name is None:
        if len(excel_file.sheet_names) != 1:
            raise InvalidWorkbookFormatError(
                "Multiple sheets found; explicit sheet_name is required"
            )
        selected_sheet = excel_file.sheet_names[0]
    else:
        selected_sheet = sheet_name

    dataframe = pd.read_excel(excel_file, sheet_name=selected_sheet)
    return parse_stock_report_dataframe(dataframe, source=source)


def parse_stock_report_dataframe(
    dataframe: pd.DataFrame,
    *,
    source: SourceSystem = SourceSystem.STOCK_REPORT,
) -> list[StockSnapshotRow]:
    """Parse stock report rows from a DataFrame using the documented contract."""
    if dataframe.empty:
        raise EmptyWorkbookError("Stock report has no data rows")

    column_map = _resolve_columns(dataframe.columns)
    rows: list[StockSnapshotRow] = []

    for _, raw_row in dataframe.iterrows():
        if _is_empty_row(raw_row):
            continue

        quantity_erp = _to_decimal(raw_row[column_map["quantityerp"]], "QuantityERP")
        quantity_wms = _to_decimal(raw_row[column_map["quantitywms"]], "QuantityWMS")
        reserved = _to_decimal(raw_row[column_map["rezervat"]], "Rezervat")
        quantity_difference = _to_decimal(
            raw_row[column_map["quantitydifference"]],
            "QuantityDifference",
        )

        stock_row = StockSnapshotRow(
            product_code=_to_text(raw_row[column_map["codarticol"]], "CodArticol"),
            product_name=_to_text(
                raw_row[column_map["denumirearticol"]],
                "DenumireArticol",
            ),
            location=_to_text(raw_row[column_map["gestiune"]], "Gestiune"),
            quantity_erp=quantity_erp,
            quantity_wms=quantity_wms,
            reserved=reserved,
            quantity_difference=quantity_difference,
            source=source,
            raw=dict(raw_row),
        )

        if not stock_row.difference_matches_reported():
            raise InvalidWorkbookFormatError(
                "QuantityDifference is inconsistent with QuantityWMS - QuantityERP"
            )

        rows.append(stock_row)

    if not rows:
        raise EmptyWorkbookError("Stock report has no valid data rows")

    return rows


def parse_baseline_stock_report_excel(
    path: str | Path,
    *,
    sheet_name: str | int | None = None,
) -> list[StockSnapshotRow]:
    """Parse the baseline stock report after WME consumption documents."""
    return parse_stock_report_excel(
        path,
        sheet_name=sheet_name,
        source=SourceSystem.BASELINE_REPORT,
    )


def parse_baseline_stock_report_dataframe(
    dataframe: pd.DataFrame,
) -> list[StockSnapshotRow]:
    """Parse baseline stock report rows using the stock report column contract."""
    return parse_stock_report_dataframe(
        dataframe,
        source=SourceSystem.BASELINE_REPORT,
    )


def _resolve_columns(columns: Any) -> dict[str, str]:
    resolved: dict[str, str] = {}
    seen: dict[str, str] = {}

    for column in columns:
        normalized = _normalize_column_name(column)
        if normalized in seen:
            raise InvalidWorkbookFormatError(
                f"Duplicate column after normalization: {column!r} and {seen[normalized]!r}"
            )
        seen[normalized] = str(column)
        if normalized in REQUIRED_COLUMNS:
            resolved[normalized] = column

    missing = [display for key, display in REQUIRED_COLUMNS.items() if key not in resolved]
    if missing:
        raise MissingRequiredColumnError(
            "Missing required stock report columns: " + ", ".join(missing)
        )

    return resolved


def _normalize_column_name(value: Any) -> str:
    return "".join(str(value).strip().lower().split())


def _is_empty_row(row: pd.Series) -> bool:
    return all(pd.isna(value) or str(value).strip() == "" for value in row)


def _to_text(value: Any, field_name: str) -> str:
    if pd.isna(value) or str(value).strip() == "":
        raise InvalidWorkbookFormatError(f"Missing required value for {field_name}")
    return str(value).strip()


def _to_decimal(value: Any, field_name: str) -> Decimal:
    if pd.isna(value) or str(value).strip() == "":
        raise InvalidWorkbookFormatError(f"Missing numeric value for {field_name}")

    text = str(value).strip().replace("\u00a0", "").replace(" ", "")
    if "," in text and "." not in text:
        text = text.replace(",", ".")

    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise InvalidWorkbookFormatError(
            f"Invalid numeric value for {field_name}: {value!r}"
        ) from exc
