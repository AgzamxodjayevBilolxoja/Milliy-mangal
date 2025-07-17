from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from loader import db
from services.database.sql import get_branches

remove_keyboard = ReplyKeyboardRemove()

uz = "🇺🇿 O'zbekcha"
ru = "🇷🇺 Русский"
back_uz = '⬅️ Ortga'
back_ru = '⬅️ Назад'

def phone_markup(lang):
    markup = {
        uz: ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📱 Telefon raqam", request_contact=True)]], resize_keyboard=True),
        ru: ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📱 Номер телефона", request_contact=True)]], resize_keyboard=True)
    }
    return markup.get(lang)

def menu_markup(lang):
    markup = {
        uz: ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🍽 Menyu')], [KeyboardButton(text="📥 Buyurtmalarim"), KeyboardButton(text="🛒 Savatcham")], [KeyboardButton(text='ℹ️ Biz haqimizda'), KeyboardButton(text="📍 Filiallarimiz")], [KeyboardButton(text='⭐ Baholash')], [KeyboardButton('⚙️ Sozlamalar')]], resize_keyboard=True),
        ru: ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🍽 Меню')], [KeyboardButton(text="📥 Мои заказы"), KeyboardButton(text="🛒 Корзинка")], [KeyboardButton(text='ℹ️ О нас'), KeyboardButton(text="📍 Наши филиалы")], [KeyboardButton(text='⭐ Оценить')], [KeyboardButton('⚙️ Настройки')]], resize_keyboard=True)
    }
    return markup.get(lang)

def settings_markup(lang):
    markup = {
        uz: ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='✏️ Ism o\'zgartirish'), KeyboardButton(text='📱 Telefon raqam o\'zgartirish')], [KeyboardButton(text='🇷🇺 Til o\'zgartirish')], [KeyboardButton(text=back_uz)]], resize_keyboard=True),
        ru: ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='✏️ Изменить имя'), KeyboardButton(text='📱 Изменить телефон номер')], [KeyboardButton(text='🇺🇿 Изменить язык')], [KeyboardButton(text=back_ru)]], resize_keyboard=True)
    }
    
    return markup.get(lang)

lang_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🇺🇿 O'zbekcha"),
            KeyboardButton(text="🇷🇺 Русский")
        ]
    ], resize_keyboard=True
)

def back_markup(lang):
    markup = {
        uz: ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=back_uz)]], resize_keyboard=True),
        ru: ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=back_ru)]], resize_keyboard=True)
    }
    
    return markup.get(lang)

def rating_markup(lang):
    markup = {
        uz: ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⭐⭐⭐⭐⭐ Hammasi a'lo")], [KeyboardButton(text="⭐⭐⭐⭐ Yaxshi")], [KeyboardButton(text="⭐⭐⭐ O'rta")], [KeyboardButton(text="❤️ Bo'ladi")], [KeyboardButton(text="👎 Juda yomon")], [KeyboardButton(text=back_uz)]], resize_keyboard=True),
        ru: ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⭐⭐⭐⭐⭐ Всё хорошо")], [KeyboardButton(text="⭐⭐⭐⭐ Хороший")], [KeyboardButton(text="⭐⭐⭐ Средний")], [KeyboardButton(text="❤️ Будет")], [KeyboardButton(text="👎 Очень плохо")], [KeyboardButton(text=back_ru)]], resize_keyboard=True)
    }
    
    return markup.get(lang)

staff_start_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Admin")
        ],
        [
            KeyboardButton(text='Oshpaz'),
            KeyboardButton(text='Yetkazib beruvchi')
        ]
    ], resize_keyboard=True
)

admin_menu_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🍽️ Menyu o'zgartirish")            
        ],
        [
          KeyboardButton('👥 Foydalanuvchilar')  
        ],
        [
            KeyboardButton(text="📍 Filiallar"),
            KeyboardButton(text="🦺 Ishchilar")
        ]
    ], resize_keyboard=True
)

admin_branch_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Filial qo'shish"),
            KeyboardButton(text="📍 Filiallarni ko'rish")
        ]
    ], resize_keyboard=True
)

def get_branches_markup(branches, lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for branch in branches:
        markup.insert(KeyboardButton(text=branch[0]))
    if lang == uz:
        markup.add(KeyboardButton(text=back_uz))
    else:
        markup.add(KeyboardButton(text=back_ru))
    return markup

admin_update_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🟢 O'zgartirish"),
            KeyboardButton(text="🔴 O'chirish")
        ],
        [
            KeyboardButton(text=back_uz)
        ]
    ], resize_keyboard=True
)

branch_update_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📍 Joylashuvni o'zgartirish"),
        ],
        [   
            KeyboardButton(text="✏️ Nomini o'zgartirish"),
        ],
        [  
            KeyboardButton(text="🕛 Ishlash vaqtini o'zgartirish")
        ],
        [
            KeyboardButton(text=back_uz)
        ]
    ], resize_keyboard=True
)

change_menu_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Kategoriyalar'),
            KeyboardButton('Ovqatlar')
        ],
        [
            KeyboardButton(text=back_uz)
        ]
    ], resize_keyboard=True
)

admin_category_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Kategoriya qo'shish"),
            KeyboardButton(text="Kategoriyalarni ko'rish")
        ],
        [
            KeyboardButton(text=back_uz)
        ]
    ], resize_keyboard=True
)

def get_categories_markup(categories, lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if lang == uz:
        for category in categories:
            markup.insert(KeyboardButton(text=category[1]))
        markup.add(KeyboardButton(text=back_uz))
    else:
        for category in categories:
            markup.insert(KeyboardButton(text=category[2]))
        markup.add(KeyboardButton(text=back_ru))
    return markup

delete_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🔴 O\'chirish')
        ],
        [
            KeyboardButton(text=back_uz)
        ]
    ], resize_keyboard=True
)

admin_foods_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Ovqat qo'shish"),
            KeyboardButton(text="Ovqatlarni ko'rish")
        ],
        [
            KeyboardButton(text=back_uz)
        ]
    ], resize_keyboard=True
)

def product_markup(products, lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if lang == uz:
        for product in products:
            markup.insert(KeyboardButton(text=product[2]))
        markup.add(KeyboardButton(text=back_uz))
    else:
        for product in products:
            markup.insert(KeyboardButton(text=product[3]))
        markup.add(KeyboardButton(text=back_ru))
    return markup

admin_food_update_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🇺🇿 O'zbekcha nomni o'zgartirish")
        ],
        [   
            KeyboardButton(text="🇷🇺 Ruscha nomni o'zgartirish")
        ],
        [
            KeyboardButton(text="🇺🇿 O'zbekcha ma'lumotni o'zgartirish")
        ],
        [   
            KeyboardButton(text="🇷🇺 Ruscha ma'lumotni o'zgartirish")
        ],
        [
            KeyboardButton(text="🤑 Narxni o'zgartirish")
        ],
        [  
            KeyboardButton(text="🖼️ Rasmni o'zgartirish")
        ],
        [
            KeyboardButton(text=back_uz)
        ]
    ]
)