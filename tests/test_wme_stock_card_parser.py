"""Tests for the WME stock card parser only."""

from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from app.parsers.errors import EmptyWorkbookError, InvalidWorkbookFormatError, UnsupportedFileTypeError
from app.parsers.wme_stock_card import parse_wme_stock_card_dataframe, parse_wme_stock_card_excel


def _movement_row(document_type: str = "BC") -> list[object]:
    row: list[object] = [None] * 15
    row[1] = document_type
    row[2] = "00012345"
    row[3] = "02.06.2026"
    row[4] = "2,50"
    row[5] = "5,75"
    row[6] = "12,00"
    row[9] = "Anonymized partner"
    row[10] = "Anonymized product"
    row[12] = "SKU-001"
    row[13] = "Depozit Principal"
    row[14] = "kg"
    return row


def _valid_wme_stock_card_dataframe() -> pd.DataFrame:
    return pd.DataFrame([
        ["Header"] + [None] * 14,
        _movement_row(),
    ])


def test_parse_wme_stock_card_dataframe_maps_positional_event_fields() -> None:
    events = parse_wme_stock_card_dataframe(_valid_wme_stock_card_dataframe())

    assert len(events) == 1
    event = events[0]
    assert event.document_type == "BC"
    assert event.document_number == "00012345"
    assert event.normalized_document == "BC 12345"
    assert event.event_date == date(2026, 6, 2)
    assert event.in_quantity == Decimal("2.50")
    assert event.out_quantity == Decimal("5.75")
    assert event.net_quantity == Decimal("-3.25")
    assert event.stock_after == Decimal("12.00")
    assert event.partner == "Anonymized partner"
    assert event.product_name == "Anonymized product"
    assert event.internal_product_code == "SKU-001"
    assert event.warehouse == "Depozit Principal"
    assert event.unit == "kg"


def test_parse_wme_stock_card_dataframe_accepts_valid_document_types() -> None:
    dataframe = pd.DataFrame([_movement_row(document_type) for document_type in ["StocInitial", "AE", "BC", "NT", "NP", "PV", "F", "FE"]])

    events = parse_wme_stock_card_dataframe(dataframe)

    assert [event.document_type for event in events] == ["StocInitial", "AE", "BC", "NT", "NP", "PV", "F", "FE"]


def test_parse_wme_stock_card_dataframe_skips_headers_and_unsupported_rows() -> None:
    dataframe = pd.DataFrame([
        ["Header"] + [None] * 14,
        _movement_row("BC"),
        _movement_row("UNSUPPORTED"),
    ])

    events = parse_wme_stock_card_dataframe(dataframe)

    assert len(events) == 1
    assert events[0].document_type == "BC"


def test_parse_wme_stock_card_dataframe_rejects_short_layout() -> None:
    dataframe = pd.DataFrame([[None] * 14])

    with pytest.raises(InvalidWorkbookFormatError, match="15 columns"):
        parse_wme_stock_card_dataframe(dataframe)


def test_parse_wme_stock_card_dataframe_rejects_missing_document_number() -> None:
    row = _movement_row()
    row[2] = ""
    dataframe = pd.DataFrame([row])

    with pytest.raises(InvalidWorkbookFormatError, match="document number"):
        parse_wme_stock_card_dataframe(dataframe)


def test_parse_wme_stock_card_dataframe_rejects_invalid_quantity() -> None:
    row = _movement_row()
    row[4] = "not-a-number"
    dataframe = pd.DataFrame([row])

    with pytest.raises(InvalidWorkbookFormatError, match="in quantity"):
        parse_wme_stock_card_dataframe(dataframe)


def test_parse_wme_stock_card_dataframe_rejects_invalid_date() -> None:
    row = _movement_row()
    row[3] = "not-a-date"
    dataframe = pd.DataFrame([row])

    with pytest.raises(InvalidWorkbookFormatError, match="date"):
        parse_wme_stock_card_dataframe(dataframe)


def test_parse_wme_stock_card_dataframe_rejects_empty_data() -> None:
    dataframe = pd.DataFrame(columns=range(15))

    with pytest.raises(EmptyWorkbookError):
        parse_wme_stock_card_dataframe(dataframe)


def test_parse_wme_stock_card_excel_reads_single_sheet_workbook(tmp_path) -> None:
    workbook_path = tmp_path / "wme_stock_card.xlsx"
    _valid_wme_stock_card_dataframe().to_excel(workbook_path, index=False, header=False)

    events = parse_wme_stock_card_excel(workbook_path)

    assert len(events) == 1
    assert events[0].document_type == "BC"


def test_parse_wme_stock_card_excel_requires_sheet_name_for_multiple_sheets(tmp_path) -> None:
    workbook_path = tmp_path / "wme_stock_card.xlsx"
    with pd.ExcelWriter(workbook_path) as writer:
        _valid_wme_stock_card_dataframe().to_excel(writer, index=False, header=False, sheet_name="A")
        _valid_wme_stock_card_dataframe().to_excel(writer, index=False, header=False, sheet_name="B")

    with pytest.raises(InvalidWorkbookFormatError, match="Multiple sheets"):
        parse_wme_stock_card_excel(workbook_path)

    events = parse_wme_stock_card_excel(workbook_path, sheet_name="B")
    assert len(events) == 1


def test_parse_wme_stock_card_excel_rejects_unsupported_file_type(tmp_path) -> None:
    csv_path = tmp_path / "wme_stock_card.csv"
    csv_path.write_text("not,xlsx\n", encoding="utf-8")

    with pytest.raises(UnsupportedFileTypeError):
        parse_wme_stock_card_excel(csv_path)
