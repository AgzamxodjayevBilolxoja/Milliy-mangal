from aiogram import types
from aiogram.dispatcher import FSMContext
import requests
import math
import os

from loader import dp, db, bot2, bot
from keyboards.default.markup import delivery_or_pick_up_markup, uz, ru, back_markup, back_uz, back_ru, menu_markup, cart_markup, correct_delivery_markup, location_markup, delivery_or_pick_up_markup, buy_markup,yes_or_no_markup, remove_keyboard
from keyboards.inline.markup import cart_plus_minus_markup, cart_callback, chef_yes_or_no_markup, chef_return_markup, chef_return_delivery_markup
from services.database.sql import check_user, check_cart_empty, get_food_by_id, update_count_cart, delete_food_cart, clean_cart, update_delivery_type, get_branches, get_chef_by_branch, create_order, create_order_items, get_last_order
from states.states import Cart

async def is_tashkent_city_api(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "json",
        "lat": lat,
        "lon": lon,
        "zoom": 10,
        "addressdetails": 1,
    }

    headers = {
        "User-Agent": "milliy_mangal_bot/1.0 (agzamxodjayevbilolxoja@gmail.com)"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        address = data.get("address", {})

        city = address.get("city", "") or address.get("town", "") or address.get("village", "")
        state = address.get("state", "")
        if city and city == 'Toshkent':
            return True
        if state and state == 'Toshkent':
            return True

        return False

    except Exception as e:
        print("API xatosi:", e)
        return False


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def get_closest_branch(user_lat, user_lon, branches):
    closest = None
    min_distance = float('inf')

    for branch in branches:
        branch_lat = branch[1]
        branch_lon = branch[2]
        distance = calculate_distance(user_lat, user_lon, branch_lat, branch_lon)
        if distance < min_distance:
            min_distance = distance
            closest = branch

    return closest, min_distance

@dp.message_handler(lambda x: x.text in ["🛒 Savatcham", "🛒 Корзинка"])
async def cart_handler(message: types.Message):
    await message.delete()
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    cart = db.execute(check_cart_empty, (message.from_user.id,),fetchall=True)
    if lang == 'uz':
        if cart:
            answer = ""
            price = 0
            for cart_item in cart:
                food = db.execute(get_food_by_id, (cart_item[2],), fetchone=True)
                answer += f"{food[2]} ----- {cart_item[3]} ta ----- {food[6] * cart_item[3]} so'm\n"
                price += food[6] * cart_item[3]
            answer += f"\nJami: {price}"
            await message.answer(text="🛒 Savatcha", reply_markup=cart_markup(uz))
            await message.answer(answer, reply_markup=cart_plus_minus_markup(uz, cart, get_food_by_id))
            await Cart.step_one.set()
        else:
            await message.answer('🛒 Savatcha bo\'sh!', reply_markup=menu_markup(uz))
    else:
        if cart:
            answer = ""
            price = 0
            for cart_item in cart:
                food = db.execute(get_food_by_id, (cart_item[2],), fetchone=True)
                answer += f"{food[3]} ----- {cart_item[3]} шт. ----- {food[6] * cart_item[3]} сум\n"
                price += food[6] * cart_item[3]
            answer += f"\nВсего: {price}"
            await message.answer(text="🛒 Корзина", reply_markup=cart_markup(ru))
            await message.answer(answer, reply_markup=cart_plus_minus_markup(ru, cart, get_food_by_id))
            await Cart.step_one.set()
        else:
            await message.answer('🛒 Корзина пуста!', reply_markup=menu_markup(ru))

@dp.callback_query_handler(cart_callback.filter(), state=Cart.step_one)
async def plus_minus_handler(callback: types.CallbackQuery, callback_data: dict):
    action = callback_data['action']
    lang = callback_data['lang']
    food_id = callback_data['food_id']
    count = int(callback_data['count'])
    
    food = db.execute(get_food_by_id, (food_id, ), fetchone=True)
    if action == 'name':
        if lang == uz:
            await callback.answer(food[2])
        else:
            await callback.answer(food[3])
    elif action == 'count':
        await callback.answer(str(count))
    elif action == 'plus':
        count += 1
        db.execute(update_count_cart, (count, callback.from_user.id, food_id), commit=True)
        cart = db.execute(check_cart_empty, (callback.from_user.id,),fetchall=True)
        if lang == uz:
            answer = ""
            price = 0
            for cart_item in cart:
                food = db.execute(get_food_by_id, (cart_item[2],), fetchone=True)
                answer += f"{food[2]} ----- {cart_item[3]} ta ----- {food[6] * cart_item[3]} so'm\n"
                price += food[6] * cart_item[3]
            answer += f"\nJami: {price}"
            await callback.message.edit_text(answer, reply_markup=cart_plus_minus_markup(uz, cart, get_food_by_id))
            await Cart.step_one.set()
        else:
            answer = ""
            price = 0
            for cart_item in cart:
                food = db.execute(get_food_by_id, (cart_item[2],), fetchone=True)
                answer += f"{food[3]} ----- {cart_item[3]} шт. ----- {food[6] * cart_item[3]} сум\n"
                price += food[6] * cart_item[3]
            answer += f"\nВсего: {price}"
            await callback.message.edit_text(answer, reply_markup=cart_plus_minus_markup(ru, cart, get_food_by_id))
            await Cart.step_one.set()
    elif action == "minus":
        if count > 1:
            count -= 1
            db.execute(update_count_cart, (count, callback.from_user.id, food_id), commit=True)
            cart = db.execute(check_cart_empty, (callback.from_user.id,),fetchall=True)
            if lang == uz:
                answer = ""
                price = 0
                for cart_item in cart:
                    food = db.execute(get_food_by_id, (cart_item[2],), fetchone=True)
                    answer += f"{food[2]} ----- {cart_item[3]} ta ----- {food[6] * cart_item[3]} so'm\n"
                    price += food[6] * cart_item[3]
                answer += f"\nJami: {price}"
                await callback.message.edit_text(answer, reply_markup=cart_plus_minus_markup(uz, cart, get_food_by_id))
                await Cart.step_one.set()
            else:
                answer = ""
                price = 0
                for cart_item in cart:
                    food = db.execute(get_food_by_id, (cart_item[2],), fetchone=True)
                    answer += f"{food[3]} ----- {cart_item[3]} шт. ----- {food[6] * cart_item[3]} сум\n"
                    price += food[6] * cart_item[3]
                answer += f"\nВсего: {price}"
                await callback.message.edit_text(answer, reply_markup=cart_plus_minus_markup(ru, cart, get_food_by_id))
                await Cart.step_one.set()
        else:
            db.execute(delete_food_cart, (callback.from_user.id, food_id), commit=True)
            cart = db.execute(check_cart_empty, (callback.from_user.id,),fetchall=True)
            if lang == uz:
                if cart:
                    answer = ""
                    price = 0
                    for cart_item in cart:
                        food = db.execute(get_food_by_id, (cart_item[2],), fetchone=True)
                        answer += f"{food[2]} ----- {cart_item[3]} ta ----- {food[6] * cart_item[3]} so'm\n"
                        price += food[6] * cart_item[3]
                    answer += f"\nJami: {price}"
                    await callback.message.edit_text(answer, reply_markup=cart_plus_minus_markup(uz, cart, get_food_by_id))
                    await Cart.step_one.set()
                else:
                    await callback.message.delete()
                    await callback.message.answer('🛒 Savatcha bo\'sh!', reply_markup=menu_markup(uz))
            else:
                if cart:
                    answer = ""
                    price = 0
                    for cart_item in cart:
                        food = db.execute(get_food_by_id, (cart_item[2],), fetchone=True)
                        answer += f"{food[3]} ----- {cart_item[3]} шт. ----- {food[6] * cart_item[3]} сум\n"
                        price += food[6] * cart_item[3]
                    answer += f"\nВсего: {price}"
                    await callback.message.edit_text(answer, reply_markup=cart_plus_minus_markup(ru, cart, get_food_by_id))
                    await Cart.step_one.set()
                else:
                    await callback.message.delete()
                    await callback.message.answer('🛒 Корзина пуста!', reply_markup=menu_markup(ru))
    elif action == 'remove':
        db.execute(delete_food_cart, (callback.from_user.id, food_id), commit=True)
        cart = db.execute(check_cart_empty, (callback.from_user.id,),fetchall=True)
        if lang == uz:
            if cart:
                answer = ""
                price = 0
                for cart_item in cart:
                    food = db.execute(get_food_by_id, (cart_item[2],), fetchone=True)
                    answer += f"{food[2]} ----- {cart_item[3]} ta ----- {food[6] * cart_item[3]} so'm\n"
                    price += food[6] * cart_item[3]
                answer += f"\nJami: {price}"
                await callback.message.edit_text(answer, reply_markup=cart_plus_minus_markup(uz, cart, get_food_by_id))
                await Cart.step_one.set()
            else:
                await callback.message.delete()
                await callback.message.answer('🛒 Savatcha bo\'sh!', reply_markup=menu_markup(uz))
        else:
            if cart:
                answer = ""
                price = 0
                for cart_item in cart:
                    food = db.execute(get_food_by_id, (cart_item[2],), fetchone=True)
                    answer += f"{food[3]} ----- {cart_item[3]} шт. ----- {food[6] * cart_item[3]} сум\n"
                    price += food[6] * cart_item[3]
                answer += f"\nВсего: {price}"
                await callback.message.edit_text(answer, reply_markup=cart_plus_minus_markup(ru, cart, get_food_by_id))
                await Cart.step_one.set()
            else:
                await callback.message.delete()
                await callback.message.answer('🛒 Корзина пуста!', reply_markup=menu_markup(ru))

@dp.message_handler(text=back_uz, state=Cart.step_one)
@dp.message_handler(text=back_ru, state=Cart.step_one)
async def back_main_handler(message: types.Message, state: FSMContext):
    await message.delete()
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    
    if lang == 'uz':
        await message.answer('Menyu', reply_markup=menu_markup(uz))
    else:
        await message.answer('Меню', reply_markup=menu_markup(ru))
    await state.finish()

@dp.message_handler(text="🛒 Savatni tozalash", state=Cart.step_one)
@dp.message_handler(text="🛒 Очистить корзину", state=Cart.step_one)
async def clean_cart_handler(message: types.Message, state: FSMContext):
    db.execute(clean_cart, (message.from_user.id, ), commit=True)
    await message.delete()
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    
    if lang == 'uz':
        await message.answer('🗑️ Tozalandi')
        await message.answer('Menyu', reply_markup=menu_markup(uz))
    else:
        await message.answer('🗑️ Очистена')
        await message.answer('Меню', reply_markup=menu_markup(ru))
    await state.finish()

@dp.message_handler(text="📲 Buyurtma berish", state=Cart.step_one)
@dp.message_handler(text="📲 Сделать заказ", state=Cart.step_one)
async def order_handler(message: types.Message):
    await message.delete()
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    
    cart = db.execute(check_cart_empty, (message.from_user.id,),fetchall=True)
    if lang == 'uz':
        if cart[0][4] == 'delivery':
            await message.answer("Buyurtma turi: 🚚 Yetkazib berish\nTo'grimi?", reply_markup=correct_delivery_markup(uz))
        else:
            await message.answer("Buyurtma turi: 🚶‍♂️ Olib ketish\nTo'grimi?", reply_markup=correct_delivery_markup(uz))
    else:
        if cart[0][4] == 'delivery':
            await message.answer("Тип заказа: 🚚 Доставка\nВерно?", reply_markup=correct_delivery_markup(ru))
        else:
            await message.answer("Тип заказа: 🚶‍♂️ Самовывоз\nВерно?", reply_markup=correct_delivery_markup(ru))
    await Cart.delivery.set()

@dp.message_handler(lambda x: x.text in ['✅ Ha', '✅ Да'], state=Cart.delivery)
async def yes_handler(message: types.Message):
    await message.delete()
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]

    if lang == 'uz':
        await message.answer("O'z joylashuvingizni yuboring", reply_markup=location_markup(uz))
    else:
        await message.answer("Отправте свое место положение", reply_markup=location_markup(ru))
    await Cart.location.set()

