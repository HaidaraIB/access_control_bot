import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    OWNER_ID = int(os.getenv("OWNER_ID"))
    ERRORS_CHANNEL = int(os.getenv("ERRORS_CHANNEL"))

    PRIVATE_CHANNEL_ID = int(os.getenv("PRIVATE_CHANNEL_ID"))

    DB_PATH = os.getenv("DB_PATH")
    DB_POOL_SIZE = 20
    DB_MAX_OVERFLOW = 10
