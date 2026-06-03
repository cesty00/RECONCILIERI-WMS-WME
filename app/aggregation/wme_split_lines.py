from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

from app.models import WmeEvent


@dataclass(frozen=True)
class AggregatedWmeDocument:
    product_code: str | None
    normalized_document: str | None
    document_type: str
    product_name: str
    document_number: str | None
    event_date: object | None
    in_quantity: Decimal
    out_quantity: Decimal
    source_row_count: int
    source_events: tuple[WmeEvent, ...]

    @property
    def net_quantity(self) -> Decimal:
        return self.in_quantity - self.out_quantity


def aggregate_wme_split_lines(events: list[WmeEvent] | tuple[WmeEvent, ...]) -> list[AggregatedWmeDocument]:
    """Aggregate WME split lines by product and normalized document only.

    This utility does not match WMS events and does not produce reconciliation verdicts.
    """
    grouped: dict[tuple[str | None, str | None, str], list[WmeEvent]] = defaultdict(list)
    for event in events:
        key = (event.internal_product_code, event.normalized_document, event.document_type)
        grouped[key].append(event)

    aggregated: list[AggregatedWmeDocument] = []
    for (product_code, normalized_document, document_type), group in grouped.items():
        first = group[0]
        aggregated.append(
            AggregatedWmeDocument(
                product_code=product_code,
                normalized_document=normalized_document,
                document_type=document_type,
                product_name=first.product_name,
                document_number=first.document_number,
                event_date=first.event_date,
                in_quantity=sum((event.in_quantity for event in group), Decimal("0")),
                out_quantity=sum((event.out_quantity for event in group), Decimal("0")),
                source_row_count=len(group),
                source_events=tuple(group),
            )
        )

    return sorted(
        aggregated,
        key=lambda item: (
            item.product_code or "",
            item.normalized_document or "",
            item.document_type,
        ),
    )
