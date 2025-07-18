from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp2, db
from keyboards.default.markup import admin_menu_markup, back_uz, back_markup, uz, get_categories_markup, admin_foods_markup, product_markup, admin_update_markup, admin_food_update_markup
from keyboards.inline.markup import yes_or_no_markup
from services.database.sql import get_categories, get_category_by_name_uz, add_product, get_products, get_product_by_name_uz, get_category_by_id, delete_product, update_product
from states.states import AdminMain, AdminProduct, AddProduct

@dp2.message_handler(text="Ovqatlar", state=AdminMain.menu)
async def admin_products_handler(message: types.Message):
    await message.delete()
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_foods_markup)
    await AdminProduct.step_one.set()

@dp2.message_handler(text="➕ Ovqat qo'shish", state=AdminProduct.step_one)
async def add_product_handler(message: types.Message):
    await message.delete()
    categories = db.execute(get_categories, fetchall=True)
    await message.answer(text='Yangi ovqat qo\'shish uchun kategoriyalardan birini tanlang!', reply_markup=get_categories_markup(categories, uz))
    await AddProduct.category.set()

@dp2.message_handler(lambda x: x.text in [category[1] for category in db.execute(get_categories, fetchall=True)], state=AddProduct.category)
async def name_uz_gandler(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.delete()
    await message.answer('Ovqatning 🇺🇿 O\'zbekcha nomini kiriting!', reply_markup=back_markup(uz))
    await AddProduct.name_uz.set()

@dp2.message_handler(state=AddProduct.name_uz)
async def name_ru_handler(message: types.Message, state: FSMContext):
    await state.update_data(name_uz=message.text)
    await message.delete()
    await message.answer('Endi ovqatning 🇷🇺 Ruscha nomini kiriting!', reply_markup=back_markup(uz))
    await AddProduct.name_ru.set()

@dp2.message_handler(state=AddProduct.name_ru)
async def description_uz_handler(message: types.Message, state: FSMContext):
    await state.update_data(name_ru=message.text)
    await message.delete()
    await message.answer('Endi ovqat haqida 🇺🇿 O\'zbekcha ma\'lumot kiriting!', reply_markup=back_markup(uz))
    await AddProduct.description_uz.set()

@dp2.message_handler(state=AddProduct.description_uz)
async def description_ru_handler(message: types.Message, state: FSMContext):
    await state.update_data(description_uz=message.text)
    await message.delete()
    await message.answer('Endi ovqat haqida 🇷🇺 Ruscha ma\'lumot kiriting!', reply_markup=back_markup(uz))
    await AddProduct.description_ru.set()

@dp2.message_handler(state=AddProduct.description_ru)
async def price_handler(message: types.Message, state: FSMContext):
    await state.update_data(description_ru=message.text)
    await message.delete()
    await message.answer('Endi ovqatning narxini kiriting! Masalan 34000 E\'tbor bering harf va belgilardan foydalanmang', reply_markup=back_markup(uz))
    await AddProduct.price.set()

@dp2.message_handler(state=AddProduct.price)
async def image_handler(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.delete()
    await message.answer('Endi ovqatning rasmini yuboring!', reply_markup=back_markup(uz))
    await AddProduct.image.set()

@dp2.message_handler(content_types=types.ContentType.PHOTO, state=AddProduct.image)
async def add_product_finish_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    category = data.get('category')
    name_uz = data.get('name_uz')
    name_ru = data.get('name_ru')
    description_uz = data.get('description_uz')
    description_ru = data.get('description_ru')
    price = data.get('price')
    image = message.photo[-1].file_id
    category_id = db.execute(get_category_by_name_uz, (category, ), fetchone=True)[0]
    await state.update_data(category_id=category_id)
    await state.update_data(image=image)
    await message.delete()
    answer = f"""
Kategoriya: {category}
🇺🇿 O'zbekcha nomi: {name_uz}
🇷🇺 Ruscha nomi: {name_ru}
🇺🇿 O'zbekcha ma'luot: {description_uz}
🇷🇺 Ruscha ma'lumot: {description_ru}
🤑 Narxi: {price} so'm
"""
    await message.answer_photo(photo=image, caption=answer, reply_markup=yes_or_no_markup)
    await AddProduct.check.set()

@dp2.callback_query_handler(state=AddProduct.check)
async def add_product_finish_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category = data.get('category')
    category_id = data.get('category_id')
    name_uz = data.get('name_uz')
    name_ru = data.get('name_ru')
    description_uz = data.get('description_uz')
    description_ru = data.get('description_ru')
    price = data.get('price')
    image = data.get('image')
    await callback.message.delete()
    answer = f"""
Kategoriya: {category}
🇺🇿 O'zbekcha nomi: {name_uz}
🇷🇺 Ruscha nomi: {name_ru}
🇺🇿 O'zbekcha ma'luot: {description_uz}
🇷🇺 Ruscha ma'lumot: {description_ru}
🤑 Narxi: {price} so'm
"""
    if callback.data == 'yes':
        try:
            db.execute(add_product, (category_id, name_uz, name_ru, description_uz, description_ru, price, image), commit=True)
            await callback.message.answer_photo(photo=image, caption=answer)
            await callback.message.answer('✅ Mahsulor qo\'shildi!')
        except:
            await callback.message.delete('❌ Nimadir xato ketdi qaytatdan urinib ko\'ring!')
    else:
        await callback.message.answer('❌ Ovaqt qo\'shilmadi!')
    await callback.message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()

@dp2.message_handler(text="Ovqatlarni ko'rish", state=AdminProduct.step_one)
async def get_products_handler(message: types.Message):
    products = db.execute(get_products, fetchall=True)
    await message.delete()
    await message.answer('Ovqatlardan birini tanlang!', reply_markup=product_markup(products, uz))
    await AdminProduct.choose.set()

@dp2.message_handler(lambda x: x.text in [product[2] for product in db.execute(get_products, fetchall=True)], state=AdminProduct.choose)
async def name_uz_gandler(message: types.Message, state: FSMContext):
    product = db.execute(get_product_by_name_uz, (message.text, ), fetchone=True)
    category = db.execute(get_category_by_id, (product[1],), fetchone=True)
    answer = f"""
Kategoriya: {category[1]}
🇺🇿 O'zbekcha nomi: {product[2]}
🇷🇺 Ruscha nomi: {product[3]}
🇺🇿 O'zbekcha ma'luot: {product[4]}
🇷🇺 Ruscha ma'lumot: {product[5]}
🤑 Narxi: {product[6]} so'm
"""
    await state.update_data(product_id=product[0])
    await message.delete()
    await message.answer_photo(photo=product[7], caption=answer)
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_update_markup)
    await AdminProduct.command.set()

@dp2.message_handler(text="🔴 O'chirish", state=AdminProduct.command)
async def delete_product_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    id = data.get('product_id')
    db.execute(delete_product, (id, ), commit=True)
    await message.delete()
    await message.answer("✅ Ovqat o'chirildi!")
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()

@dp2.message_handler(text="🟢 O'zgartirish", state=AdminProduct.command)
async def update_product_handler(message: types.Message):
    await message.delete()
    await message.answer('Ovqatni o\'zgartirish uchun buyruqlardan birini tanlang!', reply_markup=admin_food_update_markup)
    await AdminProduct.update.set()

@dp2.message_handler(text="🇺🇿 O'zbekcha nomni o'zgartirish", state=AdminProduct.update)
async def name_uz_handler(message: types.Message):
    await message.delete()
    await message.answer("🇺🇿 O'zbekcha nom kiriting!", reply_markup=back_markup(uz))
    await AdminProduct.name_uz.set()

@dp2.message_handler(text="🇷🇺 Ruscha nomni o'zgartirish", state=AdminProduct.update)
async def name_ru_handler(message: types.Message):
    await message.delete()
    await message.answer("🇷🇺 Ruscha nom kiriting!", reply_markup=back_markup(uz))
    await AdminProduct.name_ru.set()

@dp2.message_handler(text="🇺🇿 O'zbekcha ma'lumotni o'zgartirish", state=AdminProduct.update)
async def description_uz_hadnler(message: types.Message):
    await message.delete()
    await message.answer("🇺🇿 O'zbekcha ma'lumot kiriting!", reply_markup=back_markup(uz))
    await AdminProduct.description_uz.set()
    
@dp2.message_handler(text="🇷🇺 Ruscha ma'lumotni o'zgartirish", state=AdminProduct.update)
async def description_ru_handler(message: types.Message):
    await message.delete()
    await message.answer("🇷🇺 Ruscha ma'lumot kiriting!", reply_markup=back_markup(uz))
    await AdminProduct.description_ru.set()
    
@dp2.message_handler(text="🤑 Narxni o'zgartirish", state=AdminProduct.update)
async def price_handler(message: types.Message):
    await message.delete()
    await message.answer("🤑 Narx kiriting!", reply_markup=back_markup(uz))
    await AdminProduct.price.set()
    
@dp2.message_handler(text="🖼️ Rasmni o'zgartirish", state=AdminProduct.update)
async def image_handler(message: types.Message):
    await message.delete()
    await message.answer("🖼️ Rasm yuboring!", reply_markup=back_markup(uz))
    await AdminProduct.image.set()

@dp2.message_handler(state=AdminProduct.name_uz)
async def update_name_uz_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product_id = data.get('product_id')
    text = message.text
    sql = update_product('name_uz')
    db.execute(sql, (text, product_id), commit=True)
    await message.delete()
    await message.answer('✅ Mahsulot nomi o\'zgartirildi!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()


@dp2.message_handler(state=AdminProduct.name_ru)
async def update_name_uz_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product_id = data.get('product_id')
    text = message.text
    sql = update_product('name_ru')
    db.execute(sql, (text, product_id), commit=True)
    await message.delete()
    await message.answer('✅ Mahsulot nomi o\'zgartirildi!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()


@dp2.message_handler(state=AdminProduct.description_uz)
async def update_name_ru_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product_id = data.get('product_id')
    text = message.text
    sql = update_product('description_uz')
    db.execute(sql, (text, product_id), commit=True)
    await message.delete()
    await message.answer('✅ Mahsulot ma\'lumoti o\'zgartirildi!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()


@dp2.message_handler(state=AdminProduct.description_ru)
async def update_description_uz_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product_id = data.get('product_id')
    text = message.text
    sql = update_product('description_ru')
    db.execute(sql, (text, product_id), commit=True)
    await message.delete()
    await message.answer('✅ Mahsulot ma\'lumoti o\'zgartirildi!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()


@dp2.message_handler(state=AdminProduct.price)
async def update_description_ru_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product_id = data.get('product_id')
    text = message.text
    sql = update_product('price')
    db.execute(sql, (text, product_id), commit=True)
    await message.delete()
    await message.answer('✅ Mahsulot narxi o\'zgartirildi!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()


@dp2.message_handler(state=AdminProduct.price)
async def update_price_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product_id = data.get('product_id')
    text = message.text
    sql = update_product('price')
    await message.delete()
    try:
        db.execute(sql, (text, product_id), commit=True)
        await message.answer('✅ Mahsulot narxi o\'zgartirildi!')
    except:
        await message.answer('❌ Nimadir xato ketdi!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()
    
@dp2.message_handler(content_types=types.ContentType.PHOTO, state=AdminProduct.image)
async def update_image_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product_id = data.get('product_id')
    text = message.photo[-1].file_id
    sql = update_product('image')
    db.execute(sql, (text, product_id), commit=True)
    await message.delete()
    await message.answer('✅ Mahsulot rasmi o\'zgartirildi!')
    await message.answer('Buyruqlardan birini tanlang!', reply_markup=admin_menu_markup)
    await state.finish()
    