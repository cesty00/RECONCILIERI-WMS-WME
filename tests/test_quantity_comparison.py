from decimal import Decimal

from app.reconciliation import QuantityRelation, compare_quantities


def test_compare_quantities_exact_match():
    result = compare_quantities(Decimal("5.00"), Decimal("5.00"))

    assert result.relation == QuantityRelation.EXACT
    assert result.difference == Decimal("0.00")


def test_compare_quantities_rounding_diff_within_tolerance():
    result = compare_quantities(
        Decimal("5.00005"),
        Decimal("5.00000"),
        tolerance=Decimal("0.0001"),
    )

    assert result.relation == QuantityRelation.ROUNDING_DIFF
    assert result.difference == Decimal("0.00005")


def test_compare_quantities_different_when_outside_tolerance():
    result = compare_quantities(
        Decimal("5.25"),
        Decimal("5.00"),
        tolerance=Decimal("0.0001"),
    )

    assert result.relation == QuantityRelation.DIFFERENT
    assert result.difference == Decimal("0.25")


def test_compare_quantities_difference_is_wms_minus_wme():
    result = compare_quantities(Decimal("2.00"), Decimal("5.00"))

    assert result.difference == Decimal("-3.00")
    assert result.relation == QuantityRelation.DIFFERENT
