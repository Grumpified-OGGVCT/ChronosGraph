"""ChronosGraph Configuration — Pydantic Settings loaded from config.env."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from config.env at project root."""

    gemini_api_key: str = "your-key-here"
    model_version: str = "gemini-2.5-pro"
    max_chunk_size_minutes: int = 15

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "chronosgraph"

    chroma_persist_dir: str = "./data/chroma"
    sqlite_db_path: str = "./data/db/queue.db"
    video_cache_dir: str = "./data/cache/video"
    audio_cache_dir: str = "./data/cache/audio"
    log_dir: str = "./logs"

    model_config = {
        "env_file": str(PROJECT_ROOT / "config.env"),
        "env_file_encoding": "utf-8",
    }

    def resolve_path(self, relative: str) -> Path:
        p = Path(relative)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        return p

    def ensure_directories(self) -> None:
        dirs = [
            self.resolve_path(self.chroma_persist_dir),
            self.resolve_path(self.sqlite_db_path).parent,
            self.resolve_path(self.video_cache_dir),
            self.resolve_path(self.audio_cache_dir),
            self.resolve_path(self.log_dir),
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
