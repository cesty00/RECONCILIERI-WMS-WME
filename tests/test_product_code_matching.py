from app.matching import ProductCodeRelation, compare_product_codes


def test_compare_product_codes_exact_after_normalization():
    result = compare_product_codes(" sku-001 ", "SKU-001")

    assert result.relation == ProductCodeRelation.EXACT
    assert result.wms_product_code == "SKU-001"
    assert result.wme_product_code == "SKU-001"


def test_compare_product_codes_missing_when_wms_code_absent():
    result = compare_product_codes(None, "SKU-001")

    assert result.relation == ProductCodeRelation.MISSING
    assert result.wms_product_code is None
    assert result.wme_product_code == "SKU-001"


def test_compare_product_codes_missing_when_wme_code_blank():
    result = compare_product_codes("SKU-001", "")

    assert result.relation == ProductCodeRelation.MISSING
    assert result.wms_product_code == "SKU-001"
    assert result.wme_product_code is None


def test_compare_product_codes_different():
    result = compare_product_codes("SKU-001", "SKU-002")

    assert result.relation == ProductCodeRelation.DIFFERENT
    assert result.wms_product_code == "SKU-001"
    assert result.wme_product_code == "SKU-002"
