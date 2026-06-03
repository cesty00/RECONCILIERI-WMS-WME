from app.matching import DocumentCandidateRelation, compare_document_candidates


def test_compare_document_candidates_exact_key():
    result = compare_document_candidates("AE-000123", "AE 123")

    assert result.relation == DocumentCandidateRelation.EXACT_KEY
    assert result.wms_key == "AE 123"
    assert result.wme_key == "AE 123"
    assert result.shared_key == "AE 123"


def test_compare_document_candidates_alias_key():
    result = compare_document_candidates("SFA47326", "AE 47326")

    assert result.relation == DocumentCandidateRelation.CANDIDATE_ALIAS
    assert result.wms_key == "SFA 47326"
    assert result.wme_key == "AE 47326"
    assert result.shared_key in {"AE 47326", "AE47326"}


def test_compare_document_candidates_wme_alias_key():
    result = compare_document_candidates("WME112133", "AE 112133")

    assert result.relation == DocumentCandidateRelation.CANDIDATE_ALIAS
    assert result.wms_key == "WME 112133"
    assert result.wme_key == "AE 112133"


def test_compare_document_candidates_no_candidate_for_different_numbers():
    result = compare_document_candidates("SFA47326", "AE 99999")

    assert result.relation == DocumentCandidateRelation.NO_CANDIDATE
    assert result.shared_key is None


def test_compare_document_candidates_no_candidate_for_invalid_input():
    result = compare_document_candidates("no-number", "AE 123")

    assert result.relation == DocumentCandidateRelation.NO_CANDIDATE
    assert result.wms_key is None
    assert result.wme_key == "AE 123"
    assert result.shared_key is None
