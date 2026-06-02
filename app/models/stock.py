from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from app.models.statuses import SourceSystem


@dataclass(frozen=True)
class StockSnapshotRow:
    product_code: str
    product_name: str
    location: str
    quantity_erp: Decimal
    quantity_wms: Decimal
    reserved: Decimal
    quantity_difference: Decimal
    source: SourceSystem
    raw: dict[str, Any] | None = None

    def calculated_difference(self) -> Decimal:
        return self.quantity_wms - self.quantity_erp

    def difference_matches_reported(
        self,
        tolerance: Decimal = Decimal("0.0001"),
    ) -> bool:
        return abs(self.calculated_difference() - self.quantity_difference) <= tolerance
