from aiogram import types
from aiogram.dispatcher import FSMContext
import os

from loader import dp, db
from keyboards.default.markup import delivery_or_pick_up_markup, uz, ru, back_markup, back_uz, back_ru, menu_markup
from keyboards.inline.markup import inline_category_markup, inline_food_markup, plus_minus_markup, food_callback, language_markup
from services.database.sql import check_user, get_categories, get_products_by_category, get_category_by_name, get_products, get_product_by_name_uz, get_product_by_name_ru, get_food_by_id, insert_cart, check_cart, delete_food_cart, update_count_cart, check_cart_empty
from states.states import UserMenu, Register

@dp.message_handler(text="🍽 Menyu")
@dp.message_handler(text="🍽 Меню")
async def menu_handler(message: types.Message):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    if user:
        lang = user[2]
        await message.delete()

        categories = db.execute(get_categories, fetchall=True)
        cart = db.execute(check_cart_empty, (message.from_user.id, ), fetchall=True)
        if cart:
            if lang == "uz":
                await message.answer('Kategoriyalardan birini tanlang!', reply_markup=back_markup(uz))
                await message.answer('Kategoriyalar', reply_markup=inline_category_markup(categories, uz))
            else:
                await message.answer('Выберите одну из категорий!', reply_markup=back_markup(ru))
                await message.answer('Категории', reply_markup=inline_category_markup(categories, ru))
            await UserMenu.category.set()
        else:
            if lang == "uz":
                await message.answer('Buyurtma qilish turini tanlang!', reply_markup=delivery_or_pick_up_markup(uz))
            else:
                await message.answer('Выберите тип заказа!', reply_markup=delivery_or_pick_up_markup(ru))
            await UserMenu.delivery_or_pick_up.set()
    else:
        answer = f"""
Assalomu alaykum <b>{message.from_user.first_name}</b>, men Milliy Mangal Botman.
Здравствуйте <b>{message.from_user.first_name}</b>, я Mangal Burger Bot.

Tilni tanlag!
Выберите язык!
    """
        await message.answer(text=answer, reply_markup=language_markup)
        await Register.lang.set()

@dp.message_handler(lambda x: x.text in [back_uz, back_ru], state=UserMenu.category)
@dp.message_handler(lambda x: x.text in [back_uz, back_ru], state=UserMenu.delivery_or_pick_up)
@dp.message_handler(lambda x: x.text in [back_uz, back_ru], state=UserMenu.food)
async def back_main_handler(message: types.Message, state: FSMContext):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    await message.delete()
    if lang == 'uz':
        await message.answer(f'Menyu', reply_markup=menu_markup(uz))
    else:
        await message.answer(f'Меню', reply_markup=menu_markup(ru))
    await state.finish()

@dp.message_handler(lambda x: x.text in ["🚚 Yetkazib berish", "🚶‍♂️ Olib ketish", "🚚 Доставка", "🚶‍♂️ Самовывоз"], state=UserMenu.delivery_or_pick_up)
async def delivery_or_pick_up_handler(message: types.Message, state: FSMContext):
    if message.text in ["🚚 Yetkazib berish", "🚚 Доставка"]:
        await state.update_data(delivery='delivery')
    else:
        await state.update_data(delivery='pick_up')
    await message.delete()
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    categories = db.execute(get_categories, fetchall=True)
    if lang == "uz":
        await message.answer('Kategoriyalardan birini tanlang!', reply_markup=back_markup(uz))
        await message.answer('Kategoriyalar', reply_markup=inline_category_markup(categories, uz))
    else:
        await message.answer('Выберите одну из категорий!', reply_markup=back_markup(ru))
        await message.answer('Категории', reply_markup=inline_category_markup(categories, ru))
    await UserMenu.category.set()

