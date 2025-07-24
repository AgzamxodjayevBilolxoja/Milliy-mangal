from aiogram import types

from loader import dp, db
from services.database.sql import check_user

@dp.message_handler(text="ℹ️ Biz haqimizda")
@dp.message_handler(text="ℹ️ О нас")
async def about_us_uz_handler(message: types.Message):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    if lang == 'uz':
        answer = """
🍔 Milliy Mangal

Ish vaqti: 24/7
Tel: +998900910090
<a href="https://www.instagram.com/milliy.mangal/" >Instagram</a>
⬇️ Manzilimiz ⬇️
"""
        await message.answer(answer)
    else:
        answer = """
🍔 Milliy Mangal

Время работы: 24/7
Tel: +998900910090
<a href="https://www.instagram.com/milliy.mangal/" >Instagram</a>
⬇️ Наш адрес ⬇️
"""

        await message.answer(answer)
    await message.answer_location(latitude=41.295019, longitude=69.199774)