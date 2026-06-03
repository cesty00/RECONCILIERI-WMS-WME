from datetime import date, datetime

from app.reconciliation import TimingRelation, compare_event_dates


def test_compare_event_dates_same_day_from_datetime_and_date():
    result = compare_event_dates(datetime(2026, 6, 3, 10, 30), date(2026, 6, 3))

    assert result.relation == TimingRelation.SAME_DAY
    assert result.day_difference == 0
    assert result.wms_date == date(2026, 6, 3)
    assert result.wme_date == date(2026, 6, 3)


def test_compare_event_dates_within_window():
    result = compare_event_dates(date(2026, 6, 4), date(2026, 6, 3), window_days=1)

    assert result.relation == TimingRelation.WITHIN_WINDOW
    assert result.day_difference == 1


def test_compare_event_dates_outside_window():
    result = compare_event_dates(date(2026, 6, 6), date(2026, 6, 3), window_days=1)

    assert result.relation == TimingRelation.OUTSIDE_WINDOW
    assert result.day_difference == 3


def test_compare_event_dates_missing_when_one_side_is_absent():
    result = compare_event_dates(None, date(2026, 6, 3))

    assert result.relation == TimingRelation.MISSING
    assert result.wms_date is None
    assert result.wme_date == date(2026, 6, 3)
    assert result.day_difference is None
