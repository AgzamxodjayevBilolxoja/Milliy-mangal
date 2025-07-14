from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from services.database.database import Database
from config import BOT_TOKEN, BOT_TOKEN2

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
bot2 = Bot(token=BOT_TOKEN2, parse_mode="HTML")

storage = MemoryStorage()

dp = Dispatcher(bot=bot, storage=storage)
dp2 = Dispatcher(bot=bot2, storage=storage)

db = Database()