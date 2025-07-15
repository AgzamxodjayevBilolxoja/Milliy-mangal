from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp2, db
from keyboards.default.markup import remove_keyboard,admin_menu_markup, admin_branch_markup, uz, get_branches_markup, back_uz, admin_branch_update_markup, branch_update_markup, back_markup
from keyboards.inline.markup import yes_or_no_markup
from services.database.sql import check_staff_by_chat_id, add_branch, get_branch_by_name, get_branches, update_location_branch, update_name_branch, update_time_branch, delete_branch
from states.states import AddBranch, AdminMain, UpdateBranch

@dp2.message_handler(text="📍 Filiallar")
async def branches_handler(message: types.Message):
    admin = db.execute(check_staff_by_chat_id, (message.from_user.id, ), fetchone=True)
    if admin:
        role = admin[2]
        if role == "Admin":
            await message.delete()
            await message.answer('Buyruqni tanlang', reply_markup=admin_branch_markup)
            await AdminMain.branch.set()
        else:
            await message.answer('Sizda bu buyruq uchun ruxsat yo\'q!')
            await message.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')
    else:
        await message.answer('Sizda bu buyruq uchun ruxsat yo\'q!')
        await message.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')

@dp2.message_handler(text="➕ Filial qo'shish", state=AdminMain.branch)
async def branches_handler(message: types.Message):
    await message.delete()
    await message.answer('Yangi filial qo\'shish uchun filial joylashuvini yuboring!', reply_markup=remove_keyboard)
    await AddBranch.location.set()

@dp2.message_handler(state=AddBranch.location, content_types=types.ContentType.LOCATION)
async def location_handler(message: types.Message, state: FSMContext):
    latitude = message.location.latitude
    longitude = message.location.longitude
    await state.update_data(latitude=latitude)
    await state.update_data(longitude=longitude)
    await message.delete()
    await message.answer('Filial joylashuv nomini yuboring!')
    await AddBranch.name.set()

@dp2.message_handler(state=AddBranch.name)
async def name_hnadler(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.delete()
    await message.answer('Endi shu filialning ishlash vaqtini yuboring, Masalan 24/7 yoki 8:00-20:00')
    await AddBranch.opening_time.set()

@dp2.message_handler(state=AddBranch.opening_time)
async def opening_time_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    name = data.get('name')
    opening_time = message.text
    await state.update_data(opening_time=opening_time)
    await message.delete()
    await message.answer_location(latitude=latitude, longitude=longitude)
    await message.answer(text=f"{name} ---------- {opening_time}")
    await message.answer('Barcha ma\'lumotlar to\'g\'rimi?', reply_markup=yes_or_no_markup)
    await AddBranch.yes_or_no.set()

@dp2.callback_query_handler(lambda x: x.data in ['yes', 'no'], state=AddBranch.yes_or_no)
async def yes_or_no_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    name = data.get('name')
    opening_time = data.get('opening_time')
    await callback.message.delete()
    if callback.data == 'yes':
        try:
            db.execute(add_branch, (latitude, longitude, name, opening_time), commit=True)
            await callback.message.answer('✅ Filial qo\'shildi!')
        except:
            await callback.message.answer('Qandaydiq xato sodir bo\'di.')
            await callback.message.answer('Bu filialni oldin qo\'shgan bo\'lishingiz mumkin. Iltimos tekshirib ko\'ring!')
            await callback.message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
        await state.finish()
    else:
        await callback.message.answer('❌ Filial qo\'shilmadi!')
        await callback.message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()

@dp2.message_handler(text="📍 Filiallarni ko'rish", state=AdminMain.branch)
async def branches_handler(message: types.Message):
    await message.delete()
    branches = db.execute(get_branches, fetchall=True)
    await message.answer('Filiallardan birini tanlang!', reply_markup=get_branches_markup(branches, uz))
    await UpdateBranch.step_one.set()

@dp2.message_handler(lambda x: x.text in [branch[0] for branch in db.execute(get_branches, fetchall=True)], state=UpdateBranch.step_one)
async def get_branch_handler(message: types.Message, state: FSMContext):
    branch = db.execute(get_branch_by_name, (message.text, ), fetchone=True)
    await message.delete()
    await message.answer_location(latitude=branch[1], longitude=branch[2])
    await state.update_data(id=branch[0])
    await message.answer(f"{branch[3]} ---------- {branch[4]}")
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_branch_update_markup)
    await UpdateBranch.update.set()

