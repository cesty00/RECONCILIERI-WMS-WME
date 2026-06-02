"""Tests for the existing model layer only."""

from datetime import date, datetime
from decimal import Decimal

from app.models import (
    MovementDirection,
    ReconciliationStatus,
    SourceSystem,
    StockSnapshotRow,
    WmeEvent,
    WmsEvent,
)


def test_reconciliation_status_values_include_required_statuses() -> None:
    assert {status.value for status in ReconciliationStatus} == {
        "MATCH",
        "MATCH_DUPA_AGREGARE",
        "MATCH_DUPA_NETARE",
        "WMS_ONLY",
        "WME_ONLY",
        "TIMING_RISK",
        "LOCATION_ONLY",
        "STATUS_ONLY",
        "ROUNDING_DIFF",
        "REVIEW_REQUIRED",
        "NOT_RECONCILED",
    }


def test_stock_snapshot_difference_uses_wms_minus_erp_without_reserved() -> None:
    row = StockSnapshotRow(
        product_code="SKU-001",
        product_name="Anonymized product",
        location="Depozit Principal",
        quantity_erp=Decimal("10.00"),
        quantity_wms=Decimal("7.00"),
        reserved=Decimal("99.00"),
        quantity_difference=Decimal("-3.00"),
        source=SourceSystem.STOCK_REPORT,
    )

    assert row.calculated_difference() == Decimal("-3.00")
    assert row.difference_matches_reported()


def test_stock_snapshot_difference_tolerance_handles_small_decimal_drift() -> None:
    row = StockSnapshotRow(
        product_code="SKU-002",
        product_name="Anonymized product",
        location="Depozit Principal",
        quantity_erp=Decimal("1.00"),
        quantity_wms=Decimal("1.01"),
        reserved=Decimal("0.00"),
        quantity_difference=Decimal("0.01001"),
        source=SourceSystem.STOCK_REPORT,
    )

    assert row.difference_matches_reported()
    assert not row.difference_matches_reported(tolerance=Decimal("0.000001"))


def test_wme_event_net_quantity_is_in_minus_out() -> None:
    event = WmeEvent(
        product_name="Anonymized product",
        internal_product_code="SKU-003",
        document_type="BON_CONSUM",
        document_number="DOC-001",
        normalized_document="DOC-001",
        event_date=date(2026, 6, 2),
        in_quantity=Decimal("2.50"),
        out_quantity=Decimal("5.75"),
        stock_after=Decimal("12.00"),
        warehouse="Depozit Principal",
        unit="kg",
        partner=None,
    )

    assert event.net_quantity == Decimal("-3.25")


def test_wms_event_preserves_document_and_movement_fields() -> None:
    event = WmsEvent(
        product_code="SKU-004",
        product_name="Anonymized product",
        event_datetime=datetime(2026, 6, 2, 10, 30),
        operation_type="TRANSFER",
        document_number="DOC-002",
        normalized_document="DOC-002",
        source_location="REC100",
        destination_location="RAFT-001",
        lot=None,
        quantity=Decimal("4.00"),
        partner=None,
    )

    assert event.normalized_document == "DOC-002"
    assert event.quantity == Decimal("4.00")
    assert event.source_location == "REC100"
    assert event.destination_location == "RAFT-001"


def test_source_and_movement_enums_keep_expected_values() -> None:
    assert SourceSystem.WMS.value == "WMS"
    assert SourceSystem.WME.value == "WME"
    assert SourceSystem.STOCK_REPORT.value == "STOCK_REPORT"
    assert SourceSystem.BASELINE_REPORT.value == "BASELINE_REPORT"
    assert MovementDirection.IN.value == "IN"
    assert MovementDirection.OUT.value == "OUT"
    assert MovementDirection.NEUTRAL.value == "NEUTRAL"
    assert MovementDirection.UNKNOWN.value == "UNKNOWN"
