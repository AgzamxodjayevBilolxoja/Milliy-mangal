from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp2, db
from keyboards.default.markup import remove_keyboard,admin_menu_markup
from keyboards.inline.markup import yes_or_no_markup
from services.database.sql import check_staff_by_chat_id
from states.states import AddBranch

@dp2.message_handler(text="📍 Filiallar")
async def branches_handler(message: types.Message):
    admin = db.execute(check_staff_by_chat_id, (message.from_user.id, ), fetchone=True)
    if admin:
        role = admin[2]
        if role == "Admin":
            await message.delete()
            await message.answer('Yangi filial qo\'shish uchun filial joylashuvini yuboring!', reply_markup=remove_keyboard)
            await AddBranch.location.set()
        else:
            await message.answer('Sizda bu buyruq uchun ruxsatyo\'q!')
            await message.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')
    else:
        await message.answer('Sizda bu buyruq uchun ruxsatyo\'q!')
        await message.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')

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
        pass
    else:
        await callback.message.answer('❌ Filial qo\'shilmadi!')
        await callback.message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()