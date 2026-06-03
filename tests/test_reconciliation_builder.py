from datetime import date
from decimal import Decimal

from app.aggregation import AggregatedWmeDocument
from app.matching import DocumentCandidateRelation
from app.models import ReconciliationStatus, WmeEvent, WmsEvent
from app.reconciliation import EvidenceSeverity, build_pair_evidence


def _wms_event(document="SFA 47326", quantity="5.75"):
    return WmsEvent(
        product_code="SKU-001",
        product_name="Anonymized product",
        event_datetime=None,
        operation_type="Mutare",
        document_number=document,
        normalized_document=document,
        source_location="REC100",
        destination_location="RAFT-001",
        lot="LOT-001",
        quantity=Decimal(quantity),
        partner="Anonymized partner",
    )


def _wme_event(document="AE 47326", in_quantity="5.75", out_quantity="0"):
    return WmeEvent(
        product_name="Anonymized product",
        internal_product_code="SKU-001",
        document_type="AE",
        document_number=document,
        normalized_document=document,
        event_date=date(2026, 6, 2),
        in_quantity=Decimal(in_quantity),
        out_quantity=Decimal(out_quantity),
        stock_after=Decimal("10.00"),
        warehouse="Depozit Principal",
        unit="kg",
        partner="Anonymized partner",
    )


def _wme_document(document="AE 47326", in_quantity="5.75", out_quantity="0"):
    event = _wme_event(document=document, in_quantity=in_quantity, out_quantity=out_quantity)
    return AggregatedWmeDocument(
        product_code="SKU-001",
        normalized_document=document,
        document_type="AE",
        product_name="Anonymized product",
        document_number=document,
        event_date=date(2026, 6, 2),
        in_quantity=Decimal(in_quantity),
        out_quantity=Decimal(out_quantity),
        source_row_count=1,
        source_events=(event,),
    )


def test_build_pair_evidence_keeps_review_required_even_for_candidate_alias_and_exact_quantity():
    evidence = build_pair_evidence(_wms_event(), _wme_document())

    assert evidence.document_relation == DocumentCandidateRelation.CANDIDATE_ALIAS
    assert evidence.quantity_difference == Decimal("0.00")
    assert evidence.status_ceiling == ReconciliationStatus.REVIEW_REQUIRED
    assert evidence.candidate.product_code == "SKU-001"
    assert len(evidence.candidate.wms_events) == 1
    assert len(evidence.candidate.wme_events) == 1
    assert {ref.source for ref in evidence.candidate.source_references} == {"WMS", "WME"}
    assert not evidence.has_errors


def test_build_pair_evidence_adds_quantity_warning_when_quantities_differ():
    evidence = build_pair_evidence(_wms_event(quantity="5.75"), _wme_document(in_quantity="4.00"))

    assert evidence.quantity_difference == Decimal("1.75")
    assert evidence.status_ceiling == ReconciliationStatus.REVIEW_REQUIRED
    assert any(note.severity == EvidenceSeverity.WARNING and note.code == "QUANTITY" for note in evidence.notes)


def test_build_pair_evidence_adds_document_warning_when_no_candidate():
    evidence = build_pair_evidence(_wms_event(document="SFA 47326"), _wme_document(document="AE 99999"))

    assert evidence.document_relation == DocumentCandidateRelation.NO_CANDIDATE
    assert evidence.status_ceiling == ReconciliationStatus.REVIEW_REQUIRED
    assert any(note.severity == EvidenceSeverity.WARNING and note.code == "DOCUMENT" for note in evidence.notes)
