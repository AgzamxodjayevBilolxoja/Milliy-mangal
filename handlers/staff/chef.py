from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp2, bot, db, bot2
from keyboards.inline.markup import order_callback, chef_return_callback, chef_return_delivery_callback, delivermen_markup, delivermen_callback, chef_return_delivery_markup, chef_return_markup
from services.database.sql import check_staff_by_chat_id, clean_cart, create_order, get_last_order, create_order_items, check_cart_empty, get_food_by_id, get_user_by_id, delete_order_items, delete_order, get_staff, update_status, check_user, get_order_items

@dp2.callback_query_handler(order_callback.filter())
async def yes_or_no_handler(callback: types.CallbackQuery, callback_data: dict):
    chef = db.execute(check_staff_by_chat_id, (callback.from_user.id, ), fetchone=True)
    if chef:
        role = chef[2]
        if role == "Chef":
            action = callback_data['action']
            id = callback_data['user_id']
            user_id = db.execute(get_user_by_id, (id, ), fetchone=True)[1]
            latitude = callback_data['latitude']
            longitude = callback_data['longitude']
            if action == "yes":
                cart = db.execute(check_cart_empty, (user_id, ), fetchall=True)
                db.execute(create_order, (user_id, latitude, longitude, False), commit=True)
                order = db.execute(get_last_order, (user_id, ), fetchone=True)
                for cart_item in cart:
                    food = db.execute(get_food_by_id, (cart_item[2],), fetchone=True)
                    db.execute(create_order_items, (order[0], food[0], cart_item[3]), commit=True)
                db.execute(clean_cart, (user_id, ), commit=True)
                await bot.send_message(chat_id=user_id, text="✅ Qabul qilindi!\n✅ Принята!")
                if cart[0][4] == 'delivery':
                    await callback.message.edit_reply_markup(reply_markup=chef_return_delivery_markup(user_id, 'card'))
                else:
                    await callback.message.edit_reply_markup(reply_markup=chef_return_markup(user_id))
            else:
                await bot.send_message(chat_id=user_id, text="❌ Qabul qilinmadi!\n❌ Не принята!")
                
        else:
            await callback.answer('Sizda bu buyruq uchun ruxsat yo\'q!')
            await callback.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')
    else:
        await callback.answer('Sizda bu buyruq uchun ruxsat yo\'q!')
        await callback.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')

# pick_up

@dp2.callback_query_handler(chef_return_callback.filter())
async def no_or_finish_handler(callback: types.CallbackQuery, callback_data: dict):
    chef = db.execute(check_staff_by_chat_id, (callback.from_user.id, ), fetchone=True)
    if chef:
        role = chef[2]
        if role == "Chef":
            action = callback_data['action']
            user_chat_id = callback_data['chat_id']
            if action == 'no':
                order = db.execute(get_last_order, (user_chat_id, ), fetchone=True)
                db.execute(delete_order_items, (order[0],), commit=True)
                db.execute(delete_order, (order[0], ), commit=True)
                await bot.send_message(chat_id=user_chat_id, text="❌ Qabul qilinmadi!\n❌ Не принята!")
            else:
                user = db.execute(check_user, (user_chat_id, ), fetchone=True)
                db.execute(update_status, (True, user[0]), commit=True)
                await bot.send_message(chat_id=user_chat_id, text="✅ Tayyor!\n✅ Готова!")
        else:
            await callback.answer('Sizda bu buyruq uchun ruxsat yo\'q!')
            await callback.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')
    else:
        await callback.answer('Sizda bu buyruq uchun ruxsat yo\'q!')
        await callback.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')

# delivery

@dp2.callback_query_handler(chef_return_delivery_callback.filter())
async def no_or_delivery_handler(callback: types.CallbackQuery, callback_data: dict):
    chef = db.execute(check_staff_by_chat_id, (callback.from_user.id, ), fetchone=True)
    if chef:
        role = chef[2]
        if role == "Chef":
            action = callback_data['action2']
            user_chat_id = callback_data['chat_id']
            buy_type = callback_data['buy_type']
            order = db.execute(get_last_order, (user_chat_id, ), fetchone=True)
            if action == 'no':
                db.execute(delete_order_items, (order[0],), commit=True)
                db.execute(delete_order, (order[0], ), commit=True)
                await bot.send_message(chat_id=user_chat_id, text="❌ Qabul qilinmadi!\n❌ Не принята!")
                await callback.message.delete()
            elif action == 'next':
                delivermen = db.execute(get_staff, ('Deliverman', ), fetchall=True)
                if not delivermen:
                    await bot.send_message(chat_id=user_chat_id, text="❌ Qabul qilinmadi!\n❌ Не принята!")
                    await callback.message.delete()
                else:
                    if len(delivermen) > 1:
                        await callback.message.edit_reply_markup(reply_markup=delivermen_markup(delivermen, user_chat_id, buy_type))
                    else:
                        await callback.message.delete()
                        await callback.message.answer(callback.message.text)
                        text = callback.message.text
                        if buy_type == 'card':
                            text += '\nTo\'angan'
                        await bot2.send_message(chat_id=delivermen[0][1], text=callback.message.text)
                        await bot2.send_location(chat_id=delivermen[0][1], latitude=order[2], longitude=order[3])
                        await bot.send_message(chat_id=user_chat_id, text="▶️ Yetkazilmoqda!\n▶️ Yetkazilmoqda!")
                
        else:
            await callback.answer('Sizda bu buyruq uchun ruxsat yo\'q!')
            await callback.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')
    else:
        await callback.answer('Sizda bu buyruq uchun ruxsat yo\'q!')
        await callback.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')

@dp2.callback_query_handler(delivermen_callback.filter())
async def deliverman_handler(callback: types.CallbackQuery, callback_data: dict):
    chef = db.execute(check_staff_by_chat_id, (callback.from_user.id, ), fetchone=True)
    if chef:
        role = chef[2]
        if role == "Chef":
            deliverman_chat_id = callback_data['chat_id']
            user_chat_id = callback_data['user_chat_id']
            buy_type = callback_data['buy_type']
            answer = "🆕 Yangi buyurtma\n\n"
            price = 0
            order = db.execute(get_last_order, (user_chat_id, ), fetchone=True)
            order_items = db.execute(get_order_items, (order[0],), fetchall=True)
            user = db.execute(check_user, (user_chat_id, ), fetchone=True)
            for order_item in order_items:
                food = db.execute(get_food_by_id, (order_item[2],), fetchone=True)
                answer += f"{food[2]} ----- {order_item[3]} ta ----- {food[6] * order_item[3]} so'm\n"
                price += food[6] * order_item[3]
                answer += f"\nJami: {price}\n\n👤 Buyurtma oluvchi ismi: {user[4]}\n📱 Telefon raqami: {user[3]}"
            if buy_type == 'card':
                answer += '\nTo\'angan'
            await bot2.send_message(chat_id=int(deliverman_chat_id), text=answer)
            await bot2.send_location(chat_id=int(deliverman_chat_id), latitude=order[2], longitude=order[3])
            await bot.send_message(chat_id=user_chat_id, text="▶️ Yetkazilmoqda!\n▶️ Доставляется!")
            await callback.message.delete()
        else:
            await callback.answer('Sizda bu buyruq uchun ruxsat yo\'q!')
            await callback.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')
    else:
        await callback.answer('Sizda bu buyruq uchun ruxsat yo\'q!')
        await callback.answer('/start kommandasi orqali o\'zingizning ishingizni toping!')

