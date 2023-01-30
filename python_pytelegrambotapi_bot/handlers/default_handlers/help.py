from telebot.types import Message

from config_data.config import default_commands
from loader import bot


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    text = [f'/{command} - {desk}' for command, desk in default_commands]
    bot.reply_to(message, '\n'.join(text))
