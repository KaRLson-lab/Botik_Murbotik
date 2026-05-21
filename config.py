import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = "database.db"
REMINDER_HOUR = 21
REMINDER_MINUTE = 0