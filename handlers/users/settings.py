from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, db
from keyboards.inline.markup import language_markup
from keyboards.default.markup import settings_markup, uz, back_uz, menu_markup, lang_markup, back_markup, phone_markup, ru, back_ru
from states.states import Settings, Register
from services.database.sql import change_name, change_phone, change_lang, check_user

@dp.message_handler(text="⚙️ Sozlamalar")
@dp.message_handler(text="⚙️ Настройки")
async def settings_handler(message: types.Message, state: FSMContext):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    if user:
        lang = user[2]
        await message.delete()
        if lang == 'uz':
            await message.answer(text='Buyruqni tanlang', reply_markup=settings_markup(uz))
        else:
            await message.answer(text='Выберите движение', reply_markup=settings_markup(ru))
        await Settings.step_one.set()
    else:
        answer = f"""
Assalomu alaykum <b>{message.from_user.first_name}</b>, men Milliy Mangal Botman.
Здравствуйте <b>{message.from_user.first_name}</b>, я Mangal Burger Bot.

Tilni tanlag!
Выберите язык!
    """
        await message.answer(text=answer, reply_markup=language_markup)
        await Register.lang.set()
        

@dp.message_handler(text="✏️ Ism o'zgartirish", state=Settings.step_one)
@dp.message_handler(text="✏️ Изменить имя", state=Settings.step_one)
async def name_handler(message: types.Message):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    await message.delete()
    if lang == 'uz':
        await message.answer('Yangi ism kiriting!', reply_markup=back_markup(uz))
    else:
        await message.answer('Ведите новое имя', reply_markup=back_markup(ru))
    await Settings.name.set()

@dp.message_handler(lambda m: m.text in[back_uz, back_ru], state=Settings.name)
@dp.message_handler(lambda m: m.text in[back_uz, back_ru], state=Settings.phone)
async def back_settings_handler(message: types.Message):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    await message.delete()
    if lang == 'uz':
        await message.answer(text='Buyruqni tanlang', reply_markup=settings_markup(uz))
    else:
        await message.answer(text='Выберите движение', reply_markup=settings_markup(ru))
    await Settings.step_one.set()

@dp.message_handler(state=Settings.name, content_types=types.ContentType.TEXT)
async def change_name_handler(message: types.Message, state: FSMContext):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    name = message.text
    db.execute(change_name, (name, message.from_user.id), commit=True)
    await message.delete()
    if lang == 'uz':
        await message.answer('✅ Ism o\'zgartirildi!')
        await message.answer('Menyu', reply_markup=menu_markup(uz))
    else:
        await message.answer('✅ Имя изменена!')
        await message.answer('Меню', reply_markup=menu_markup(ru))
    await state.finish()

@dp.message_handler(text="📱 Telefon raqam o'zgartirish", state=Settings.step_one)
@dp.message_handler(text="📱 Изменить телефон номер", state=Settings.step_one)
async def phone_handler(message: types.Message):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    await message.delete()
    if lang == 'uz':
        await message.answer('Telefon raqam o\'zgartirish uchun tugmani bosing, yoki +998xx xxx xx xx korinishda raqam yuboring!', reply_markup=phone_markup(uz))
    else:
        await message.answer('Чтобы изменить свой номер телефона, нажмите кнопку или отправьте номер в формате +998xx xxx xx xx!', reply_markup=phone_markup(ru))
    await Settings.phone.set()

@dp.message_handler(state=Settings.phone, content_types=types.ContentType.CONTACT)
async def change_phone_handler(message: types.Message, state: FSMContext):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    phone = message.contact.phone_number
    db.execute(change_phone, (phone, message.from_user.id), commit=True)
    await message.delete()
    if lang == 'uz':
        await message.answer('✅ Telefon raqam o\'zgartirildi!')
        await message.answer('Menyu', reply_markup=menu_markup(uz))
    else:
        await message.answer('✅ Номер телефона изменена!')
        await message.answer('Меню', reply_markup=menu_markup(ru))
    await state.finish()

@dp.message_handler(state=Settings.phone)
async def change_phone_two_handler(message: types.Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").replace("-", "")
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    await message.delete()
    if text.startswith("+998") and len(text) == 13 and text[1:].isdigit():
        db.execute(change_phone, (text, message.from_user.id), commit=True)
        if lang == 'uz':
            await message.answer('✅ Telefon raqam o\'zgartirildi!')
            await message.answer('Menyu', reply_markup=menu_markup(uz))
        else:
            await message.answer('✅ Номер телефона изменена!')
            await message.answer('Меню', reply_markup=menu_markup(ru))
        await state.finish()
    else:
        if lang == 'uz':
            await message.answer("Telefon raqam o\'zgartirish uchun tugmani bosing, yoki +998xx xxx xx xx korinishda raqam yuboring!", reply_markup=phone_markup(uz))
        else:
            await message.answer('Чтобы изменить свой номер телефона, нажмите кнопку или отправьте номер в формате +998xx xxx xx xx!', reply_markup=phone_markup(ru))

@dp.message_handler(text="🇷🇺 Til o'zgartirish", state=Settings.step_one)
@dp.message_handler(text="🇺🇿 Изменить язык", state=Settings.step_one)
async def lang_handler(message: types.Message):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    await message.delete()
    if lang == 'uz':
        await message.answer(text='Tilni tanlang!', reply_markup=lang_markup)
    else:
        await message.answer(text='Выберите язык!', reply_markup=lang_markup)
    await Settings.lang.set()

@dp.message_handler(lambda m: m.text in [uz, ru], state=Settings.lang)
async def change_lang_handler(message: types.Message, state: FSMContext):
    lang = message.text
    await message.delete()
    if lang == uz:
        db.execute(change_lang, ('uz', message.from_user.id), commit=True)
        await message.answer('✅ Yangi til tanlandi!')
        await message.answer('Menyu', reply_markup=menu_markup(uz))
    else:
        db.execute(change_lang, ('ru', message.from_user.id), commit=True)
        await message.answer('✅ Новый язык выбран!')
        await message.answer('Меню', reply_markup=menu_markup(ru))
    await state.finish()
    
@dp.message_handler(state=Settings.lang)
async def error_lang_handler(message: types.Message):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    await message.delete()
    if lang == 'uz':
        await message.answer(text='Tilni tanlang!', reply_markup=lang_markup)
    else:
        await message.answer(text='Выберите язык!', reply_markup=lang_markup)
    await Settings.lang.set()

@dp.message_handler(lambda m: m.text in [back_uz, back_ru], state=Settings.step_one)
async def back_main_handler(message: types.Message, state: FSMContext):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    await message.delete()
    if lang == 'uz':
        await message.answer(text='Menyu', reply_markup=menu_markup(uz))
    else:
        await message.answer(text='Меню', reply_markup=menu_markup(ru))
    await state.finish()
    