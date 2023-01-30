from telebot.types import Message, InputMediaPhoto, CallbackQuery
from loader import bot
from keyboards.inline import hotels_amount, photos_necessity, photos_amount
from states.hotels_info_states import UserStates
import re
from handlers.custom_handlers import req_handler
from database import mysql_database_handler
from datetime import datetime, date
"""
Хендлер для обработки команд lowprice, highprice и bestdeal.
Выдаёт пользователю топ самых дешёвых отелей в городе с основной информацией о них.
По желанию пользователя может также выдать фотографии.
"""


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def command_handler(message: Message) -> None:
    """
    Функция обрабатывает команды lowprice, highprice и betdeal и спрашивает в ответ на неё город,
    в котором будет вестись поиск.

    :param message: принимает на вход сообщение, которое передаёт декоратор
    """
    bot.set_state(message.from_user.id, UserStates.CityInfo)
    bot.reply_to(
        message,
        text='В каком городе будем искать?'
    )
    with bot.retrieve_data(message.from_user.id) as data:
        data['user_command'] = message.text


@bot.message_handler(commands=['history'])
def history_sender(message: Message) -> None:
    results = mysql_database_handler.table_query(message.from_user.id)
    for i_result in results:
        bot.send_message(message.from_user.id, text=
                         f"Введённая команда: {i_result[0]}\n"
                         f"Дата и время поиска: {i_result[1]}\n"
                         f"Результаты поиска: {i_result[2]}")


@bot.message_handler(state=UserStates.CityInfo)
def get_city_name(message: Message) -> None:
    """
    Функция обрабатывает название города, нужного пользователю и меняет текущий статус пользователя.
    Делает запрос к api с нужным названием города.
    Сохраняет id нужного города.
    Даёт боту команду отослать пользователю клавиатуру с вариантами количества отелей.

    :param message: получает из декоратора название города, введённого пользователем.
    """

    if re.search(r'\d', message.text):
        bot.send_message(
            message.from_user.id,
            text='Введены некорректные данные, попробуйте ещё раз.')

    else:
        with bot.retrieve_data(message.from_user.id) as data:
            data['city_name'] = message.text
            data['city_id'] = req_handler.find_city_id(city_name=data['city_name'])

        bot.send_message(
            message.from_user.id,
            text='Введите дату заселения и выезда в формате "ггг-мм-дд" через пробел'
        )
        bot.set_state(message.from_user.id, UserStates.DateInput)


@bot.message_handler(state=UserStates.DateInput)
def save_date(message: Message):
    """
    Функция обрабатывает данные, введенные пользователем в ответ на сообщение из функции get_city_name, и, если всё
    введено корректно, то сохраняет их как дату заезда и дату отъезда, меняет состояние пользователя в зависимости
    от введённой в начале работы команды и даёт боту команду
    отправить запрос на максимальную допустимую цену.

    :param message: получает из декоратора данные, отправленные пользователем
    """

    if re.search(r'\d{4}-\d{2}-\d{2}\s\d{4}-\d{2}-\d{2}', message.text):
        dates_strings_list = message.text.split()
        with bot.retrieve_data(message.from_user.id) as data:
            data['checkIn_date'] = dates_strings_list[0]
            data['checkOut_date'] = dates_strings_list[1]

            if data['user_command'] == '/bestdeal':
                bot.reply_to(
                    message,
                    text='Введите максимальную цену для отеля.'
                    '\n(Внимание, все цены вводятся в долларах США($)!)',
                )
                bot.set_state(message.from_user.id, UserStates.PriceRange)
            else:
                bot.send_message(
                    message.from_user.id,
                    text='Сколько вариантов вам понадобится?',
                    reply_markup=hotels_amount.hotels_amount())
                bot.set_state(message.from_user.id, UserStates.HotelsAmount)
    else:
        bot.send_message(
            message.from_user.id,
            text='Данные введены некорректно.'
                 '\nВведите дату заезда и отъезда в формате "ггг-мм-дд" через пробел.'
        )


