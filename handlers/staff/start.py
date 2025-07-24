from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp2, db
from keyboards.default.markup import staff_start_markup, remove_keyboard, admin_menu_markup, back_uz
from states.states import StaffRegister
from services.database.sql import check_staff, update_staff, check_staff_by_chat_id

@dp2.message_handler(commands=['start'], state='*')
async def staff_start_handler(message: types.Message, state: FSMContext):
    await state.finish()
    staff = db.execute(check_staff_by_chat_id, (message.from_user.id,), fetchone=True)
    if staff:
        role = staff[2]
        if role == 'Admin':
            await message.answer('Xush kelibsiz Admin')
            await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
            await state.finish()
    else:
        await message.answer('Milliy Mangal Ishchi botiga xush kelibsiz!\n\nQaysi ishda ishlaysiz?\nTugma orqali tanlang!', reply_markup=staff_start_markup)
        await StaffRegister.role.set()
    

@dp2.message_handler(lambda x: x.text in ['Admin', 'Oshpaz', 'Yetkazib beruvchi'], state=StaffRegister.role)
async def role_handler(message: types.Message, state: FSMContext):
    await state.update_data(role=message.text)
    await message.delete()
    await message.answer(F'Siz haqiqatdan ham {message.text} bo\'lsangiz, unda o\'z parolingiznikiriting!', reply_markup=remove_keyboard)
    await StaffRegister.password.set()

@dp2.message_handler(state=StaffRegister.password)
async def password_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    role = data.get('role')
    password = message.text
    role = 'Admin' if role == 'Admin' else 'Chef' if role == 'Oshpaz' else 'Deliverman'
    staff = db.execute(check_staff, (role, password), fetchone=True)
    await message.delete()
    if staff:
        db.execute(update_staff, (message.from_user.id, role, password), commit=True)
        await message.answer(f'Siz haqiqatdan ham {role} ekansiz!')
        await message.answer(f'Xush kelibsiz {role}')
        if role == "Admin":
            await message.answer('Buyruqlardan birini tanlang!',reply_markup= admin_menu_markup)
            await state.finish()
    else:
        await message.answer('❌ Parol xato!')
        await message.answer('Qaytatdan urinib ko\'ring!')

@dp2.message_handler(text=back_uz, state="*")
async def command_chef_handler(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()