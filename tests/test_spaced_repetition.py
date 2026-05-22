"""Tests for the SM-2 spaced repetition algorithm."""

import datetime
from app.learning.spaced_repetition import sm2_calculate, get_due_knowledge_points


def utcnow():
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)


def test_sm2_perfect_recall():
    """Perfect recall should increase interval and EF."""
    ef, interval, reps, next_review = sm2_calculate(
        quality=5, repetitions=0, easiness_factor=2.5, interval_days=0
    )
    assert reps == 1
    assert interval == 1  # First review: interval = 1
    assert ef > 2.5  # EF should increase


def test_sm2_second_correct():
    """Second correct recall: interval = 6."""
    ef, interval, reps, next_review = sm2_calculate(
        quality=4, repetitions=1, easiness_factor=2.5, interval_days=1
    )
    assert reps == 2
    assert interval == 6
    assert next_review > utcnow()


def test_sm2_incorrect_reset():
    """Incorrect recall should reset repetitions."""
    ef, interval, reps, next_review = sm2_calculate(
        quality=1, repetitions=3, easiness_factor=2.5, interval_days=10
    )
    assert reps == 0  # Reset
    assert interval == 1  # Back to 1 day


def test_sm2_ef_floor():
    """EF should not go below 1.3."""
    ef, interval, reps, next_review = sm2_calculate(
        quality=0, repetitions=0, easiness_factor=1.3, interval_days=0
    )
    assert ef >= 1.3


def test_sm2_quality_clamping():
    """Quality should be clamped to 0-5."""
    ef, interval, reps, next_review = sm2_calculate(
        quality=10, repetitions=0, easiness_factor=2.5, interval_days=0
    )
    assert reps == 1  # Treated as quality=5


def test_sm2_repeated_success():
    """Multiple successful recalls should increase interval exponentially."""
    ef = 2.5
    interval = 0
    reps = 0

    # Simulate 3 successful reviews
    ef, interval, reps, _ = sm2_calculate(5, reps, ef, interval)
    assert interval == 1 and reps == 1

    ef, interval, reps, _ = sm2_calculate(5, reps, ef, interval)
    assert interval == 6 and reps == 2

    ef, interval, reps, _ = sm2_calculate(5, reps, ef, interval)
    # After 2 successful reviews, ef=2.7, interval=round(6*2.7)=16
    assert interval == 16 and reps == 3


def test_get_due_empty():
    """Empty list should return empty."""
    assert get_due_knowledge_points([]) == []
