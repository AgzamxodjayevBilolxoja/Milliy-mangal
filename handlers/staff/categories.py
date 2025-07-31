from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp2, db
from keyboards.default.markup import admin_menu_markup, back_uz, admin_category_markup, back_markup, uz, get_categories_markup, delete_markup
from keyboards.inline.markup import *
from services.database.sql import add_category, get_categories, delete_category_by_name_uz
from states.states import AdminMain, AdminCategory, AddCategory, GetCategories


@dp2.message_handler(text="Kategoriyalar", state=AdminMain.menu)
async def admin_categories_handler(message: types.Message):
    await message.delete()
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_category_markup)
    await AdminCategory.step_one.set()

@dp2.message_handler(text="➕ Kategoriya qo'shish", state=AdminCategory.step_one)
async def add_category_handler(message: types.Message):
    await message.delete()
    await message.answer("Kategoriya qo'shish uchun 🇺🇿 O'zbekcha nomini yuboring!", reply_markup=back_markup(uz))
    await AddCategory.name_uz.set()

@dp2.message_handler(state=AddCategory.name_uz)
async def add_category_name_uz_handler(message: types.Message, state: FSMContext):
    await state.update_data(name_uz=message.text)
    await message.delete()
    await message.answer('Endi kategoriyaning 🇷🇺 Ruscha nomini yuboring!', reply_markup=back_markup(uz))
    await AddCategory.name_ru.set()

@dp2.message_handler(state=AddCategory.name_ru)
async def back_main_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name_uz = data.get('name_uz')
    name_ru = message.text
    db.execute(add_category, (name_uz, name_ru), commit=True)
    await message.delete()
    await message.answer('✅ Kategoriya qo\'shildi')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_category_markup)
    await AdminCategory.step_one.set()

@dp2.message_handler(text="Kategoriyalarni ko'rish", state=AdminCategory.step_one)
async def get_categories_handler(message: types.Message):
    await message.delete()
    categories = db.execute(get_categories, fetchall=True)
    await message.answer(text='Kategoriyalardan birini tanlang!', reply_markup=get_categories_markup(categories, uz))
    await GetCategories.step_one.set()

@dp2.message_handler(lambda x: x.text in [category[1] for category in db.execute(get_categories, fetchall=True)], state=GetCategories.step_one)
async def cet_category_handler(message: types.Message, state: FSMContext):
    await message.delete()
    await state.update_data(name_uz=message.text)
    await message.answer('Buyqurlardan birini tanlang!', reply_markup=delete_markup)
    await GetCategories.delete.set()

@dp2.message_handler(text="🔴 O'chirish", state=GetCategories.delete)
async def delete_category_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name_uz = data.get('name_uz')
    db.execute(delete_category_by_name_uz, (name_uz, ), commit=True)
    await message.delete()
    await message.answer('✅ Kategoriya o\'chirildi!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()