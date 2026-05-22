"""
SM-2 spaced repetition algorithm implementation.

Based on the SuperMemo SM-2 algorithm by Piotr Wozniak.
Quality scale: 0 (complete blackout) to 5 (perfect response).
"""

import datetime


def sm2_calculate(
    quality: int,
    repetitions: int,
    easiness_factor: float,
    interval_days: int,
) -> tuple[float, int, int, datetime.datetime]:
    """Calculate new SM-2 parameters after a review.

    Args:
        quality: User-assessed recall quality (0-5)
        repetitions: Number of consecutive correct recalls
        easiness_factor: Current easiness factor (EF)
        interval_days: Current interval in days

    Returns:
        (new_easiness_factor, new_interval, new_repetitions, next_review_date)
    """
    # Clamp quality to 0-5
    quality = max(0, min(5, quality))

    if quality >= 3:
        # Correct response
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval_days * easiness_factor)
        repetitions += 1
    else:
        # Incorrect response — reset
        repetitions = 0
        interval = 1

    # Update easiness factor
    easiness_factor = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    easiness_factor = max(1.3, easiness_factor)

    next_review = datetime.datetime.now(datetime.UTC).replace(tzinfo=None) + datetime.timedelta(days=interval)

    return easiness_factor, interval, repetitions, next_review


def get_due_knowledge_points(srs_records: list) -> list:
    """Filter SRS records that are due for review (now or past due)."""
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    return [sr for sr in srs_records if sr.next_review_at is None or sr.next_review_at <= now]