@dp.callback_query_handler(lambda x: x.data in [category[1] for category in db.execute(get_categories, fetchall=True)], state=UserMenu.category)
@dp.callback_query_handler(lambda x: x.data in [category[2] for category in db.execute(get_categories, fetchall=True)], state=UserMenu.category)
async def category_handler(callback: types.CallbackQuery, state: FSMContext):
    category_id = db.execute(get_category_by_name, (callback.data, callback.data), fetchone=True)[0]
    foods = db.execute(get_products_by_category, (category_id, ), fetchall=True)
    user = db.execute(check_user, (callback.from_user.id, ), fetchone=True)
    lang = user[2]
    if lang == "uz":
        await callback.message.edit_text('Ovqatlardan birini tanlang!', reply_markup=inline_food_markup(foods, uz))
    else:
        await callback.message.edit_text('Выберите одно из еды!', reply_markup=inline_food_markup(foods, ru))
    await state.update_data(category_id=category_id)
    await UserMenu.food.set()
    
@dp.callback_query_handler(lambda x: x.data in [back_uz, back_ru], state=UserMenu.food)
async def back_category_handler(callback: types.CallbackQuery, state: FSMContext):
    user = db.execute(check_user, (callback.from_user.id, ), fetchone=True)
    lang = user[2]
    categories = db.execute(get_categories, fetchall=True)
    if lang == "uz":
        await callback.message.edit_text('Kategoriyalar', reply_markup=inline_category_markup(categories, uz))
    else:
        await callback.message.edit_text('Категории', reply_markup=inline_category_markup(categories, ru))
    await UserMenu.category.set()

@dp.callback_query_handler(lambda x: x.data in [food[2] for food in db.execute(get_products, fetchall=True)], state=UserMenu.food)
@dp.callback_query_handler(lambda x: x.data in [food[3] for food in db.execute(get_products, fetchall=True)], state=UserMenu.food)
async def food_handler(callback: types.CallbackQuery, state: FSMContext):
    user = db.execute(check_user, (callback.from_user.id, ), fetchone=True)
    lang = user[2]
    await callback.message.delete()
    if lang == "uz":
        food = db.execute(get_product_by_name_uz, (callback.data, ), fetchone=True)
        cart = db.execute(check_cart, (callback.from_user.id, food[0]), fetchone=True)
        path = f"photos/{food[7]}.jpg"

        if not cart:
            answer = f"""
{food[2]}

{food[4]}
{food[6]} so'm
        """
            with open(path, 'rb') as photo_file:
                await callback.message.answer_photo(photo=photo_file, caption=answer, reply_markup=plus_minus_markup(uz, food[0], food[6], 1))
        else:
            answer = f"""
{food[2]}

{food[4]}
{food[6] * cart[3]} so'm
        """
            await state.update_data(cart='yes')
            with open(path, 'rb') as photo_file:
                await callback.message.answer_photo(photo=photo_file, caption=answer, reply_markup=plus_minus_markup(uz, food[0], food[6], cart[3], cart))
    else:
        food = db.execute(get_product_by_name_ru, (callback.data, ), fetchone=True)
        cart = db.execute(check_cart, (callback.from_user.id, food[0]), fetchone=True)
        path = f"photos/{food[7]}.jpg"

        if not cart:
            answer = f"""
{food[2]}

{food[4]}
{food[6]} сум
        """
            with open(path, 'rb') as photo_file:
                await callback.message.answer_photo(photo=photo_file, caption=answer, reply_markup=plus_minus_markup(ru, food[0], food[6], 1))
        else:
            answer = f"""
{food[2]}

{food[4]}
{food[6] * cart[3]} сум
        """
            await state.update_data(cart='yes')
            with open(path, 'rb') as photo_file:
                await callback.message.answer_photo(photo=photo_file, caption=answer, reply_markup=plus_minus_markup(ru, food[0], food[6], cart[3], cart))
    data = await state.get_data()
    await state.update_data(delivery=data.get('delivery'))
    await UserMenu.plus_minus.set()

