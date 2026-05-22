import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean,
    ForeignKey, DateTime, UniqueConstraint, Index,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


# ─── Settings ────────────────────────────────────────────────────────

class SettingsModel(Base):
    __tablename__ = "settings"

    key = Column(String(255), primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


# ─── Knowledge Base ──────────────────────────────────────────────────

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    source_path = Column(Text)
    source_type = Column(String(50), nullable=False)  # file_upload, text_paste, web_url
    file_type = Column(String(20))  # pdf, txt, md, html
    raw_text = Column(Text)
    word_count = Column(Integer, default=0)
    char_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    summary = Column(Text)
    tags = Column(Text)  # JSON array
    imported_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    knowledge_points = relationship("KnowledgePoint", back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    embedding_id = Column(String(255))

    document = relationship("Document", back_populates="chunks")

    __table_args__ = (
        Index("idx_chunks_document", "document_id"),
    )


# ─── Knowledge Points ───────────────────────────────────────────────

class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"))
    label = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50))  # concept, formula, definition, principle, procedure
    source_chunk_ids = Column(Text)  # JSON array of chunk IDs
    embedding_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="knowledge_points")
    learning_sessions = relationship("LearningSession", back_populates="knowledge_point")
    mastery_records = relationship("MasteryRecord", back_populates="knowledge_point", order_by="MasteryRecord.recorded_at.desc()")
    spaced_repetition = relationship("SpacedRepetition", back_populates="knowledge_point", uselist=False)
    review_logs = relationship("ReviewLog", back_populates="knowledge_point")
    practice_questions = relationship("PracticeQuestion", back_populates="knowledge_point")
    practice_schedules = relationship("PracticeSchedule", back_populates="knowledge_point")


class ConceptRelation(Base):
    __tablename__ = "concept_relations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("knowledge_points.id", ondelete="CASCADE"), nullable=False)
    target_id = Column(Integer, ForeignKey("knowledge_points.id", ondelete="CASCADE"), nullable=False)
    relation_type = Column(String(50), nullable=False)  # prerequisite, related, similar, contradicts
    description = Column(Text)
    strength = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("source_id", "target_id", "relation_type"),
    )


# ─── Learning Records ───────────────────────────────────────────────

class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id", ondelete="CASCADE"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer, default=0)
    focus_level = Column(Integer)  # 1-5
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    knowledge_point = relationship("KnowledgePoint", back_populates="learning_sessions")


class MasteryRecord(Base):
    __tablename__ = "mastery_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id", ondelete="CASCADE"), nullable=False)
    mastery_level = Column(Float, nullable=False, default=0.0)  # 0.0-1.0
    confidence_score = Column(Float, default=0.0)
    assessment_method = Column(String(50), default="self")  # self, practice, llm
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)

    knowledge_point = relationship("KnowledgePoint", back_populates="mastery_records")

    __table_args__ = (
        Index("idx_mastery_kp", "knowledge_point_id"),
    )


# ─── Spaced Repetition ──────────────────────────────────────────────

class SpacedRepetition(Base):
    __tablename__ = "spaced_repetition"

    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id", ondelete="CASCADE"), nullable=False, unique=True)
    easiness_factor = Column(Float, default=2.5)
    interval_days = Column(Integer, default=0)
    repetitions = Column(Integer, default=0)
    next_review_at = Column(DateTime)
    last_reviewed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    knowledge_point = relationship("KnowledgePoint", back_populates="spaced_repetition")

    __table_args__ = (
        Index("idx_spaced_next", "next_review_at"),
    )


class ReviewLog(Base):
    __tablename__ = "review_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id", ondelete="CASCADE"), nullable=False)
    review_date = Column(DateTime, nullable=False)
    quality_score = Column(Integer, nullable=False)  # SM-2: 0-5
    response_time_ms = Column(Integer)
    session_id = Column(Integer, ForeignKey("learning_sessions.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    knowledge_point = relationship("KnowledgePoint", back_populates="review_logs")

    __table_args__ = (
        Index("idx_review_log_kp", "knowledge_point_id"),
    )


# ─── Practice ───────────────────────────────────────────────────────

class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scheduled_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    question_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, in_progress, completed, skipped
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    questions = relationship("PracticeQuestion", back_populates="session")

    __table_args__ = (
        Index("idx_practice_session_status", "status"),
    )


class PracticeQuestion(Base):
    __tablename__ = "practice_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id", ondelete="CASCADE"))
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id", ondelete="SET NULL"))
    question_type = Column(String(50), nullable=False)  # multiple_choice, true_false, short_answer, fill_blank
    question_text = Column(Text, nullable=False)
    options = Column(Text)  # JSON array
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text)
    difficulty = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("PracticeSession", back_populates="questions")
    knowledge_point = relationship("KnowledgePoint", back_populates="practice_questions")
    answers = relationship("PracticeAnswer", back_populates="question")

    __table_args__ = (
        Index("idx_questions_session", "session_id"),
    )


class PracticeAnswer(Base):
    __tablename__ = "practice_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("practice_questions.id", ondelete="CASCADE"), nullable=False)
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    confidence = Column(Integer)  # 1-3
    response_time_ms = Column(Integer)
    feedback = Column(Text)
    answered_at = Column(DateTime, default=datetime.datetime.utcnow)

    question = relationship("PracticeQuestion", back_populates="answers")

    __table_args__ = (
        Index("idx_answers_question", "question_id"),
    )


class PracticeSchedule(Base):
    __tablename__ = "practice_schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id", ondelete="CASCADE"))
    frequency_days = Column(Integer, default=1)
    question_count = Column(Integer, default=5)
    enabled = Column(Boolean, default=True)
    next_due_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    knowledge_point = relationship("KnowledgePoint", back_populates="practice_schedules")


# ─── Analysis Cache ─────────────────────────────────────────────────

class AnalysisCache(Base):
    __tablename__ = "analysis_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    analysis_type = Column(String(50), nullable=False)  # summary, concepts, relations
    result = Column(Text, nullable=False)  # JSON blob
    llm_model = Column(String(100))
    token_cost = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("document_id", "analysis_type"),
        Index("idx_analysis_doc_type", "document_id", "analysis_type"),
    )
