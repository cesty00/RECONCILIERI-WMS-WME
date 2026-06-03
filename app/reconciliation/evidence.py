from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from app.models import ReconciliationStatus, WmeEvent, WmsEvent
from app.matching import DocumentCandidateRelation


class EvidenceSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass(frozen=True)
class EvidenceNote:
    severity: EvidenceSeverity
    code: str
    message: str


@dataclass(frozen=True)
class SourceReference:
    source: str
    row_index: int | None = None
    document: str | None = None
    product_code: str | None = None


@dataclass(frozen=True)
class ReconciliationCandidateInput:
    product_code: str | None
    normalized_document: str | None
    wms_events: tuple[WmsEvent, ...] = field(default_factory=tuple)
    wme_events: tuple[WmeEvent, ...] = field(default_factory=tuple)
    source_references: tuple[SourceReference, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ReconciliationEvidence:
    candidate: ReconciliationCandidateInput
    document_relation: DocumentCandidateRelation
    quantity_difference: Decimal | None = None
    status_ceiling: ReconciliationStatus = ReconciliationStatus.REVIEW_REQUIRED
    notes: tuple[EvidenceNote, ...] = field(default_factory=tuple)

    @property
    def has_errors(self) -> bool:
        return any(note.severity == EvidenceSeverity.ERROR for note in self.notes)

    @property
    def has_warnings(self) -> bool:
        return any(note.severity == EvidenceSeverity.WARNING for note in self.notes)
