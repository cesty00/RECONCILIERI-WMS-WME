from __future__ import annotations

from dataclasses import dataclass

from app.models import ReconciliationStatus, WmsEvent

RECEIVING_LOCATIONS = {"REC100", "RECEPTIE", "RECEPTION"}
VERIFY_LOCATIONS = {"VER100", "VERIFICARE", "VERIFY"}


@dataclass(frozen=True)
class WmsMovementClassification:
    status: ReconciliationStatus
    reason: str


def classify_wms_movement(event: WmsEvent) -> WmsMovementClassification:
    """Classify WMS movement shape only.

    This utility does not match WME events and does not produce reconciliation verdicts.
    """
    source = _normalize_location(event.source_location)
    destination = _normalize_location(event.destination_location)
    operation = _normalize_text(event.operation_type)

    if source and destination and source == destination:
        return WmsMovementClassification(
            status=ReconciliationStatus.STATUS_ONLY,
            reason="source and destination locations are the same",
        )

    if source and destination:
        return WmsMovementClassification(
            status=ReconciliationStatus.LOCATION_ONLY,
            reason="source and destination locations differ",
        )

    if source in RECEIVING_LOCATIONS or destination in RECEIVING_LOCATIONS:
        return WmsMovementClassification(
            status=ReconciliationStatus.LOCATION_ONLY,
            reason="movement touches receiving location",
        )

    if source in VERIFY_LOCATIONS or destination in VERIFY_LOCATIONS:
        return WmsMovementClassification(
            status=ReconciliationStatus.STATUS_ONLY,
            reason="movement touches verification/status location",
        )

    if any(token in operation for token in ("MUTARE", "TRANSFER", "MOVE")):
        return WmsMovementClassification(
            status=ReconciliationStatus.REVIEW_REQUIRED,
            reason="movement operation lacks enough location context",
        )

    return WmsMovementClassification(
        status=ReconciliationStatus.REVIEW_REQUIRED,
        reason="movement shape is not classifiable by utility rules",
    )


def _normalize_location(value: str | None) -> str | None:
    text = _normalize_text(value)
    if text == "":
        return None
    return text


def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()
