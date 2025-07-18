from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp2, db
from keyboards.default.markup import admin_menu_markup, change_menu_markup, back_uz, admin_category_markup, back_markup, uz, get_categories_markup, delete_markup, admin_foods_markup
from keyboards.inline.markup import *
from services.database.sql import check_staff_by_chat_id, add_category, get_categories, delete_category_by_name_uz
from states.states import AdminMain, AdminCategory, AddCategory, GetCategories, AdminProduct, AddProduct

@dp2.message_handler(text="🍽️ Menyu o'zgartirish")
async def menu_hander(message: types.Message):
    admin = db.execute(check_staff_by_chat_id, (message.from_user.id, ), fetchone=True)
    if admin:
        role = admin[2]
        if role == "Admin":
            await message.delete()
            await message.answer('Buyruqlardan birini tanlang!', reply_markup=change_menu_markup)
            await AdminMain.menu.set()
        else:
            await message.answer('Sizda bu buyruq uchun ruxsat yo\'q!')
            await message.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')
    else:
        await message.answer('Sizda bu buyruq uchun ruxsat yo\'q!')
        await message.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')
