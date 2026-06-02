"""Tests for current and baseline stock report parsers only."""

from decimal import Decimal

import pandas as pd
import pytest

from app.models import SourceSystem
from app.parsers.errors import (
    EmptyWorkbookError,
    InvalidWorkbookFormatError,
    MissingRequiredColumnError,
    UnsupportedFileTypeError,
)
from app.parsers.stock_report import (
    parse_baseline_stock_report_dataframe,
    parse_baseline_stock_report_excel,
    parse_stock_report_dataframe,
    parse_stock_report_excel,
)


def _valid_stock_report_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "CodArticol": "SKU-001",
                "DenumireArticol": "Anonymized product",
                "QuantityERP": "10.00",
                "QuantityWMS": "7.00",
                "Rezervat": "99.00",
                "QuantityDifference": "-3.00",
                "Gestiune": "Depozitare",
            },
            {
                "CodArticol": "SKU-002",
                "DenumireArticol": "Second anonymized product",
                "QuantityERP": "1,50",
                "QuantityWMS": "2,75",
                "Rezervat": "0",
                "QuantityDifference": "1,25",
                "Gestiune": "Receptie",
            },
        ]
    )


def test_parse_stock_report_dataframe_maps_rows_and_preserves_formula() -> None:
    rows = parse_stock_report_dataframe(_valid_stock_report_dataframe())

    assert len(rows) == 2
    assert rows[0].product_code == "SKU-001"
    assert rows[0].product_name == "Anonymized product"
    assert rows[0].location == "Depozitare"
    assert rows[0].quantity_erp == Decimal("10.00")
    assert rows[0].quantity_wms == Decimal("7.00")
    assert rows[0].reserved == Decimal("99.00")
    assert rows[0].quantity_difference == Decimal("-3.00")
    assert rows[0].calculated_difference() == Decimal("-3.00")
    assert rows[0].source == SourceSystem.STOCK_REPORT

    assert rows[1].quantity_erp == Decimal("1.50")
    assert rows[1].quantity_wms == Decimal("2.75")
    assert rows[1].quantity_difference == Decimal("1.25")


def test_parse_baseline_stock_report_dataframe_marks_baseline_source() -> None:
    rows = parse_baseline_stock_report_dataframe(_valid_stock_report_dataframe())

    assert len(rows) == 2
    assert {row.source for row in rows} == {SourceSystem.BASELINE_REPORT}
    assert rows[0].calculated_difference() == Decimal("-3.00")


def test_parse_stock_report_dataframe_requires_all_contract_columns() -> None:
    dataframe = _valid_stock_report_dataframe().drop(columns=["QuantityWMS"])

    with pytest.raises(MissingRequiredColumnError, match="QuantityWMS"):
        parse_stock_report_dataframe(dataframe)


def test_parse_stock_report_dataframe_rejects_inconsistent_difference() -> None:
    dataframe = _valid_stock_report_dataframe()
    dataframe.loc[0, "QuantityDifference"] = "-2.00"

    with pytest.raises(InvalidWorkbookFormatError, match="QuantityDifference"):
        parse_stock_report_dataframe(dataframe)


def test_parse_stock_report_dataframe_rejects_invalid_numeric_value() -> None:
    dataframe = _valid_stock_report_dataframe()
    dataframe.loc[0, "QuantityERP"] = "not-a-number"

    with pytest.raises(InvalidWorkbookFormatError, match="QuantityERP"):
        parse_stock_report_dataframe(dataframe)


def test_parse_stock_report_dataframe_rejects_empty_data() -> None:
    dataframe = pd.DataFrame(
        columns=[
            "CodArticol",
            "DenumireArticol",
            "QuantityERP",
            "QuantityWMS",
            "Rezervat",
            "QuantityDifference",
            "Gestiune",
        ]
    )

    with pytest.raises(EmptyWorkbookError):
        parse_stock_report_dataframe(dataframe)


def test_parse_stock_report_excel_reads_single_sheet_workbook(tmp_path) -> None:
    workbook_path = tmp_path / "stock_report.xlsx"
    _valid_stock_report_dataframe().to_excel(workbook_path, index=False)

    rows = parse_stock_report_excel(workbook_path)

    assert len(rows) == 2
    assert rows[0].product_code == "SKU-001"


def test_parse_baseline_stock_report_excel_reads_baseline_source(tmp_path) -> None:
    workbook_path = tmp_path / "baseline_stock_report.xlsx"
    _valid_stock_report_dataframe().to_excel(workbook_path, index=False)

    rows = parse_baseline_stock_report_excel(workbook_path)

    assert len(rows) == 2
    assert rows[0].source == SourceSystem.BASELINE_REPORT


def test_parse_stock_report_excel_requires_sheet_name_for_multiple_sheets(tmp_path) -> None:
    workbook_path = tmp_path / "stock_report.xlsx"
    with pd.ExcelWriter(workbook_path) as writer:
        _valid_stock_report_dataframe().to_excel(writer, index=False, sheet_name="A")
        _valid_stock_report_dataframe().to_excel(writer, index=False, sheet_name="B")

    with pytest.raises(InvalidWorkbookFormatError, match="Multiple sheets"):
        parse_stock_report_excel(workbook_path)

    rows = parse_stock_report_excel(workbook_path, sheet_name="B")
    assert len(rows) == 2


def test_parse_baseline_stock_report_excel_accepts_explicit_sheet_name(tmp_path) -> None:
    workbook_path = tmp_path / "baseline_stock_report.xlsx"
    with pd.ExcelWriter(workbook_path) as writer:
        _valid_stock_report_dataframe().to_excel(writer, index=False, sheet_name="A")
        _valid_stock_report_dataframe().to_excel(writer, index=False, sheet_name="B")

    rows = parse_baseline_stock_report_excel(workbook_path, sheet_name="B")

    assert len(rows) == 2
    assert rows[0].source == SourceSystem.BASELINE_REPORT


def test_parse_stock_report_excel_rejects_unsupported_file_type(tmp_path) -> None:
    csv_path = tmp_path / "stock_report.csv"
    csv_path.write_text("not,xlsx\n", encoding="utf-8")

    with pytest.raises(UnsupportedFileTypeError):
        parse_stock_report_excel(csv_path)
