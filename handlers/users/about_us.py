from aiogram import types

from loader import dp, db
from services.database.sql import check_user
from states.states import Register
from keyboards.inline.markup import language_markup

@dp.message_handler(text="ℹ️ Biz haqimizda")
@dp.message_handler(text="ℹ️ О нас")
async def about_us_uz_handler(message: types.Message):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    if user:
        lang = user[2]
        if lang == 'uz':
            answer = """
🍔 Milliy Mangal

Ish vaqti: 24/7
Tel: +998900910090
<a href="https://www.instagram.com/milliy.mangal/" >Instagram</a>
"""
            await message.answer(answer)
        else:
            answer = """
🍔 Milliy Mangal

Время работы: 24/7
Tel: +998900910090
<a href="https://www.instagram.com/milliy.mangal/" >Instagram</a>
"""

            await message.answer(answer)
    else:
        answer = f"""
Assalomu alaykum <b>{message.from_user.first_name}</b>, men Milliy Mangal Botman.
Здравствуйте <b>{message.from_user.first_name}</b>, я Mangal Burger Bot.

Tilni tanlag!
Выберите язык!
    """
        await message.answer(text=answer, reply_markup=language_markup)
        await Register.lang.set()