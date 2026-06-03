from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class QuantityRelation(str, Enum):
    EXACT = "EXACT"
    ROUNDING_DIFF = "ROUNDING_DIFF"
    DIFFERENT = "DIFFERENT"


@dataclass(frozen=True)
class QuantityComparison:
    wms_quantity: Decimal
    wme_net_quantity: Decimal
    difference: Decimal
    relation: QuantityRelation
    tolerance: Decimal


def compare_quantities(
    wms_quantity: Decimal,
    wme_net_quantity: Decimal,
    *,
    tolerance: Decimal = Decimal("0.0001"),
) -> QuantityComparison:
    """Compare WMS quantity against WME net quantity only.

    Difference is calculated as WMS - WME. This utility does not decide document,
    product, timing, or reconciliation verdicts.
    """
    difference = wms_quantity - wme_net_quantity
    absolute_difference = abs(difference)

    if difference == Decimal("0"):
        relation = QuantityRelation.EXACT
    elif absolute_difference <= tolerance:
        relation = QuantityRelation.ROUNDING_DIFF
    else:
        relation = QuantityRelation.DIFFERENT

    return QuantityComparison(
        wms_quantity=wms_quantity,
        wme_net_quantity=wme_net_quantity,
        difference=difference,
        relation=relation,
        tolerance=tolerance,
    )
