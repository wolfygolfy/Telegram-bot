from config_data import config
import requests
import re
import json
from datetime import date


def request_to_api(url: str, headers: dict, querystring: dict) -> requests.Response or str:
    """
    Функция для отправки запроса к апи и для проверки наличия ответа.

    :param url: url-ссылка, требуемая для конкретного запроса
    :param headers: словарь, включающий в скбя api-key и api-host
    :param querystring: словарь, включающий в себя нужные для запроса параметры
    :return: возвращает полученый ответ либо строку 'Ошибка'
    """
    try:
        response = requests.get(url=url, headers=headers, params=querystring, timeout=10)
        if response.status_code == requests.codes.ok:
            return response
    except Exception:
        return 'Ошибка'


def find_city_id(city_name: str) -> str:
    """
    Функция, передающая в функцию request_to_api параметр querystring с нужными ключами для получения ID нужного города.

    :param city_name: получает название города
    :return: возвращает десериализированный json-файл
    """
    response = request_to_api(url=config.location_URL,
                              headers={
                                        'X-RapidAPI-Key': config.api_key,
                                        'X-RapidAPI-Host': config.api_host
                                       },
                              querystring={
                                            'query': city_name,
                                            'locale': 'ru_RU'
                                           })
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, response.text)
    if find:
        return json.loads(f"{{{find[0]}}}")['entities'][0]['destinationId']


def hotels_info(city_id: str, size: str, check_in: str, check_out: str, max_distance: int = None,
                sort_order: str = 'PRICE', max_price: str = '') -> dict:
    """
    Передает в функцию request_to_api параметр querystring с нужными ключами для получения информации об отелях
    по возрастанию или убыванию цен.

    :param city_id: ID города, в котором ведётся поиск
    :param size: количество результатов
    :param check_in: дата заезда
    :param check_out: дата отъезда
    :param max_distance: максимальное расстояние от центра. Используется только при команде bestdeal
    :param sort_order: порядок сортировки (по возрастанию или убыванию цен)
    :param max_price: максимальная допустимая цена. Используется только при команде bestdeal
    :return: возвращает словарь с информацией об отелях
    """
    flag = False
    response = request_to_api(url=config.property_URL,
                              headers={
                                    'X-RapidAPI-Key': config.api_key,
                                    'X-RapidAPI-Host': config.api_host
                                         },
                              querystring={
                                    'destinationId': city_id,
                                    'pageNumber': '1',
                                    'pageSize': size,
                                    'checkIn': check_in,
                                    'checkOut': check_out,
                                    'adults1': '1',
                                    'priceMax': max_price,
                                    'sortOrder': sort_order,
                                    'locale': 'ru_RU'
                                         })
    pattern = r'(?<=,)"results":.+?(?=,"pagination)'
    find = re.search(pattern, response.text)
    if find:
        data = json.loads(f"{{{find[0]}}}")
        hotels_inform = dict()
        for i_hotel in data['results']:
            if max_price != '':
                flag = True
                if ',' in i_hotel['landmarks'][0]['distance'].split()[0]:
                    distance = i_hotel['landmarks'][0]['distance'].split()[0]
                    distance = f'{distance[0]}.{distance[2]}'
                else:
                    distance = i_hotel['landmarks'][0]['distance'].split()
                    distance = distance[0]
            if (float(distance) <= max_distance) and (int(max_price) > float(i_hotel['ratePlan']['price']['current'][1:]))\
                    or (not flag):
                try:
                    hotels_inform[f'{i_hotel["name"]}'] = {
                            'id': i_hotel['id'],
                            'Адрес': i_hotel['address']['streetAddress'],
                            'Расстояние от центра': i_hotel['landmarks'][0]['distance'],
                            'Цена': i_hotel['ratePlan']['price']['current']
                        }
                except KeyError:
                    hotels_inform[f'{i_hotel["name"]}'] = {
                            'id': i_hotel['id'],
                            'Расстояние от центра': i_hotel['landmarks'][0]['distance'],
                            'Цена': i_hotel['ratePlan']['price']['current']
                        }
        return hotels_inform


def get_photos(hotel_id: str, amount: int) -> dict:
    """
    Передает в функцию request_to_api параметр querystring с нужными ключами для получения фотографий нужных отелей.

    :param hotel_id: ID нужного отеля
    :param amount: количество фотографий, которые отправятся кользователю
    :return: возвращает словарь со ссылками на фотографии
    """
    response = request_to_api(url=config.photo_URL,
                              headers={

                                 'X-RapidAPI-Key': config.api_key,
                                 'X-RapidAPI-Host': config.api_host
                                },
                              querystring={
                                 'id': hotel_id
                                })
    pattern = r'(?<=,)"hotelImages":.+?(?=,"roomImages)'
    find = re.search(pattern, response.text)
    if find:
        data = json.loads(f'{{{find[0]}}}')
        result = dict()
        for i_photo in range(amount):
            result[i_photo] = data['hotelImages'][i_photo]['baseUrl'].format(size='z')
        return result
