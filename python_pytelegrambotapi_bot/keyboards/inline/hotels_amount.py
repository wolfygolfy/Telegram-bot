from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def hotels_amount() -> InlineKeyboardMarkup:
    amount = InlineKeyboardMarkup()
    for i_num in range(1, 6):
        amount.add(InlineKeyboardButton(text=i_num, callback_data=str(i_num)))
    return amount
