from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp2, db
from keyboards.default.markup import admin_menu_markup, admin_staff_markup, back_uz, back_markup, uz, admin_chef_markup, get_branches_markup, get_chefs_markup, admin_update_markup, admin_deliverman_markup, get_delivermen_markup
from services.database.sql import check_staff_by_chat_id, add_chef, add_deliverman, delete_staff_by_id, get_all_chefs, get_all_deliverman, get_branches, get_branch_by_name, get_chef_by_name, get_branch_by_id, update_chef_branch, get_delivermen_by_name, update_deliverman_branch
from states.states import Staff

@dp2.message_handler(text='🦺 Ishchilar')
async def staff_handler(message: types.Message):
    admin = db.execute(check_staff_by_chat_id, (message.from_user.id, ), fetchone=True)
    if admin:
        role = admin[2]
        if role == "Admin":
            await message.delete()
            await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_staff_markup)
            await Staff.step_one.set()
        else:
            await message.answer('Sizda bu buyruq uchun ruxsat yo\'q!')
            await message.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')
    else:
        await message.answer('Sizda bu buyruq uchun ruxsat yo\'q!')
        await message.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')

@dp2.message_handler(text="🧑‍🍳 Oshpazlar", state=Staff.step_one)
async def chefs_handler(message: types.Message):
    await message.delete()
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_chef_markup)
    await Staff.chef_state.set()

@dp2.message_handler(text="➕ Oshpaz qo'shish", state=Staff.chef_state)
async def add_chef_handler(message: types.Message):
    await message.delete()
    await message.answer('Oshpaz qo\'shish uchun uning ismini yuboring!', reply_markup=back_markup(uz))
    await Staff.chef_name.set()

@dp2.message_handler(state=Staff.chef_name)
async def chef_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.delete()
    branches = db.execute(get_branches, fetchall=True)
    await message.answer('Oshpaz qaysi filialda ishlaydi?', reply_markup=get_branches_markup(branches, uz))
    await Staff.chef_branch.set()

@dp2.message_handler(lambda x: x.text in [branch[3] for branch in db.execute(get_branches, fetchall=True)], state=Staff.chef_branch)
async def chef_branch_handler(message: types.Message, state: FSMContext):
    branch = db.execute(get_branch_by_name, (message.text, ), fetchone=True)
    await state.update_data(branch_id=branch[0])
    await message.delete()
    await message.answer('Oshpaz uchun takrorlanmas parol o\'ylab toping?', reply_markup=back_markup(uz))
    await Staff.chef_password.set()

@dp2.message_handler(state=Staff.chef_password)
async def create_chef_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    branch_id = data.get('branch_id')
    password = message.text
    await message.delete()
    try:
        db.execute(add_chef, (password, name, branch_id), commit=True)
        await message.answer("✅ Oshpaz qo'shildi!")
    except:
        await message.answer("❌ Nimadir xato ketdi!")
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()


@dp2.message_handler(text="🧑‍🍳 Oshpazlarni ko'rish", state=Staff.chef_state)
async def get_chefs_hadndler(message: types.Message):
    chefs = db.execute(get_all_chefs, fetchall=True)
    await message.delete()
    await message.answer('Oshpazlardan birini tanlang!', reply_markup=get_chefs_markup(chefs))
    await Staff.get_chef.set()

@dp2.message_handler(lambda x: x.text in [chef[4] for chef in db.execute(get_all_chefs, fetchall=True)], state=Staff.get_chef)
async def choose_command_handler(message: types.Message, state: FSMContext):
    chef = db.execute(get_chef_by_name, (message.text, ), fetchone=True)
    branch = db.execute(get_branch_by_id, (chef[5], ), fetchone=True)
    answer = f"""
Ism: {chef[4]}
Parol: {chef[3]}
"""
    await state.update_data(chef_id=chef[0])
    await message.answer(answer)
    await message.answer_location(latitude=branch[1], longitude=branch[2])
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_update_markup)
    await Staff.command_chef.set()

