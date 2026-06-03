from __future__ import annotations

import re
from dataclasses import dataclass

DOCUMENT_PATTERN = re.compile(r"(?P<prefix>[A-Za-z]+)[\s\-_/]*(?P<number>\d+)")

WMS_TO_WME_PREFIX_CANDIDATES: dict[str, tuple[str, ...]] = {
    "SFA": ("SFA", "AE"),
    "WME": ("WME", "AE"),
}

GENERIC_PREFIXES = {"AE", "BC", "FE", "F", "NP", "NT", "PV", "SFA", "WME"}


@dataclass(frozen=True)
class NormalizedDocument:
    raw: str
    prefix: str
    number: str

    @property
    def canonical(self) -> str:
        return f"{self.prefix} {self.number}"

    @property
    def compact(self) -> str:
        return f"{self.prefix}{self.number}"


def normalize_document_reference(value: object) -> NormalizedDocument | None:
    """Normalize one document reference without deciding whether it matches another."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    match = DOCUMENT_PATTERN.search(text)
    if not match:
        return None

    prefix = match.group("prefix").upper()
    number = match.group("number").lstrip("0") or "0"
    return NormalizedDocument(raw=text, prefix=prefix, number=number)


def canonical_document(value: object) -> str | None:
    normalized = normalize_document_reference(value)
    if normalized is None:
        return None
    return normalized.canonical


def compact_document(value: object) -> str | None:
    normalized = normalize_document_reference(value)
    if normalized is None:
        return None
    return normalized.compact


def candidate_document_keys(value: object) -> tuple[str, ...]:
    """Return conservative candidate keys for later matching logic.

    This utility does not choose a match and does not imply a reconciliation verdict.
    It only exposes equivalent-looking textual keys that later layers may evaluate
    with additional context.
    """
    normalized = normalize_document_reference(value)
    if normalized is None:
        return ()

    prefixes = WMS_TO_WME_PREFIX_CANDIDATES.get(normalized.prefix, (normalized.prefix,))
    candidates: list[str] = []
    for prefix in prefixes:
        candidates.append(f"{prefix} {normalized.number}")
        candidates.append(f"{prefix}{normalized.number}")

    return tuple(dict.fromkeys(candidates))


def document_key_from_type_and_number(document_type: object, document_number: object) -> str | None:
    """Build a canonical document key from separate WME type and number fields."""
    if document_type is None or document_number is None:
        return None
    prefix = str(document_type).strip().upper()
    number_text = str(document_number).strip()
    if not prefix or not number_text:
        return None
    number_match = re.search(r"\d+", number_text)
    if not number_match:
        return None
    number = number_match.group(0).lstrip("0") or "0"
    return f"{prefix} {number}"
