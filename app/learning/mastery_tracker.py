"""Mastery level calculation combining multiple signals."""

from app.config import settings


def calculate_mastery(
    total_time_seconds: int = 0,
    expected_time_seconds: int = 3600,
    average_quality: float = 0.0,
    interval_days: int = 0,
) -> float:
    """Calculate mastery level (0.0-1.0) from multiple signals.

    Combines three factors with configurable weights:
      - Time spent (diminishing returns after expected time)
      - Practice performance (average quality score / 5)
      - Spaced repetition stability (interval length indicator)

    Args:
        total_time_seconds: Total time spent learning this point
        expected_time_seconds: Expected time to reach basic understanding
        average_quality: Average SM-2 quality score (0-5) from reviews
        interval_days: Current SM-2 interval in days (longer = more stable)

    Returns:
        Mastery level from 0.0 (none) to 1.0 (mastered)
    """
    # Time factor: diminishing returns after expected time
    time_ratio = total_time_seconds / max(expected_time_seconds, 1)
    time_factor = min(1.0, time_ratio)

    # Practice factor: quality score normalized to 0-1
    practice_factor = min(1.0, average_quality / 5.0)

    # Stability factor: longer intervals = more stable knowledge
    stability_factor = min(1.0, interval_days / 90.0)

    # Weighted combination
    mastery = (
        settings.mastery_time_weight * time_factor
        + settings.mastery_practice_weight * practice_factor
        + settings.mastery_stability_weight * stability_factor
    )

    return round(min(1.0, max(0.0, mastery)), 4)
