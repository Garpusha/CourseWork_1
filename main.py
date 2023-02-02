import sys
import requests
import configparser
from time import sleep
from datetime import datetime
from sys import exit
import json

class YandexDisk:

    def __init__(self, token: str):
        self.token = token

    def make_dir(self, dir_name):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }
        # проверяю наличие каталога с заданным именем, если его нет, создаю
        params = {'path': f'disk:/{dir_name}'}
        url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 404:
            params = {'path': f'disk:/{dir_name}'}
            requests.put(url, headers=headers, params=params)

    def upload_by_url(self, source, destination):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        destination = f'{destination}/filename.jpg'
        params = {'path': destination, 'url': source}
        res = requests.post(url=url, headers=headers, params=params)
        return res


def read_config(path, section, parameter):
    config = configparser.ConfigParser()
    config.read(path)
    value = config.get(section, parameter)
    return value


class VK:
    def __init__(self, token: str):
        self.token = token

    # def get_user_info(self, user_id):
    #     url = 'https://api.vk.com/method/users.get'
    #     params = {'user_ids': user_id,
    #               'access_token': self.token,
    #               'v': '5.131'
    #               }
    #     res = requests.get(url, params=params)
    #     return res.json()

    def get_user_photos(self, user_id):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': user_id,
                  'album_id': 'profile',
                  'extended': 1,
                  'access_token': self.token,
                  'v': '5.131'
                  }
        res = requests.get(url, params=params)
        if 'error' in res.json():
            print(f'User {user_id} not exists')
            exit()
        return res.json()['response']['items'], res.json()['response']['count']


if __name__ == "__main__":

    # считываю переменные из конфигов
    yandex_token = read_config('tokens.ini', 'Tokens', 'YandexToken')
    vk_token = read_config('tokens.ini', 'Tokens', 'VKToken')
    directory = read_config('config.ini', 'Main', 'YandexDirectory')
    vk_id = read_config('config.ini', 'Main', 'VK_UserID')
    max_images = int(read_config('config.ini', 'Main', 'MaxImages'))

    my_yandex = YandexDisk(yandex_token)
    my_yandex.make_dir(directory)
    my_vk = VK(vk_token)

    size_list = []
    image_types='wzyxms'
    # print(my_yandex.upload_by_url('https://img2.goodfon.ru/original/1366x768/f/f7/kotyata-ryzhie-podstavka.jpg', directory))
        # pprint(my_vk.get_user_info(vk_id))

    result, images_count = my_vk.get_user_photos(vk_id)
    result = result[:min(len(result), max_images)]

    for image_set in result:
        likes = str(image_set['likes']['count'])
        image_date = datetime.utcfromtimestamp(image_set['date']).strftime('%Y-%m-%d')
        [size_list.append(image['type']) for image in image_set['sizes']]
        print(size_list)
        for image_type in image_types:
            if image_type in size_list:
                position = size_list.index(image_type)
                # now = datetime.datetime.now()
                # file_extension = image_set['sizes'][position]['url']
                my_yandex.upload_by_url(image_set['sizes'][position]['url'], f'{directory}/{image_date} - {likes}.jpg')
                sleep(0.4)
                break
        size_list.clear()
