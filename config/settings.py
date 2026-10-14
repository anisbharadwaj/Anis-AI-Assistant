# Application-wide settings and defaults
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "anis_ai.db"

class Settings:
    def __init__(self):
        self.ai_provider = os.getenv("AI_PROVIDER", "none")
        self.preferred_language = os.getenv("PREFERRED_LANGUAGE", "en")
        self.database_path = os.getenv("DATABASE_PATH", str(DEFAULT_DB))

    def to_dict(self):
        return {
            "ai_provider": self.ai_provider,
            "preferred_language": self.preferred_language,
            "database_path": self.database_path,
        }
