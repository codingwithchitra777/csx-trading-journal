from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    telegram_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    firebase_sa_path: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "")
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    csx_base_url: str = os.getenv("CSX_BASE_URL", "https://csx.com.kh")
    csx_lang: str = os.getenv("CSX_LANG", "en")
    default_user_id: str = os.getenv("DEFAULT_USER_ID", "u001")

settings = Settings()
