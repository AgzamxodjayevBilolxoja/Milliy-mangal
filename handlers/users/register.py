from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, db
from keyboards.default.markup import phone_markup, uz, remove_keyboard, ru, menu_markup
from states.states import Register
from services.database.sql import create_user

@dp.callback_query_handler(lambda c: c.data == "uz", state=Register.lang)
async def get_phone_uz_handler(calback: types.CallbackQuery, state: FSMContext):
    await calback.message.delete()
    await calback.message.answer('Iltimos, telefon raqam yuboring, tugmani bosing yoki +998xx xxx xx xx korinishda raqam yuboring. Bu yetkazib berish uchun muhim!', reply_markup=phone_markup(uz))
    await Register.phone.set()
    await state.update_data(lang="uz")

@dp.callback_query_handler(lambda c: c.data == "ru", state=Register.lang)
async def get_phone_uz_handler(calback: types.CallbackQuery, state: FSMContext):
    await calback.message.delete()
    await calback.message.answer('Пожалуйста, отправите свой номер телефона, нажмите кнопку или отправьте номер в формате +998xx xxx xx xx. Это важно для службы доставки!', reply_markup=phone_markup(ru))
    await Register.phone.set()
    await state.update_data(lang="ru")

@dp.message_handler(content_types=types.ContentType.CONTACT, state=Register.phone)
async def phone_uz_handler(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    data = await state.get_data()
    lang = data.get('lang')
    if lang == 'uz':
        await message.answer('Iltimos haqiqiy to\'liq ismingizni yuboring. Bu biz uchun juda muhim!', reply_markup=remove_keyboard)
    else:
        await message.answer('Пожалуйста, отправьте свое настоящее полное имя. Это очень важно для нас!', reply_markup=remove_keyboard)
    await message.delete()
    await Register.name.set()

dp.message_handler(state=Register.phone)
async def change_phone_two_handler(message: types.Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").replace("-", "")
    data = await state.get_data()
    lang = data.get('lang')
    await message.delete()
    if text.startswith("+998") and len(text) == 13 and text[1:].isdigit():
        if lang == 'uz':
            await message.answer('Iltimos haqiqiy to\'liq ismingizni yuboring. Bu biz uchun juda muhim!', reply_markup=remove_keyboard)
        else:
            await message.answer('Пожалуйста, отправьте свое настоящее полное имя. Это очень важно для нас!', reply_markup=remove_keyboard)
        await state.finish()
    else:
        if lang == 'uz':
            await message.answer("Telefon raqam yuborish uchun tugmani bosing, yoki +998xx xxx xx xx korinishda raqam yuboring!", reply_markup=phone_markup(uz))
        else:
            await message.answer('Чтобы отправить свой номер телефона, нажмите кнопку или отправьте номер в формате +998xx xxx xx xx!', reply_markup=phone_markup(ru))
    
@dp.message_handler(content_types=types.ContentType.TEXT, state=Register.name)
async def name_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    chat_id = message.from_user.id
    lang = data.get('lang')
    phone = data.get('phone')
    name = message.text
    db.execute(create_user, (chat_id, lang, phone, name), commit=True)
    await message.delete()
    if lang == 'uz':
        await message.answer('Menyu', reply_markup=menu_markup(uz))
    else:
        await message.answer('Меню', reply_markup=menu_markup(ru))
    await state.finish()
