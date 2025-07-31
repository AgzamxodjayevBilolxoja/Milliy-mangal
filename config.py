import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_TOKEN2 = os.getenv("BOT_TOKEN2")
ADMINS = list(map(int, os.getenv("ADMINS").split(",")))
