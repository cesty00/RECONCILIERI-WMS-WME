from __future__ import annotations

from app.aggregation import AggregatedWmeDocument
from app.matching import (
    DocumentCandidateRelation,
    ProductCodeRelation,
    compare_document_candidates,
    compare_product_codes,
)
from app.models import ReconciliationStatus, WmsEvent
from app.reconciliation.evidence import (
    EvidenceNote,
    EvidenceSeverity,
    ReconciliationCandidateInput,
    ReconciliationEvidence,
    SourceReference,
)
from app.reconciliation.quantity import QuantityRelation, compare_quantities


def build_pair_evidence(wms_event: WmsEvent, wme_document: AggregatedWmeDocument) -> ReconciliationEvidence:
    """Build conservative evidence for one WMS event and one aggregated WME document.

    This function does not emit PASS/MATCH verdicts and is not a batch reconciliation engine.
    """
    document_relation = compare_document_candidates(
        wms_event.normalized_document,
        wme_document.normalized_document,
    )
    product_relation = compare_product_codes(wms_event.product_code, wme_document.product_code)
    quantity_relation = compare_quantities(wms_event.quantity, wme_document.net_quantity)

    notes = _build_notes(
        document_relation.relation,
        product_relation.relation,
        quantity_relation.relation,
    )
    candidate = ReconciliationCandidateInput(
        product_code=wms_event.product_code,
        normalized_document=wms_event.normalized_document,
        wms_events=(wms_event,),
        wme_events=wme_document.source_events,
        source_references=(
            SourceReference(
                source="WMS",
                document=wms_event.normalized_document,
                product_code=wms_event.product_code,
            ),
            SourceReference(
                source="WME",
                document=wme_document.normalized_document,
                product_code=wme_document.product_code,
            ),
        ),
    )

    return ReconciliationEvidence(
        candidate=candidate,
        document_relation=document_relation.relation,
        quantity_difference=quantity_relation.difference,
        status_ceiling=ReconciliationStatus.REVIEW_REQUIRED,
        notes=tuple(notes),
    )


def _build_notes(
    document_relation: DocumentCandidateRelation,
    product_relation: ProductCodeRelation,
    quantity_relation: QuantityRelation,
) -> list[EvidenceNote]:
    notes: list[EvidenceNote] = []
    if document_relation == DocumentCandidateRelation.NO_CANDIDATE:
        notes.append(EvidenceNote(EvidenceSeverity.WARNING, "DOCUMENT", "No document candidate relationship"))
    elif document_relation == DocumentCandidateRelation.CANDIDATE_ALIAS:
        notes.append(EvidenceNote(EvidenceSeverity.INFO, "DOCUMENT_ALIAS", "Document alias candidate only"))

    if product_relation == ProductCodeRelation.MISSING:
        notes.append(EvidenceNote(EvidenceSeverity.WARNING, "PRODUCT_MISSING", "Product code missing on one side"))
    elif product_relation == ProductCodeRelation.DIFFERENT:
        notes.append(EvidenceNote(EvidenceSeverity.WARNING, "PRODUCT_DIFFERENT", "Product codes differ"))

    if quantity_relation == QuantityRelation.DIFFERENT:
        notes.append(EvidenceNote(EvidenceSeverity.WARNING, "QUANTITY", "Quantity difference outside tolerance"))
    elif quantity_relation == QuantityRelation.ROUNDING_DIFF:
        notes.append(EvidenceNote(EvidenceSeverity.INFO, "ROUNDING", "Quantity difference within tolerance"))

    return notes