@dp.message_handler(lambda x: x.text in [back_uz, back_ru], state=Cart.delivery)
async def back_handler(message: types.Message, state: FSMContext):
    await message.delete()
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]

    if lang == 'uz':
         await message.answer("Menyu", reply_markup=menu_markup(uz))
    else:
        await message.answer('Меню', reply_markup=menu_markup(ru))
    await state.finish()

@dp.message_handler(lambda x: x.text in ["🟠 O'zgartirish", "🟠 Изменить"], state=Cart.delivery)
async def delivery_handler(message: types.Message):
    await message.delete()
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]

    if lang == 'uz':
        await message.answer('Buyurtma qilish turini tanlang!', reply_markup=delivery_or_pick_up_markup(uz))
    else:
        await message.answer('Выберите тип заказа!', reply_markup=delivery_or_pick_up_markup(ru))
    await Cart.set_delivery.set()

@dp.message_handler(lambda x: x.text in [back_uz, back_ru, '❌ Yo\'q', '❌ Нет'], state=Cart.yes_or_no)
@dp.message_handler(lambda x: x.text in [back_uz, back_ru], state=Cart.buy)
@dp.message_handler(lambda x: x.text in [back_uz, back_ru], state=Cart.card)
@dp.message_handler(lambda x: x.text in [back_uz, back_ru], state=Cart.location)
@dp.message_handler(lambda x: x.text in [back_uz, back_ru], state=Cart.set_delivery)
async def back_handler(message: types.Message, state: FSMContext):
    await message.delete()
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]

    if lang == 'uz':
         await message.answer("Menyu", reply_markup=menu_markup(uz))
    else:
        await message.answer('Меню', reply_markup=menu_markup(ru))
    await state.finish()


