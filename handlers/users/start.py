from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, db
from keyboards.default.markup import menu_markup, uz, ru
from keyboards.inline.markup import language_markup
from states.states import Register
from services.database.sql import check_user

@dp.message_handler(commands=['start'], state="*")
async def start_handler(message: types.Message, state: FSMContext):
    await state.finish()
    chat_id = message.from_user.id
    user = db.execute(check_user, (chat_id, ), fetchone=True)
    if user:
        lang = user[2]
        if lang == 'uz':
            await message.answer(f'Menyu', reply_markup=menu_markup(uz))
        else:
            await message.answer(f'Меню', reply_markup=menu_markup(ru))
    else:
        answer = f"""
Assalomu alaykum <b>{message.from_user.first_name}</b>, men Milliy Mangal Botman.
Здравствуйте <b>{message.from_user.first_name}</b>, я Mangal Burger Bot.

Tilni tanlag!
Выберите язык!
    """
        await message.answer(text=answer, reply_markup=language_markup)
        await Register.lang.set()