@dp.callback_query_handler(food_callback.filter(), state=UserMenu.plus_minus)
async def plus_minus_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    data = await state.get_data()
    cart = data.get('cart', None)
    action = callback_data['action']
    food_id = callback_data['food_id']
    price = callback_data['price']
    count = int(callback_data['count'])
    lang = callback_data['lang']
    food = db.execute(get_food_by_id, (food_id, ), fetchone=True)
    
    if action == 'plus':
        count += 1
        if lang == uz:
            answer = f"""
{food[2]}

{food[4]}
{food[6] * count} so'm
"""
        else:
            answer = f"""
{food[3]}

{food[5]}
{food[6] * count} сум
"""     
        if cart:
            db.execute(update_count_cart, (count, callback.from_user.id, food_id), commit=True)
        await callback.message.edit_caption(caption=answer, reply_markup=plus_minus_markup(lang, food_id, price, count, cart))
    elif action == 'minus':
        if count > 1:
            count -= 1
            if lang == uz:
                answer = f"""
{food[2]}

{food[4]}
{food[6] * count} so'm
"""
            else:
                answer = f"""
{food[3]}

{food[5]}
{food[6] * count} сум
"""
            if cart:
                db.execute(update_count_cart, (count, callback.from_user.id, food_id), commit=True)
            await callback.message.edit_caption(caption=answer, reply_markup=plus_minus_markup(lang, food_id, price, count, cart))
        else:
            if cart:
                db.execute(delete_food_cart, (callback.from_user.id, food_id), commit=True)
                data = await state.get_data()
                category_id = data.get('category_id')
                foods = db.execute(get_products_by_category, (category_id, ), fetchall=True)
                await callback.message.delete()
                if lang == "uz":
                    await callback.message.answer('Ovqatlardan birini tanlang!', reply_markup=inline_food_markup(foods, uz))
                else:
                    await callback.message.answer('Выберите одно из еды!', reply_markup=inline_food_markup(foods, ru))
                await UserMenu.food.set()
            else:
                await callback.answer('Minimum 1')
    elif action == 'count':
        await callback.answer(str(count))
    elif action == 'cart':
        data = await state.get_data()
        delivery_type = data.get('delivery', None)
        if delivery_type:
            db.execute(insert_cart, (callback.from_user.id, food_id, count, delivery_type), commit=True)
        else:
            cart = db.execute(check_cart_empty, (callback.from_user.id, ), fetchall=True)
            delivery_type = cart[0][4]
            db.execute(insert_cart, (callback.from_user.id, food_id, count, delivery_type), commit=True)
        category_id = data.get('category_id')
        foods = db.execute(get_products_by_category, (category_id, ), fetchall=True)
        await callback.message.delete()
        if lang == "uz":
            await callback.message.answer('Ovqatlardan birini tanlang!', reply_markup=inline_food_markup(foods, uz))
        else:
            await callback.message.answer('Выберите одно из еды!', reply_markup=inline_food_markup(foods, ru))
        await state.update_data(delivery=data.get('delivery'))
        await UserMenu.food.set()
    elif action == 'delete':
        db.execute(delete_food_cart, (callback.from_user.id, food_id), commit=True)
        data = await state.get_data()
        category_id = data.get('category_id')
        foods = db.execute(get_products_by_category, (category_id, ), fetchall=True)
        await callback.message.delete()
        if lang == "uz":
            await callback.message.answer('Ovqatlardan birini tanlang!', reply_markup=inline_food_markup(foods, uz))
        else:
            await callback.message.answer('Выберите одно из еды!', reply_markup=inline_food_markup(foods, ru))
        await state.update_data(delivery=data.get('delivery'))
        await UserMenu.food.set()
    
    await callback.answer()

@dp.message_handler(lambda x: x.text in [back_uz, back_ru], state=UserMenu.plus_minus)
async def back_food_handler(message: types.Message, state: FSMContext):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    data = await state.get_data()
    category_id = data.get('category_id')
    foods = db.execute(get_products_by_category, (category_id, ), fetchall=True)
    await message.delete()
    if lang == "uz":
        await message.answer('Ovqatlardan birini tanlang!', reply_markup=inline_food_markup(foods, uz))
    else:
        await message.answer('Выберите одно из еды!', reply_markup=inline_food_markup(foods, ru))
    await UserMenu.food.set()