"""Practice scheduling logic."""

import datetime
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.models import (
    KnowledgePoint,
    PracticeSchedule,
    PracticeSession,
    PracticeQuestion,
    SpacedRepetition,
)
from app.practice.question_generator import generate_question


async def get_due_practice_items(db: AsyncSession) -> list[dict]:
    """Get knowledge points that need practice."""
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)

    # Get items from schedules
    result = await db.execute(
        select(PracticeSchedule, KnowledgePoint).join(
            KnowledgePoint,
            PracticeSchedule.knowledge_point_id == KnowledgePoint.id,
        ).where(
            PracticeSchedule.enabled == True,  # noqa: E712
            (PracticeSchedule.next_due_at == None)  # noqa: E711
            | (PracticeSchedule.next_due_at <= now),
        ).limit(10)
    )
    rows = result.all()

    items = []
    for schedule, kp in rows:
        items.append({
            "kp_id": kp.id,
            "label": kp.label,
            "content": kp.content,
            "frequency_days": schedule.frequency_days,
            "question_count": schedule.question_count,
        })

    # Also get items due for review via spaced repetition
    if len(items) < 10:
        result2 = await db.execute(
            select(SpacedRepetition, KnowledgePoint).join(
                KnowledgePoint,
                SpacedRepetition.knowledge_point_id == KnowledgePoint.id,
            ).where(
                (SpacedRepetition.next_review_at == None)  # noqa: E711
                | (SpacedRepetition.next_review_at <= now),
            ).limit(10 - len(items))
        )
        rows2 = result2.all()
        for sr, kp in rows2:
            if not any(i["kp_id"] == kp.id for i in items):
                items.append({
                    "kp_id": kp.id,
                    "label": kp.label,
                    "content": kp.content,
                    "frequency_days": 1,
                    "question_count": settings.default_questions_per_session,
                })

    return items


async def create_practice_session(
    db: AsyncSession,
    items: list[dict],
) -> PracticeSession:
    """Create a practice session with generated questions."""
    session = PracticeSession(
        scheduled_at=datetime.datetime.now(datetime.UTC).replace(tzinfo=None),
        started_at=datetime.datetime.now(datetime.UTC).replace(tzinfo=None),
        status="in_progress",
    )
    db.add(session)
    await db.flush()

    question_count = 0
    for item in items:
        q = await generate_question(item["label"], item["content"])
        if q:
            pq = PracticeQuestion(
                session_id=session.id,
                knowledge_point_id=item["kp_id"],
                question_type=q.get("question_type", "multiple_choice"),
                question_text=q.get("question", ""),
                options=json.dumps(q.get("options", [])) if q.get("options") else None,
                correct_answer=q.get("answer", ""),
                explanation=q.get("explanation", ""),
            )
            db.add(pq)
            question_count += 1

    session.question_count = question_count
    await db.commit()
    await db.refresh(session)
    return session
