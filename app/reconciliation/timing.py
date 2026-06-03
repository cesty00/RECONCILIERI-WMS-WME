from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class TimingRelation(str, Enum):
    SAME_DAY = "SAME_DAY"
    WITHIN_WINDOW = "WITHIN_WINDOW"
    OUTSIDE_WINDOW = "OUTSIDE_WINDOW"
    MISSING = "MISSING"


@dataclass(frozen=True)
class TimingComparison:
    relation: TimingRelation
    wms_date: date | None
    wme_date: date | None
    day_difference: int | None
    window_days: int


def compare_event_dates(
    wms_value: date | datetime | None,
    wme_value: date | datetime | None,
    *,
    window_days: int = 1,
) -> TimingComparison:
    """Compare WMS and WME event dates only.

    This utility does not inspect document, product, quantity, or reconciliation verdicts.
    """
    wms_date = _to_date(wms_value)
    wme_date = _to_date(wme_value)

    if wms_date is None or wme_date is None:
        return TimingComparison(
            relation=TimingRelation.MISSING,
            wms_date=wms_date,
            wme_date=wme_date,
            day_difference=None,
            window_days=window_days,
        )

    day_difference = (wms_date - wme_date).days
    absolute_difference = abs(day_difference)
    if day_difference == 0:
        relation = TimingRelation.SAME_DAY
    elif absolute_difference <= window_days:
        relation = TimingRelation.WITHIN_WINDOW
    else:
        relation = TimingRelation.OUTSIDE_WINDOW

    return TimingComparison(
        relation=relation,
        wms_date=wms_date,
        wme_date=wme_date,
        day_difference=day_difference,
        window_days=window_days,
    )


def _to_date(value: date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    return value
