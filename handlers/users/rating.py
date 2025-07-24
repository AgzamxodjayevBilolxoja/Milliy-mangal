from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, db, bot2
from keyboards.inline.markup import language_markup
from keyboards.default.markup import rating_markup, uz, back_uz, menu_markup, back_markup, ru, back_ru
from states.states import Rating, Register
from services.database.sql import create_rating, check_user, get_staffs

@dp.message_handler(text="⭐ Baholash")
@dp.message_handler(text="⭐ Оценить")
async def rating_handler(message: types.Message, state: FSMContext):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    if user:
        lang = user[2]
        await message.delete()
        if lang == 'uz':
            await message.answer('Buyruqlardan birini tanlang!', reply_markup=rating_markup(uz))
        else:
            await message.answer('Выберите одну из команд!', reply_markup=rating_markup(ru))
        await Rating.step_one.set()
    else:
        answer = f"""
Assalomu alaykum <b>{message.from_user.first_name}</b>, men Milliy Mangal Botman.
Здравствуйте <b>{message.from_user.first_name}</b>, я Mangal Burger Bot.

Tilni tanlag!
Выберите язык!
    """
        await message.answer(text=answer, reply_markup=language_markup)
        await Register.lang.set()

@dp.message_handler(lambda m: m.text in ["⭐⭐⭐⭐⭐ Hammasi a'lo", "⭐⭐⭐⭐ Yaxshi", "⭐⭐⭐ O'rta", "❤️ Bo'ladi", "👎 Juda yomon"], state=Rating.step_one)
@dp.message_handler(lambda m: m.text in ["⭐⭐⭐⭐⭐ Всё хорошо", "⭐⭐⭐⭐ Хороший", "⭐⭐⭐ Средний", "❤️ Будет", "👎 Очень плохо"], state=Rating.step_one)
async def button_uz_handler(message: types.Message, state: FSMContext):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    text = message.text
    if text in ["⭐⭐⭐⭐⭐ Hammasi a'lo", "⭐⭐⭐⭐⭐ Всё хорошо"]:
        await state.update_data(rating=5)
    elif text in ["⭐⭐⭐⭐ Yaxshi", "⭐⭐⭐⭐ Хороший"]:
        await state.update_data(rating=4)
    elif text in ["⭐⭐⭐ O'rta", "⭐⭐⭐ Средний"]:
        await state.update_data(rating=3)
    elif text in ["❤️ Bo'ladi", "❤️ Будет"]:
        await state.update_data(rating=2)
    elif text in ["👎 Juda yomon", "👎 Очень плохо"]:
        await state.update_data(rating=1)
    await message.delete()
    if lang == 'uz':
        await message.answer('Nima uchun bunday qaror qabul qildingiz, izoh yozib qoldiring!', reply_markup=back_markup(uz))
    else:
        await message.answer('Оставьте комментарий, объяснив, почему вы приняли такое решение!', reply_markup=back_markup(ru))
    await Rating.comment.set()

@dp.message_handler(text=back_uz, state=Rating.step_one)
@dp.message_handler(text=back_uz, state=Rating.comment)
@dp.message_handler(text=back_ru, state=Rating.step_one)
@dp.message_handler(text=back_ru, state=Rating.comment)
async def back_uz_handler(message: types.Message, state: FSMContext):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    await message.delete()
    if lang == 'uz':
        await message.answer('Menyu', reply_markup=menu_markup(uz))
    else:
        await message.answer('Меню', reply_markup=menu_markup(ru))
    await state.finish()


@dp.message_handler(state=Rating.comment)
async def comment_uz_handler(message: types.Message, state: FSMContext):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    data = await state.get_data()
    rating = data.get('rating')
    comment = message.text
    user_id = user[0]
    lang = user[2]
    db.execute(create_rating, (user_id, rating, comment), commit=True)
    await message.delete()
    if lang == 'uz':
        await message.answer('Fikringiz uchun raxmat ☺️!')
        await message.answer('Menyu', reply_markup=menu_markup(uz))
    else:
        await message.answer('Спасибо за ваше мнение ☺️!')
        await message.answer('Меню', reply_markup=menu_markup(ru))
    await state.finish()
    rate = ""
    if rating == 5:
        rate = "⭐⭐⭐⭐⭐ Hammasi a'lo"
    elif rating == 4:
        rate = "⭐⭐⭐⭐ Yaxshi"
    elif rating == 3:
        rate = "⭐⭐⭐ O'rta"
    elif rating == 2:
        rate = "❤️ Bo'ladi"
    elif rating == 1:
        rate = "👎 Juda yomon"
    ADMINS = db.execute(get_staffs, ('Admin', ), fetchall=True)
    for admin in ADMINS:
        answer = f"""
Foydalanuvchilardan izoh

Ball: {rate}
Izoh: {comment}
"""
        await bot2.send_message(admin[0], answer)

@dp.message_handler(state=Rating.step_one)
async def error_uz_handler(message: types.Message, state: FSMContext):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    await message.delete()
    if lang == 'uz':
        await message.answer('Buyruqlardan birini tanlang!', reply_markup=rating_markup(uz))
    else:
        await message.answer('Выберите одну из команд!', reply_markup=rating_markup(ru))
    await Rating.step_one.set()