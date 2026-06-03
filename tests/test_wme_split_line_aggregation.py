"""Tests for WME split-line aggregation utility only."""

from datetime import date
from decimal import Decimal

from app.aggregation import aggregate_wme_split_lines
from app.models import WmeEvent


def _event(product_code="SKU-001", normalized_document="BC 12345", document_type="BC", in_quantity="0", out_quantity="0"):
    return WmeEvent(
        product_name="Anonymized product",
        internal_product_code=product_code,
        document_type=document_type,
        document_number="00012345",
        normalized_document=normalized_document,
        event_date=date(2026, 6, 2),
        in_quantity=Decimal(in_quantity),
        out_quantity=Decimal(out_quantity),
        stock_after=Decimal("10.00"),
        warehouse="Depozit Principal",
        unit="kg",
        partner="Anonymized partner",
    )


def test_aggregate_wme_split_lines_groups_by_product_document_and_type():
    aggregated = aggregate_wme_split_lines([
        _event(out_quantity="2.50"),
        _event(out_quantity="3.25"),
        _event(product_code="SKU-002", out_quantity="1.00"),
    ])

    assert len(aggregated) == 2
    first = aggregated[0]
    assert first.product_code == "SKU-001"
    assert first.normalized_document == "BC 12345"
    assert first.document_type == "BC"
    assert first.out_quantity == Decimal("5.75")
    assert first.net_quantity == Decimal("-5.75")
    assert first.source_row_count == 2
    assert len(first.source_events) == 2


def test_aggregate_wme_split_lines_separates_document_types():
    aggregated = aggregate_wme_split_lines([
        _event(document_type="BC", normalized_document="BC 12345", out_quantity="1.00"),
        _event(document_type="AE", normalized_document="AE 12345", in_quantity="1.00"),
    ])

    assert len(aggregated) == 2
    assert {item.document_type for item in aggregated} == {"AE", "BC"}


def test_aggregate_wme_split_lines_preserves_evidence_events():
    event = _event(out_quantity="1.00")
    aggregated = aggregate_wme_split_lines([event])

    assert aggregated[0].source_events == (event,)
    assert aggregated[0].source_row_count == 1


def test_aggregate_wme_split_lines_returns_empty_list_for_empty_input():
    assert aggregate_wme_split_lines([]) == []
