"""Tests for the mastery level calculator."""

from app.learning.mastery_tracker import calculate_mastery


def test_mastery_zero():
    """No learning = mastery 0."""
    m = calculate_mastery(total_time_seconds=0, average_quality=0.0, interval_days=0)
    assert m == 0.0


def test_mastery_full():
    """All max inputs = mastery 1."""
    m = calculate_mastery(
        total_time_seconds=7200,   # 2 hours
        expected_time_seconds=3600,
        average_quality=5.0,
        interval_days=90,
    )
    assert m == 1.0


def test_mastery_partial():
    """Partial inputs = partial mastery."""
    m = calculate_mastery(
        total_time_seconds=1800,   # 0.5 hours
        expected_time_seconds=3600,
        average_quality=3.0,
        interval_days=10,
    )
    assert 0.0 < m < 1.0


def test_mastery_not_exceed_one():
    """Mastery should not exceed 1.0."""
    m = calculate_mastery(
        total_time_seconds=999999,
        average_quality=5.0,
        interval_days=999,
    )
    assert m == 1.0


def test_mastery_weights():
    """Practice weight is highest (default 0.5)."""
    m_practice_high = calculate_mastery(
        total_time_seconds=0,
        average_quality=5.0,  # practice factor = 1.0
        interval_days=0,
    )
    # 0.2*0 + 0.5*1.0 + 0.3*0 = 0.5
    assert m_practice_high == 0.5