@dp2.message_handler(text="🔴 O'chirish", state=Staff.command_chef)
async def delete_chef_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    chef_id = data.get('chef_id')
    await message.delete()
    try:
        db.execute(delete_staff_by_id, (chef_id, ), commit=True)
        await message.answer('✅ Oshpaz o\'chirildi!')
    except:
        await message.answer('❌ Nimadir xato bo\'di!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()

@dp2.message_handler(text="🟢 O'zgartirish", state=Staff.command_chef)
async def update_chef_handler(message: types.Message):
    branches = db.execute(get_branches, fetchall=True)
    await message.delete()
    await message.answer('Oshpazning yangi filialinitanlang!', reply_markup=get_branches_markup(branches, uz))
    await Staff.update.set()

@dp2.message_handler(lambda x: x.text in [branch[3] for branch in db.execute(get_branches, fetchall=True)], state=Staff.update)
async def chef_update_handler(message: types.Message, state: FSMContext):
    branch = db.execute(get_branch_by_name, (message.text, ), fetchone=True)
    data = await state.get_data()
    chef_id = data.get('chef_id')
    db.execute(update_chef_branch, (branch[0], chef_id), commit=True)
    await message.delete()
    await message.answer('✅ Oshpaz o\'zgartirildi!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()

@dp2.message_handler(text="🚚 Yetkazib beruvchilar", state=Staff.step_one)
async def chefs_handler(message: types.Message):
    await message.delete()
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_deliverman_markup)
    await Staff.deliverman_state.set()


@dp2.message_handler(text="➕ Yetkazib beruvchi qo'shish", state=Staff.deliverman_state)
async def add_deliverman_handler(message: types.Message):
    await message.delete()
    await message.answer('Yetkazib beruvchi qo\'shish uchun uning ismini yuboring!', reply_markup=back_markup(uz))
    await Staff.deliverman_name.set()

@dp2.message_handler(state=Staff.deliverman_name)
async def deliverman_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.delete()
    branches = db.execute(get_branches, fetchall=True)
    await message.answer('Yetkazib beruvchi qaysi filialda ishlaydi?', reply_markup=get_branches_markup(branches, uz))
    await Staff.deliverman_branch.set()

@dp2.message_handler(lambda x: x.text in [branch[3] for branch in db.execute(get_branches, fetchall=True)], state=Staff.deliverman_branch)
async def deliverman_branch_handler(message: types.Message, state: FSMContext):
    branch = db.execute(get_branch_by_name, (message.text, ), fetchone=True)
    await state.update_data(branch_id=branch[0])
    await message.delete()
    await message.answer('Yetkazib beruvchi uchun takrorlanmas parol o\'ylab toping?', reply_markup=back_markup(uz))
    await Staff.deliverman_password.set()

@dp2.message_handler(state=Staff.deliverman_password)
async def create_deliverman_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    branch_id = data.get('branch_id')
    password = message.text
    await message.delete()
    try:
        db.execute(add_deliverman, (password, name, branch_id), commit=True)
        await message.answer("✅ Yetkazib beruvchi qo'shildi!")
    except:
        await message.answer("❌ Nimadir xato ketdi!")
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()


@dp2.message_handler(text="🚚 Yetkazib beruvchilarni ko\'rish", state=Staff.deliverman_state)
async def get_delivermen_hadndler(message: types.Message):
    delivermen = db.execute(get_all_deliverman, fetchall=True)
    await message.delete()
    await message.answer('Yetkazib beruvchilardan birini tanlang!', reply_markup=get_delivermen_markup(delivermen))
    await Staff.get_deliverman.set()

@dp2.message_handler(lambda x: x.text in [chef[4] for chef in db.execute(get_all_deliverman, fetchall=True)], state=Staff.get_deliverman)
async def choose_command_handler(message: types.Message, state: FSMContext):
    deliverman = db.execute(get_delivermen_by_name, (message.text, ), fetchone=True)
    branch = db.execute(get_branch_by_id, (deliverman[5], ), fetchone=True)
    answer = f"""
Ism: {deliverman[4]}
Parol: {deliverman[3]}
"""
    await state.update_data(deliverman_id=deliverman[0])
    await message.answer(answer)
    await message.answer_location(latitude=branch[1], longitude=branch[2])
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_update_markup)
    await Staff.command_delliverman.set()

@dp2.message_handler(text="🔴 O'chirish", state=Staff.command_delliverman)
async def delete_deliverman_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    deliverman_id = data.get('deliverman_id')
    await message.delete()
    try:
        db.execute(delete_staff_by_id, (deliverman_id, ), commit=True)
        await message.answer('✅ Yetkazib beruvchi o\'chirildi!')
    except:
        await message.answer('❌ Nimadir xato bo\'di!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()

@dp2.message_handler(text="🟢 O'zgartirish", state=Staff.command_delliverman)
async def update_deliverman_handler(message: types.Message):
    branches = db.execute(get_branches, fetchall=True)
    await message.delete()
    await message.answer('Yetkazib beruvchining yangi filialinitanlang!', reply_markup=get_branches_markup(branches, uz))
    await Staff.update_deliverman.set()

@dp2.message_handler(lambda x: x.text in [branch[3] for branch in db.execute(get_branches, fetchall=True)], state=Staff.update_deliverman)
async def deliverman_update_handler(message: types.Message, state: FSMContext):
    branch = db.execute(get_branch_by_name, (message.text, ), fetchone=True)
    data = await state.get_data()
    deliverman_id = data.get('deliverman_id')
    db.execute(update_deliverman_branch, (branch[0], deliverman_id), commit=True)
    await message.delete()
    await message.answer('✅ Yetkazib beruvchi o\'zgartirildi!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()