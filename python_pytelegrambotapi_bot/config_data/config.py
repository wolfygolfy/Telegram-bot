import dotenv
import os

if not dotenv.find_dotenv():
    exit('Переменные окружения не загружены, так как отсутствует файл .env')
else:
    dotenv.load_dotenv()

bot_token = os.getenv('bot_token')
api_key = os.getenv('rapid_api_key')
api_host = os.getenv('rapid_api_host')
location_URL = os.getenv('locations_URL')
property_URL = os.getenv('properties_URL')
photo_URL = os.getenv('photos_URL')
db_host = os.getenv('host')
db_user = os.getenv('user')
db_password = os.getenv('password')


default_commands = (
    ('start', 'запустить бота'),
    ('help', 'вывести справку'),
    ('hello_world', 'отправить тестовое приветственное сообщение'),
    ('lowprice', 'Узнать топ самых дешёвых отелей в городе'),
    ('highprice', 'Узнать топ самых дорогих отлелей в городе'),
    ('bestdeal', 'Узнать топ отелей, наиболее подходящих по цене и расположению от центра'),
    ('history', 'Узнать историю поиска отелей')
)
