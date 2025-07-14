from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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