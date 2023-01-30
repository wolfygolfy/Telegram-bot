from telebot.types import Message
from loader import bot


@bot.message_handler(content_types=['text'])
def get_text_message(message: Message):
    if message.text == 'Привет':
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")

