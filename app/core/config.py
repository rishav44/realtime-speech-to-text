
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME = "Real-Time Multilingual Speech-to-Text"
    VERSION = "1.0.0"

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./speech_to_text.db"
    )

    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    DEVICE = os.getenv("DEVICE", "cpu")
    COMPUTE_TYPE = os.getenv("COMPUTE_TYPE", "int8")


settings = Settings()