@bot.message_handler(state=UserStates.PriceRange)
def save_prices(message: Message):
    """
    Функция обрабатывает введённые пользователем данные в ответ на сообщение из функции save_date и сохраняет их
    как максимально допустимую цену, меняет состояние пользователя.
    Даёт боту команду спросить у пользователя про максимально допустимое расстояние
    от центра.

    :param message: получает из декоратора данные, отправленные пользователем
    """
    with bot.retrieve_data(message.from_user.id) as data:
        data['priceMax'] = message.text
    bot.send_message(
        message.from_user.id,
        text='Введите максимально допустимое расстояние отеля от центра (в км).'
    )
    bot.set_state(message.from_user.id, UserStates.Distance)


@bot.message_handler(state=UserStates.Distance)
def save_distance(message: Message):
    """
    Функция обрабатывает введённые пользователем данные в ответ на сообщение из функции save_prices и сохраняет их
    как максимально допустимое расстояние от центра, меняет состояние пользователя.
    Даёт боту команду отправить пользователю клавиатуру с вопросом о количестве вариантов.

    :param message: получает из декоратора данные, отправленные пользователем
    """
    with bot.retrieve_data(message.from_user.id) as data:
        data['max_distance'] = message.text
    bot.send_message(
        message.from_user.id,
        text='Сколько вариантов вам понадобится?',
        reply_markup=hotels_amount.hotels_amount())
    bot.set_state(message.from_user.id, UserStates.HotelsAmount)


@bot.callback_query_handler(state=UserStates.HotelsAmount, func=lambda call: True)
def get_hotels_amount(call: CallbackQuery) -> None:
    """
    Обрабатывает отклик от клавиатуры и делает запрос к api в соответствии с ним.
    Даёт боту команду отослать клавиатуру с вариантами 'да' или 'нет'.

    :param call: отклик от клавиатуры, полученый из декоратора
    """
    with bot.retrieve_data(call.from_user.id) as data:
        data['hotels_amount'] = int(call.data)
        if data['user_command'] == '/lowprice':
            data['info'] = req_handler.hotels_info(city_id=data['city_id'],
                                                   size=call.data,
                                                   check_in=data['checkIn_date'],
                                                   check_out=data['checkOut_date'],
                                                   sort_order='PRICE')
        elif data['user_command'] == '/highprice':
            data['info'] = req_handler.hotels_info(city_id=data['city_id'],
                                                   size=call.data,
                                                   check_in=data['checkIn_date'],
                                                   check_out=data['checkOut_date'],
                                                   sort_order='PRICE_HIGHEST_FIRST')
        elif data['user_command'] == '/bestdeal':
            data['info'] = req_handler.hotels_info(city_id=data['city_id'],
                                                   size=call.data,
                                                   check_in=data['checkIn_date'],
                                                   check_out=data['checkOut_date'],
                                                   max_price=data['priceMax'],
                                                   sort_order='PRICE',
                                                   max_distance=int(data['max_distance']))
        if data['info']:
            bot.send_message(call.from_user.id, text='Понадобятся фотографии?',
                             reply_markup=photos_necessity.need_photos())
            bot.set_state(call.from_user.id, UserStates.PhotosState)
        else:
            bot.send_message(call.from_user.id,
                             text='К сожалению, отелей с такими критериями не нашлось.')