@dp2.message_handler(text=back_uz, state=UpdateBranch.update)
async def back_branches_handler(message: types.Message):
    await message.delete()
    branches = db.execute(get_branches, fetchall=True)
    await message.answer('Filiallardan birini tanlang!', reply_markup=get_branches_markup(branches, uz))
    await UpdateBranch.step_one.set()

@dp2.message_handler(text="🟢 O'zgartirish", state=UpdateBranch.update)
async def update_branch_handler(message: types.Message):
    await message.delete()
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=branch_update_markup)
    await UpdateBranch.choose_command.set()

@dp2.message_handler(lambda x: x.text in ["📍 Joylashuvni o'zgartirish", "✏️ Nomini o'zgartirish", "🕛 Ishlash vaqtini o'zgartirish"], state=UpdateBranch.choose_command)
async def update_handler(message: types.Message, state: FSMContext):
    await message.delete()
    if message.text == "📍 Joylashuvni o'zgartirish":
        await message.answer('Yangi joylashuvni yuboting!', reply_markup=back_markup(uz))
        await state.update_data(field='location')
    elif message.text == "✏️ Nomini o'zgartirish":
        await message.answer('Yangi nomni yuboring!', reply_markup=back_markup(uz))
        await state.update_data(field='name')
    elif message.text == "🕛 Ishlash vaqtini o'zgartirish":
        await message.answer('Yangi ishlash vaqtini yuboring!', reply_markup=back_markup(uz))
        await state.update_data(field='opening_time')
    await UpdateBranch.update_field.set()
    
@dp2.message_handler(text=back_uz, state=UpdateBranch.choose_command)
async def back_main_handler(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()

@dp2.message_handler(state=UpdateBranch.choose_command)
async def error_handler(message: types.Message):
    await message.delete()
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=branch_update_markup)
    await UpdateBranch.choose_command.set()

@dp2.message_handler(content_types=types.ContentType.LOCATION, state=UpdateBranch.update_field)
async def location_handler(message: types.Message, state: FSMContext):
    latitude = message.location.latitude
    longitude = message.location.longitude
    data = await state.get_data()
    id = data.get('id')
    await message.delete()
    try:
        db.execute(update_location_branch, (latitude, longitude, id), commit=True)
        await message.answer('✅ Filial joylashuvi o\'zgartirildi!')
    except:
        await message.answer('❌ Nimadir xato ketdi!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()

@dp2.message_handler(content_types=types.ContentType.TEXT, state=UpdateBranch.update_field)
async def location_handler(message: types.Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    id = data.get('id')
    field = data.get('field')
    await message.delete()
    try:
        if field == 'name':
            db.execute(update_name_branch, (text, id), commit=True)
            await message.answer('✅ Filial nomi o\'zgartirildi!')
        elif field == 'opening_time':
            db.execute(update_time_branch, (text, id), commit=True)
            await message.answer('✅ Filial ishlash vaqti o\'zgartirildi!')
    except:
        await message.answer('❌ Nimadir xato ketdi!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()

@dp2.message_handler(text="🔴 O'chirish", state=UpdateBranch.update)
async def update_branch_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    id = data.get('id')
    await message.delete()
    try:
        db.execute(delete_branch, (id, ), commit=True)
        await message.answer('✅ Filial o\'chirildi!')
    except:
        await message.answer('❌ Nimadir xato ketdi!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()

@dp2.message_handler(text=back_uz, state=UpdateBranch.step_one)
async def back_main_hadnler(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()

@dp2.message_handler(state=UpdateBranch.step_one)
async def error_branch_handler(message: types.Message):
    await message.delete()
    branches = db.execute(get_branches, fetchall=True)
    await message.answer('Filiallardan birini tanlang!', reply_markup=get_branches_markup(branches, uz))