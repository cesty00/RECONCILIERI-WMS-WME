from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ProductCodeRelation(str, Enum):
    EXACT = "EXACT"
    MISSING = "MISSING"
    DIFFERENT = "DIFFERENT"


@dataclass(frozen=True)
class ProductCodeComparison:
    relation: ProductCodeRelation
    wms_product_code: str | None
    wme_product_code: str | None


def compare_product_codes(wms_product_code: object, wme_product_code: object) -> ProductCodeComparison:
    """Compare WMS and WME product codes only.

    This utility does not inspect document, quantity, timing, or reconciliation verdicts.
    """
    wms_code = _normalize_product_code(wms_product_code)
    wme_code = _normalize_product_code(wme_product_code)

    if wms_code is None or wme_code is None:
        relation = ProductCodeRelation.MISSING
    elif wms_code == wme_code:
        relation = ProductCodeRelation.EXACT
    else:
        relation = ProductCodeRelation.DIFFERENT

    return ProductCodeComparison(
        relation=relation,
        wms_product_code=wms_code,
        wme_product_code=wme_code,
    )


def _normalize_product_code(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    if not text:
        return None
    return text