@bot.callback_query_handler(state=UserStates.PhotosState, func=lambda call: True)
def photos_stage(call: CallbackQuery) -> None:
    """
    Обрабатывает отклик от клавиатуры.
    При выборе пользователем варианта 'нет' даёт боту команду отослать полученные об отелях данные.
    При выборе пользователем варианта 'да' даёт боту команду отправить пользователю клавиатуру с вариантами количества фото.
    :param call: отклик 'yes' или 'no' из декоратора
    """
    with bot.retrieve_data(call.from_user.id) as data:
        dates_list = list()
        dates_list.append(date(int(data['checkOut_date'].split('-')[0]),
                               int(data['checkOut_date'].split('-')[1]),
                               int(data['checkOut_date'].split('-')[2])),
                          )

        dates_list.append(date(int(data['checkIn_date'].split('-')[0]),
                               int(data['checkIn_date'].split('-')[1]),
                               int(data['checkIn_date'].split('-')[2]))
                          )

        data['TotalDays'] = int(str(dates_list[0] - dates_list[1]).split()[0])
        data['hotels_names'] = list()
        if call.data == 'no':
            if data['hotels_amount'] > len(data['info']):
                bot.send_message(call.from_user.id,
                                 text='К сожалению, нашлось только {} подходящих отелей.'.format(len(data['info'])))
            for i_hotel in data['info']:
                bot.send_message(call.from_user.id,
                                 text=f'{i_hotel}\n'
                                      f'Адрес: {data["info"][i_hotel]["Адрес"]}\n'
                                      f'Расстояние до центра: {data["info"][i_hotel]["Расстояние от центра"]}\n'
                                      f'Цена за ночь: {data["info"][i_hotel]["Цена"]}\n'
                                      f'Полная цена за всё время пребывания: ${data["TotalDays"] * int(data["info"][i_hotel]["Цена"][1:])}\n'
                                      f'Ссылка на отель: https://hotels.com/ho{data["info"][i_hotel]["id"]}')
                data['hotels_names'].append(f"{i_hotel}")
            mysql_database_handler.database_query(
                user_id=call.from_user.id,
                command=data['user_command'],
                date=datetime.today(),
                results="; ".join(data['hotels_names'])
            )

        elif call.data == 'yes':
            bot.send_message(call.from_user.id, text='Сколько фотографий желаете увидеть?',
                             reply_markup=photos_amount.photos_amount())
            bot.set_state(call.from_user.id, UserStates.FinalState)


@bot.callback_query_handler(state=UserStates.FinalState, func=lambda call: True)
def amount_of_photos(call: CallbackQuery) -> None:
    """
    Обрабатывает отклик от клавиатуры и, в зависимости от него, даёт боту команду отослать пользователю главную информацию
    об отелях и требуемое количество фотографий.

    :param call: принимает отклик из декоратора
    """
    with bot.retrieve_data(call.from_user.id) as data:
        data['hotels_names'] = list()
        if data['hotels_amount'] > len(data['info']):
            bot.send_message(call.from_user.id,
                             text='К сожалению, нашлось только {} подходящих отелей.'.format(len(data['info'])))
        for i_hotel in data['info']:
            answer = req_handler.get_photos(hotel_id=data['info'][i_hotel]['id'], amount=int(call.data))
            medias = list()
            medias.append(InputMediaPhoto(answer[0],
                                          caption=f'{i_hotel}\n'
                                          f'Адрес: {data["info"][i_hotel]["Адрес"]}\n'
                                          f'Расстояние до центра: {data["info"][i_hotel]["Расстояние от центра"]}\n'
                                          f'Цена за ночь: {data["info"][i_hotel]["Цена"]}\n'
                                          f'Полная цена за всё время пребывания: ${data["TotalDays"] * int(data["info"][i_hotel]["Цена"][1:])}\n'
                                          f'Ссылка на отель: https://hotels.com/ho{data["info"][i_hotel]["id"]}'))
            data['hotels_names'].append(f"{i_hotel}")
            for i_num in range(1, int(call.data)):
                medias.append(InputMediaPhoto(answer[i_num]))
            bot.send_media_group(call.from_user.id, medias)
        mysql_database_handler.database_query(
            user_id=call.from_user.id,
            command=data['user_command'],
            date=datetime.today(),
            results=", ".join(data['hotels_names'])
        )

