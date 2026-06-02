"""Tests for the WMS traceability parser only."""

from datetime import datetime
from decimal import Decimal

import pandas as pd
import pytest

from app.parsers.errors import (
    EmptyWorkbookError,
    InvalidWorkbookFormatError,
    MissingRequiredColumnError,
    UnsupportedFileTypeError,
)
from app.parsers.wms_traceability import (
    parse_wms_traceability_dataframe,
    parse_wms_traceability_excel,
)


def _valid_wms_traceability_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Data": "02.06.2026 10:30",
                "Tip operatiune": "Mutare",
                "Numar comanda": "CMD-001",
                "Cod articol": "SKU-001",
                "Denumire articol": "Anonymized product",
                "Locatie sursa": "REC100",
                "Locatie destinatie": "RAFT-001",
                "Lot": "LOT-001",
                "Cantitate": "4,50",
                "Partener": "Anonymized partner",
                "Document comanda": "DOC-CMD-001",
                "Document intrare": "DOC-IN-001",
            }
        ]
    )


def test_parse_wms_traceability_dataframe_maps_event_fields() -> None:
    events = parse_wms_traceability_dataframe(_valid_wms_traceability_dataframe())

    assert len(events) == 1
    event = events[0]
    assert event.product_code == "SKU-001"
    assert event.product_name == "Anonymized product"
    assert event.event_datetime == datetime(2026, 6, 2, 10, 30)
    assert event.operation_type == "Mutare"
    assert event.document_number == "DOC-CMD-001"
    assert event.normalized_document == "DOC-CMD-001"
    assert event.source_location == "REC100"
    assert event.destination_location == "RAFT-001"
    assert event.lot == "LOT-001"
    assert event.quantity == Decimal("4.50")
    assert event.partner == "Anonymized partner"


def test_parse_wms_traceability_dataframe_falls_back_to_order_number() -> None:
    dataframe = _valid_wms_traceability_dataframe()
    dataframe.loc[0, "Document comanda"] = ""
    dataframe.loc[0, "Document intrare"] = ""

    events = parse_wms_traceability_dataframe(dataframe)

    assert events[0].document_number == "CMD-001"


def test_parse_wms_traceability_dataframe_requires_contract_columns() -> None:
    dataframe = _valid_wms_traceability_dataframe().drop(columns=["Cantitate"])

    with pytest.raises(MissingRequiredColumnError, match="Cantitate"):
        parse_wms_traceability_dataframe(dataframe)


def test_parse_wms_traceability_dataframe_rejects_invalid_quantity() -> None:
    dataframe = _valid_wms_traceability_dataframe()
    dataframe.loc[0, "Cantitate"] = "not-a-number"

    with pytest.raises(InvalidWorkbookFormatError, match="Cantitate"):
        parse_wms_traceability_dataframe(dataframe)


def test_parse_wms_traceability_dataframe_rejects_invalid_date() -> None:
    dataframe = _valid_wms_traceability_dataframe()
    dataframe.loc[0, "Data"] = "not-a-date"

    with pytest.raises(InvalidWorkbookFormatError, match="Data"):
        parse_wms_traceability_dataframe(dataframe)


def test_parse_wms_traceability_dataframe_rejects_empty_data() -> None:
    dataframe = pd.DataFrame(columns=_valid_wms_traceability_dataframe().columns)

    with pytest.raises(EmptyWorkbookError):
        parse_wms_traceability_dataframe(dataframe)


def test_parse_wms_traceability_excel_reads_single_sheet_workbook(tmp_path) -> None:
    workbook_path = tmp_path / "wms_traceability.xlsx"
    _valid_wms_traceability_dataframe().to_excel(workbook_path, index=False)

    events = parse_wms_traceability_excel(workbook_path)

    assert len(events) == 1
    assert events[0].product_code == "SKU-001"


def test_parse_wms_traceability_excel_requires_sheet_name_for_multiple_sheets(tmp_path) -> None:
    workbook_path = tmp_path / "wms_traceability.xlsx"
    with pd.ExcelWriter(workbook_path) as writer:
        _valid_wms_traceability_dataframe().to_excel(writer, index=False, sheet_name="A")
        _valid_wms_traceability_dataframe().to_excel(writer, index=False, sheet_name="B")

    with pytest.raises(InvalidWorkbookFormatError, match="Multiple sheets"):
        parse_wms_traceability_excel(workbook_path)

    events = parse_wms_traceability_excel(workbook_path, sheet_name="B")
    assert len(events) == 1


def test_parse_wms_traceability_excel_rejects_unsupported_file_type(tmp_path) -> None:
    csv_path = tmp_path / "wms_traceability.csv"
    csv_path.write_text("not,xlsx\n", encoding="utf-8")

    with pytest.raises(UnsupportedFileTypeError):
        parse_wms_traceability_excel(csv_path)
