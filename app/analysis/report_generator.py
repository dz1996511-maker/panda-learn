import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    Document,
    KnowledgePoint,
    MasteryRecord,
    PracticeSession,
    SpacedRepetition,
)


async def generate_learning_report(db: AsyncSession) -> dict:
    """Generate a comprehensive learning report."""
    # Document stats
    result = await db.execute(select(func.count(Document.id)))
    doc_count = result.scalar() or 0

    # Knowledge point stats
    result = await db.execute(select(func.count(KnowledgePoint.id)))
    kp_count = result.scalar() or 0

    # Practice stats
    result = await db.execute(
        select(func.count(PracticeSession.id)).where(
            PracticeSession.status == "completed"
        )
    )
    practice_count = result.scalar() or 0

    # Average mastery
    result = await db.execute(
        select(func.avg(MasteryRecord.mastery_level)).where(
            MasteryRecord.id.in_(
                select(func.max(MasteryRecord.id)).group_by(MasteryRecord.knowledge_point_id)
            )
        )
    )
    avg_mastery = result.scalar() or 0.0

    # Due for review
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    result = await db.execute(
        select(func.count(SpacedRepetition.id)).where(
            SpacedRepetition.next_review_at <= now
        )
    )
    due_count = result.scalar() or 0

    # Weakest knowledge points (lowest mastery)
    # Subquery to get latest mastery per KP
    subq = (
        select(
            MasteryRecord.knowledge_point_id,
            func.max(MasteryRecord.id).label("max_id"),
        )
        .group_by(MasteryRecord.knowledge_point_id)
        .subquery()
    )
    result = await db.execute(
        select(KnowledgePoint.label, MasteryRecord.mastery_level)
        .join(MasteryRecord, MasteryRecord.id == subq.c.max_id)
        .where(KnowledgePoint.id == subq.c.knowledge_point_id)
        .order_by(MasteryRecord.mastery_level.asc())
        .limit(5)
    )
    weakest = [
        {"label": label, "mastery": round(mastery * 100, 1)}
        for label, mastery in result.all()
    ]

    return {
        "document_count": doc_count,
        "knowledge_point_count": kp_count,
        "practice_count": practice_count,
        "average_mastery": round(avg_mastery * 100, 1),
        "due_review_count": due_count,
        "weakest_points": weakest,
    }
