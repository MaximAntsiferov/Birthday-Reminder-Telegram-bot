import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = [int(i) for i in os.getenv("ADMINS").split(",")]

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

I18N_DOMAIN = "birthday_reminder"
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / "locales"
