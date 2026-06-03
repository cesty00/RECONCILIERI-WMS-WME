from decimal import Decimal

from app.classification import classify_wms_movement
from app.models import ReconciliationStatus, WmsEvent


def _event(source, destination, operation="Mutare"):
    return WmsEvent(
        product_code="SKU-001",
        product_name="Anonymized product",
        event_datetime=None,
        operation_type=operation,
        document_number="DOC-001",
        normalized_document="DOC 1",
        source_location=source,
        destination_location=destination,
        lot="LOT-001",
        quantity=Decimal("1.00"),
        partner="Anonymized partner",
    )


def test_location_only_when_locations_differ():
    result = classify_wms_movement(_event("REC100", "RAFT-001"))
    assert result.status == ReconciliationStatus.LOCATION_ONLY


def test_status_only_when_locations_are_same():
    result = classify_wms_movement(_event("VER100", "VER100"))
    assert result.status == ReconciliationStatus.STATUS_ONLY


def test_location_only_when_receiving_location_is_present():
    result = classify_wms_movement(_event(None, "Receptie"))
    assert result.status == ReconciliationStatus.LOCATION_ONLY


def test_status_only_when_verification_location_is_present():
    result = classify_wms_movement(_event("VER100", None))
    assert result.status == ReconciliationStatus.STATUS_ONLY


def test_review_required_when_move_lacks_location_context():
    result = classify_wms_movement(_event(None, None, "Transfer"))
    assert result.status == ReconciliationStatus.REVIEW_REQUIRED
