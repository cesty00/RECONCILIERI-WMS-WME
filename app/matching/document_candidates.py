from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.normalization import canonical_document, candidate_document_keys


class DocumentCandidateRelation(str, Enum):
    EXACT_KEY = "EXACT_KEY"
    CANDIDATE_ALIAS = "CANDIDATE_ALIAS"
    NO_CANDIDATE = "NO_CANDIDATE"


@dataclass(frozen=True)
class DocumentCandidateMatch:
    relation: DocumentCandidateRelation
    wms_key: str | None
    wme_key: str | None
    shared_key: str | None


def compare_document_candidates(wms_document: object, wme_document: object) -> DocumentCandidateMatch:
    """Compare document text keys only.

    This utility does not inspect product, quantity, timing or source data and does not
    produce reconciliation verdicts.
    """
    wms_key = canonical_document(wms_document)
    wme_key = canonical_document(wme_document)
    if wms_key is None or wme_key is None:
        return DocumentCandidateMatch(
            relation=DocumentCandidateRelation.NO_CANDIDATE,
            wms_key=wms_key,
            wme_key=wme_key,
            shared_key=None,
        )

    if wms_key == wme_key:
        return DocumentCandidateMatch(
            relation=DocumentCandidateRelation.EXACT_KEY,
            wms_key=wms_key,
            wme_key=wme_key,
            shared_key=wms_key,
        )

    wms_candidates = set(candidate_document_keys(wms_document))
    wme_candidates = set(candidate_document_keys(wme_document))
    shared = sorted(wms_candidates.intersection(wme_candidates))
    if shared:
        return DocumentCandidateMatch(
            relation=DocumentCandidateRelation.CANDIDATE_ALIAS,
            wms_key=wms_key,
            wme_key=wme_key,
            shared_key=shared[0],
        )

    return DocumentCandidateMatch(
        relation=DocumentCandidateRelation.NO_CANDIDATE,
        wms_key=wms_key,
        wme_key=wme_key,
        shared_key=None,
    )