@dp.message_handler(lambda x: x.text in ["🚚 Yetkazib berish", "🚶‍♂️ Olib ketish", "🚚 Доставка", "🚶‍♂️ Самовывоз"], state=Cart.set_delivery)
async def delivery_or_pick_up_handler(message: types.Message, state: FSMContext):
    if message.text in ["🚚 Yetkazib berish", "🚚 Доставка"]:
        db.execute(update_delivery_type, ('delivery', message.from_user.id), commit=True)
    else:
        db.execute(update_delivery_type, ('pick_up', message.from_user.id), commit=True)
    await message.delete()
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    if lang == 'uz':
        await message.answer("O'z joylashuvingizni yuboring", reply_markup=location_markup(uz))
    else:
        await message.answer("Отправте свое место положение", reply_markup=location_markup(ru))
    await Cart.location.set()

@dp.message_handler(content_types=types.ContentType.LOCATION, state=Cart.location)
async def location_handler(message: types.Message, state: FSMContext):
    await message.delete()
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    latitude = message.location.latitude
    longitude = message.location.longitude
    cart = db.execute(check_cart_empty, (message.from_user.id, ), fetchall=True)
    
    is_tashkent = await is_tashkent_city_api(latitude, longitude)
    delivery_type = cart[0][4]
    price = 0
    for cart_item in cart:
        food = db.execute(get_food_by_id, (cart_item[2], ), fetchone=True)
        price += int(food[6])
    branches = db.execute(get_branches, fetchall=True)
    closest_branch, distance = get_closest_branch(latitude, longitude, branches)
    await state.update_data(closest_branch=closest_branch)
    await state.update_data(latitude=latitude)
    await state.update_data(longitude=longitude)
    if lang == 'uz':
        answer = f"Jami narx: {price} so'm bo'ldi"
        if delivery_type == 'delivery':
            if is_tashkent:
                answer += "\nYetkazib berish xizmati uchun esa yana 30000 so'm qo'shiladi."
                await message.answer(answer)
            else:
                answer += "\nYetkazib berish xizmati uchun esa yana 30000 so'm + (kelishiladi) qo'shiladi."
                await message.answer(answer)
        else:
            text = f"""
🏢 Eng yaqin filial:
📍 Nomi: {closest_branch[3]}
🕒 Ish vaqti: {closest_branch[4]}
📏 Masofa: {distance:.2f} km"""
            await message.answer(answer)
            await message.answer(text)
            await message.answer_location(closest_branch[1], closest_branch[2] )
        await message.answer("To'lov turini tanlang!", reply_markup=buy_markup(uz))
    else:
        answer = f"Общая цена: {price} сум"
        if delivery_type == 'delivery':
            if is_tashkent:
                answer += "\nЕще 30 000 сум будет добавлено за доставку."
                await message.answer(answer)
            else:
                answer += "\nЗа доставку дополнительно будет добавлено 30 000 сум + (договорная)."
                await message.answer(answer)
        else:
            text = f"""
🏢 Ближайший филиал:
📍 Имя: {closest_branch[3]}
🕒 Время работы: {closest_branch[4]}
📏 Расстояние: {distance:.2f} km"""
            await message.answer(answer)
            await message.answer(text)
            await message.answer_location(closest_branch[1], closest_branch[2])
        await message.answer("Выберите способ оплаты!", reply_markup=buy_markup(ru))
    await Cart.buy.set()

