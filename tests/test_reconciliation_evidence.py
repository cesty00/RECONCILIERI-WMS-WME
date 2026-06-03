from decimal import Decimal

from app.matching import DocumentCandidateRelation
from app.models import ReconciliationStatus
from app.reconciliation import (
    EvidenceNote,
    EvidenceSeverity,
    ReconciliationCandidateInput,
    ReconciliationEvidence,
    SourceReference,
)


def test_reconciliation_evidence_defaults_to_review_required():
    candidate = ReconciliationCandidateInput(
        product_code="SKU-001",
        normalized_document="AE 12345",
    )

    evidence = ReconciliationEvidence(
        candidate=candidate,
        document_relation=DocumentCandidateRelation.EXACT_KEY,
    )

    assert evidence.status_ceiling == ReconciliationStatus.REVIEW_REQUIRED
    assert evidence.quantity_difference is None
    assert not evidence.has_errors
    assert not evidence.has_warnings


def test_reconciliation_evidence_tracks_warning_and_error_notes():
    candidate = ReconciliationCandidateInput(
        product_code="SKU-001",
        normalized_document="AE 12345",
    )
    evidence = ReconciliationEvidence(
        candidate=candidate,
        document_relation=DocumentCandidateRelation.CANDIDATE_ALIAS,
        quantity_difference=Decimal("1.25"),
        notes=(
            EvidenceNote(EvidenceSeverity.WARNING, "ALIAS", "Candidate alias only"),
            EvidenceNote(EvidenceSeverity.ERROR, "QTY", "Quantity differs"),
        ),
    )

    assert evidence.has_warnings
    assert evidence.has_errors
    assert evidence.quantity_difference == Decimal("1.25")


def test_reconciliation_candidate_input_preserves_source_references():
    reference = SourceReference(
        source="WMS",
        row_index=7,
        document="SFA 47326",
        product_code="SKU-001",
    )
    candidate = ReconciliationCandidateInput(
        product_code="SKU-001",
        normalized_document="SFA 47326",
        source_references=(reference,),
    )

    assert candidate.source_references == (reference,)
    assert candidate.wms_events == ()
    assert candidate.wme_events == ()
