"""Tests for document reference normalization utilities only."""

from app.normalization import (
    canonical_document,
    candidate_document_keys,
    compact_document,
    document_key_from_type_and_number,
    normalize_document_reference,
)


def test_normalize_document_reference_extracts_prefix_and_number() -> None:
    normalized = normalize_document_reference(" SFA-00047326 ")

    assert normalized is not None
    assert normalized.raw == "SFA-00047326"
    assert normalized.prefix == "SFA"
    assert normalized.number == "47326"
    assert normalized.canonical == "SFA 47326"
    assert normalized.compact == "SFA47326"


def test_canonical_and_compact_document_helpers() -> None:
    assert canonical_document("wme112133") == "WME 112133"
    assert compact_document("wme 112133") == "WME112133"


def test_candidate_document_keys_are_conservative_and_do_not_choose_match() -> None:
    assert candidate_document_keys("SFA47326") == (
        "SFA 47326",
        "SFA47326",
        "AE 47326",
        "AE47326",
    )
    assert candidate_document_keys("WME112133") == (
        "WME 112133",
        "WME112133",
        "AE 112133",
        "AE112133",
    )


def test_document_key_from_type_and_number_supports_document_intrare_nt() -> None:
    assert document_key_from_type_and_number("NT", "69138") == "NT 69138"
    assert document_key_from_type_and_number(" ae ", "000112133") == "AE 112133"


def test_invalid_or_blank_document_values_return_none_or_empty_candidates() -> None:
    assert normalize_document_reference(None) is None
    assert normalize_document_reference("") is None
    assert normalize_document_reference("no numeric suffix") is None
    assert canonical_document("no numeric suffix") is None
    assert compact_document("no numeric suffix") is None
    assert candidate_document_keys("no numeric suffix") == ()
    assert document_key_from_type_and_number("AE", "no-number") is None
