import os
from pathlib import Path
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv()

# Key Management: Ensure stable Fernet encryption key
def _get_or_create_fernet_key() -> str:
    env_key = os.getenv("FERNET_KEY")
    if env_key and len(env_key.strip()) > 0:
        return env_key.strip()
    
    key_file = DATA_DIR / ".fernet.key"
    if key_file.exists():
        key = key_file.read_text(encoding="utf-8").strip()
        if key:
            return key
    
    # Generate and persist locally
    new_key = Fernet.generate_key().decode("utf-8")
    key_file.write_text(new_key, encoding="utf-8")
    return new_key

# Database and file storage
SQLITE_PATH = os.getenv("SQLITE_PATH", str(DATA_DIR / "healthbuddy.db"))
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
SUMMARIES_DIR = DATA_DIR / "summaries"
SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)

# AI Service Config
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-7-sonnet-20250219").strip()
IS_DEMO_MODE = not bool(ANTHROPIC_API_KEY and len(ANTHROPIC_API_KEY) > 10 and not ANTHROPIC_API_KEY.startswith("your_"))

# Security & Encryption
FERNET_KEY = _get_or_create_fernet_key()

# Application Settings
APP_URL = os.getenv("APP_URL", "http://localhost:8501").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", "5"))

# Localization & Timezone
DEFAULT_TIMEZONE = "Asia/Kolkata"
DEFAULT_REMINDER_TIMES_IST = {
    "morning": "08:00",
    "afternoon": "14:00",
    "night": "20:00"
}

SUPPORTED_LANGUAGES = {
    "en": "English 🇬🇧",
    "te": "తెలుగు 🇮🇳"
}
