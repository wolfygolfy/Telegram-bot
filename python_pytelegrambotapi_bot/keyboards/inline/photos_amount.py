from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def photos_amount() -> InlineKeyboardMarkup:
    amount = InlineKeyboardMarkup()
    for i_num in range(1, 5):
        amount.add(InlineKeyboardButton(text=i_num, callback_data=f'{i_num}'))
    return amount
