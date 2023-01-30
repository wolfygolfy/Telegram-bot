from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def need_photos() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    key_yes = InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    return keyboard


