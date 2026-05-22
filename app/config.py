from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "AI 学习助手"
    debug: bool = True

    # Database
    database_path: str = str(Path(__file__).parent.parent / "data" / "learning_assistant.db")

    # Vector store
    chroma_db_path: str = str(Path(__file__).parent.parent / "data" / "chroma_db")

    # File uploads
    upload_dir: str = str(Path(__file__).parent.parent / "data" / "uploads")
    max_upload_size_mb: int = 50

    # LLM — default provider
    llm_provider: str = "deepseek"
    claude_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"

    # Chunking
    chunk_target_tokens: int = 512
    chunk_overlap_tokens: int = 128

    # Learning
    mastery_time_weight: float = 0.2
    mastery_practice_weight: float = 0.5
    mastery_stability_weight: float = 0.3

    # Practice
    default_questions_per_session: int = 5


settings = Settings()
