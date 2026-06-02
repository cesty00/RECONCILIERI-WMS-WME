from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class WmsEvent:
    product_code: str
    product_name: str
    event_datetime: datetime | None
    operation_type: str
    document_number: str | None
    normalized_document: str | None
    source_location: str | None
    destination_location: str | None
    lot: str | None
    quantity: Decimal
    partner: str | None
    raw: dict[str, Any] | None = None


@dataclass(frozen=True)
class WmeEvent:
    product_name: str
    internal_product_code: str | None
    document_type: str
    document_number: str | None
    normalized_document: str | None
    event_date: date | None
    in_quantity: Decimal
    out_quantity: Decimal
    stock_after: Decimal | None
    warehouse: str | None
    unit: str | None
    partner: str | None
    raw: dict[str, Any] | None = None

    @property
    def net_quantity(self) -> Decimal:
        return self.in_quantity - self.out_quantity
