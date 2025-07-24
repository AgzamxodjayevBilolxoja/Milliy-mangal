from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from loader import db
from ..default.markup import uz, back_uz, back_ru

language_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data='uz'),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data='ru')
        ]
    ]
)

yes_or_no_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='✅ Ha', callback_data='yes'),
            InlineKeyboardButton(text='❌ Yo\'q', callback_data='no')
        ]
    ]
)

def inline_category_markup(categories, lang):
    markup = InlineKeyboardMarkup(row_width=2)
    if lang == uz:
        for category in categories:
            markup.insert(InlineKeyboardButton(text=category[1], callback_data=category[1]))
    else:
        for category in categories:
            markup.insert(InlineKeyboardButton(text=category[2], callback_data=category[2]))
    
    return markup

def inline_food_markup(foods, lang):
    markup = InlineKeyboardMarkup(row_width=2)
    if lang == uz:
        for food in foods:
            markup.insert(InlineKeyboardButton(text=food[2], callback_data=food[2]))
        markup.add(InlineKeyboardButton(text=back_uz, callback_data=back_uz))
    else:
        for food in foods:
            markup.insert(InlineKeyboardButton(text=food[3], callback_data=food[3]))
        markup.add(InlineKeyboardButton(text=back_ru, callback_data=back_ru))
    
    return markup

food_callback = CallbackData("food", "action", "food_id", "price", "count", "lang")

def plus_minus_markup(lang, food_id: int, price: int, count: int=1, cart=None):
    markup = InlineKeyboardMarkup(row_width=3)
    markup.insert(InlineKeyboardButton(text="➖", callback_data=food_callback.new(action="minus", food_id=food_id, price=price, count=count, lang=lang)))
    markup.insert(InlineKeyboardButton(text=f"{count}", callback_data=food_callback.new(action="count", food_id=food_id, price=price, count=count, lang=lang)))
    markup.insert(InlineKeyboardButton(text="➕", callback_data=food_callback.new(action="plus", food_id=food_id, price=price, count=count, lang=lang)))
        
    if lang == uz:
        if cart:
            markup.add(InlineKeyboardButton(text="❌ Savatchadan olib tashlash", callback_data=food_callback.new(action="delete", food_id=food_id, price=price, count=count, lang=lang)))
        else:
            markup.add(InlineKeyboardButton(text="🛒 Savatchaga qo'shish", callback_data=food_callback.new(action="cart", food_id=food_id, price=price, count=count, lang=lang)))
    else:
        if cart:
            markup.add(InlineKeyboardButton(text="❌ Убрать от корзины", callback_data=food_callback.new(action="delete", food_id=food_id, price=price, count=count, lang=lang)))
        else:
            markup.add(InlineKeyboardButton(text="🛒 Добавить в корзину", callback_data=food_callback.new(action="cart", food_id=food_id, price=price, count=count, lang=lang)))
    
    return markup

cart_callback = CallbackData("cart", "action", "lang", "food_id", "count")

def cart_plus_minus_markup(lang, cart: list, sql):
    markup = InlineKeyboardMarkup(row_width=3)
    if lang == uz:
        for cart_item in cart:
            food = db.execute(sql, (cart_item[2], ), fetchone=True)
            markup.add(InlineKeyboardButton(text=food[2], callback_data=cart_callback.new(action="name", lang=lang, food_id=food[0], count=cart_item[3])))
            markup.add(InlineKeyboardButton(text="➖", callback_data=cart_callback.new(action="minus", lang=lang, food_id=food[0], count=cart_item[3])))
            markup.insert(InlineKeyboardButton(text=f"{cart_item[3]}", callback_data=cart_callback.new(action="count", lang=lang, food_id=food[0], count=cart_item[3])))
            markup.insert(InlineKeyboardButton(text="➕", callback_data=cart_callback.new(action="plus", lang=lang, food_id=food[0], count=cart_item[3])))
            markup.add(InlineKeyboardButton(text="❌ Savatchadan olib tashlash", callback_data=cart_callback.new(action="remove", lang=lang, food_id=food[0], count=cart_item[3])))
    else:
        for cart_item in cart:
            food = db.execute(sql, (cart_item[2], ), fetchone=True)
            markup.add(InlineKeyboardButton(text=food[3], callback_data=cart_callback.new(action="name", lang=lang, food_id=food[0], count=cart_item[3])))
            markup.add(InlineKeyboardButton(text="➖", callback_data=cart_callback.new(action="minus", lang=lang, food_id=food[0], count=cart_item[3])))
            markup.insert(InlineKeyboardButton(text=f"{cart_item[3]}", callback_data=cart_callback.new(action="count", lang=lang, food_id=food[0], count=cart_item[3])))
            markup.insert(InlineKeyboardButton(text="➕", callback_data=cart_callback.new(action="plus", lang=lang, food_id=food[0], count=cart_item[3])))
            markup.add(InlineKeyboardButton(text="❌ Убрать от корзины", callback_data=cart_callback.new(action="remove", lang=lang, food_id=food[0], count=cart_item[3])))
    
    return markup

order_callback = CallbackData('yes_or_no', 'action', 'user_id', 'latitude', 'longitude')

def chef_yes_or_no_markup(user_id, latitude, longitude):
    markup = InlineKeyboardMarkup(
    inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha", callback_data=order_callback.new(action='yes', user_id=user_id, latitude=latitude, longitude=longitude)),
                InlineKeyboardButton(text="❌ Yo'q", callback_data=order_callback.new(action='no', user_id=user_id, latitude=latitude, longitude=longitude))
            ]
        ]
    )
    return markup

chef_return_callback = CallbackData("chef_return", "action", "chat_id")

def chef_return_markup(chat_id):
    markup = InlineKeyboardMarkup(
    inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data=chef_return_callback.new(action='no', chat_id=chat_id)),
                InlineKeyboardButton(text="✅ Tayyor", callback_data=chef_return_callback.new(action='finish', chat_id=chat_id))
            ]
        ]
    )
    return markup

chef_return_delivery_callback = CallbackData("chef_return_delivery", "action2", "chat_id", "buy_type")

def chef_return_delivery_markup(chat_id, buy_type):
    markup = InlineKeyboardMarkup(
    inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data=chef_return_delivery_callback.new(action2='no', chat_id=chat_id, buy_type=buy_type)),
                InlineKeyboardButton(text="✅ Yetkazib beruvchiga yuborish", callback_data=chef_return_delivery_callback.new(action2='next', chat_id=chat_id, buy_type=buy_type))
            ]
        ]
    )
    return markup

delivermen_callback = CallbackData("delivermen", "action", "chat_id", "user_chat_id", "buy_type")

def delivermen_markup(delivermen, user_chat_id, buy_type):
    markup = InlineKeyboardMarkup(row_width=2)
    for deliverman in delivermen:
        markup.insert(
            InlineKeyboardButton(text=deliverman[4], callback_data=delivermen_callback.new(action="deliverman", chat_id=str(deliverman[1]), user_chat_id=user_chat_id, buy_type=buy_type))
            )
    
    return markup