@dp.message_handler(lambda x: x.text in ["💵 Naqd to'lov", "💵 Оплата наличными"], state=Cart.buy)
async def cash_handler(message: types.Message):
    await message.delete()
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    if lang == 'uz':
        await message.answer('Haqiqatan ham buyurtma berasizmi?', reply_markup=yes_or_no_markup(uz))
    else:
        await message.answer('Вы действительно заказываете?', reply_markup=yes_or_no_markup(ru))
    await Cart.yes_or_no.set()

@dp.message_handler(lambda x: x.text in ['✅ Ha', '✅ Да'], state=Cart.yes_or_no)
async def yes_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    branch = data.get('closest_branch')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    cart = db.execute(check_cart_empty, (message.from_user.id, ), fetchall=True)
    chef = db.execute(get_chef_by_branch, (branch[0], ), fetchone=True)
    
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    
    db.execute(create_order, (message.from_user.id, latitude, longitude, False), commit=True)
    order = db.execute(get_last_order, (message.from_user.id, ), fetchone=True)
    answer = "🆕 Yangi buyurtma\n\n"
    price = 0
    for cart_item in cart:
        food = db.execute(get_food_by_id, (cart_item[2],), fetchone=True)
        answer += f"{food[2]} ----- {cart_item[3]} ta ----- {food[6] * cart_item[3]} so'm\n"
        price += food[6] * cart_item[3]
        db.execute(create_order_items, (order[0], food[0], cart_item[3]), commit=True)
    answer += f"\nJami: {price}\n\n👤 Buyurtma oluvchi ismi: {user[4]}\n📱 Telefon raqami: {user[3]}"

    db.execute(clean_cart, (message.from_user.id, ), commit=True)
    
    if cart[0][4] == 'delivery':
        answer += f"\nBuyurtma turi: 🚚 Yetkazib berish\nQabul qilasizmi?"
        await bot2.send_message(chat_id=chef[1], text=answer, reply_markup=chef_return_delivery_markup(message.from_user.id))
    else:
        answer += f"\nBuyurtma turi: 🚶‍♂️ Olib ketish"
        await bot2.send_message(chat_id=chef[1], text=answer, reply_markup=chef_return_markup(message.from_user.id))
    
    await message.delete()
    
    if lang == 'uz':
        await message.answer('Qabul qilindi!')
        await message.answer("Esingizdan chiqmasin, buyurtmani olishda ismingizni va telefon raqamingizni aytishni unitmang!")
        await message.answer("Menyu", reply_markup=menu_markup(uz))
    else:
        await message.answer("Принята!")
        await message.answer("Не забудьте сказать свое имя и номер телефона при получении заказа!")
        await message.answer("Меню", reply_markup=menu_markup(ru))
    await state.finish()

@dp.message_handler(lambda x: x.text in ['💳 Karta orqali', '💳 Картой'], state=Cart.buy)
async def card_handler(message: types.Message):
    await message.delete()
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    price = 0
    cart = db.execute(check_cart_empty, (message.from_user.id, ), fetchall=True)
    delivery_type = ""
    for cart_item in cart:
        food = db.execute(get_food_by_id, (cart_item[2],), fetchone=True)
        delivery_type = food[4]
        price += food[6] * cart_item[3]
    if lang == 'uz':
        await message.answer(f'Shu karta raqamiga {price} so\'m pul tashlang!', reply_markup=back_markup(uz))
        if delivery_type == 'delivery':
            await message.answer('Esingizdan chiqmasin yetkazib berish uchun yana 30000 so\'m + naqd pul to\'aysiz')
    else:
        await message.answer(f'Оплатите {price} сум к этому номеру карты!', reply_markup=back_markup(ru))
        if delivery_type == 'delivery':
            await message.answer('Не забудьте, вы заплатите еще 30 000 сум + наличные за доставку.')
    await Cart.card.set()

@dp.message_handler(content_types=types.ContentType.PHOTO, state=Cart.card)
async def check_photo_handler(message: types.Message, state: FSMContext):
    await message.delete()
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    data = await state.get_data()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    branch = data.get('closest_branch')
    chef = db.execute(get_chef_by_branch, (branch[0], ), fetchone=True)
    cart = db.execute(check_cart_empty, (message.from_user.id, ), fetchall=True)
    answer = "🆕 Yangi buyurtma\n\n"
    price = 0
    for cart_item in cart:
        food = db.execute(get_food_by_id, (cart_item[2],), fetchone=True)
        answer += f"{food[2]} ----- {cart_item[3]} ta ----- {food[6] * cart_item[3]} so'm\n"
        price += food[6] * cart_item[3]
    answer += f"\nJami: {price}\n\n👤 Buyurtma oluvchi ismi: {user[4]}\n📱 Telefon raqami: {user[3]}"
    if cart[0][4] == 'delivery':
        answer += f"\nBuyurtma turi: 🚚 Yetkazib berish\nQabul qilasizmi?"
    else:
        answer += f"\nBuyurtma turi: 🚶‍♂️ Olib ketish"
    answer += "\nTo'lov to'g'ri qilinganmi?"
    file = await bot.get_file(message.photo[-1].file_id)
    file_path = file.file_path

    filename = f"{message.photo[-1].file_id}.jpg"
    destination_path = f"photos/{filename}"
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)

    await bot.download_file(file_path, destination_path)

    with open(destination_path, 'rb') as photo_file:
        await bot2.send_photo(
            chat_id=chef[1],
            photo=photo_file,
            caption=answer,
            reply_markup=chef_yes_or_no_markup(user[0], latitude, longitude)
        )

    os.remove(destination_path)

    if lang == 'uz':
        await message.answer("🕑 To'lov tekshirilmoqda biroz kutib turing!", reply_markup=remove_keyboard)
    else:
        await message.answer("🕑 Платеж проверяется, пожалуйста, подождите немного!", reply_markup=remove_keyboard)
        