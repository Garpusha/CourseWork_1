import requests
import configparser
from time import sleep
from datetime import datetime
from sys import exit
import json


class YandexDisk:

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def make_dir(self, dir_name):
        # headers = {
        #     'Content-Type': 'application/json',
        #     'Authorization': f'OAuth {self.token}'
        # }
        # проверяю наличие каталога с заданным именем, если его нет, создаю
        params = {'path': f'disk:/{dir_name}'}
        url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 404:
            params = {'path': f'disk:/{dir_name}'}
            requests.put(url, headers=self.headers, params=params)

    def upload_by_url(self, source, destination):
        # headers = {
        #     'Content-Type': 'application/json',
        #     'Authorization': f'OAuth {self.token}'
        # }
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        destination = f'{destination}'
        params = {'path': destination, 'url': source}
        return requests.post(url=url, headers=self.headers, params=params)

    def check_status(self, operation_url):
        # headers = {
        #     'Content-Type': 'application/json',
        #     'Authorization': f'OAuth {self.token}'
        # }
        return requests.get(url=operation_url, headers=self.headers).json()['status']


def read_config(path, section, parameter):
    config = configparser.ConfigParser()
    config.read(path)
    value = config.get(section, parameter)
    return value


class VK:
    def __init__(self, token: str):
        self.token = token


    def get_user_photos(self, user_id):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': user_id,
                  'album_id': 'profile',
                  'extended': 1,
                  'access_token': self.token,
                  'v': '5.131'
                  }
        res_photos = requests.get(url, params=params)
        if 'error' in res_photos.json():
            print(f'User {user_id} not exists')
            exit()
        return res_photos.json()['response']['items'], res_photos.json()['response']['count']



if __name__ == "__main__":

    # считываю переменные из конфигов
    yandex_token = read_config('tokens.ini', 'Tokens', 'YandexToken')
    vk_token = read_config('tokens.ini', 'Tokens', 'VKToken')
    directory = read_config('config.ini', 'Main', 'YandexDirectory')
    vk_id = read_config('config.ini', 'Main', 'VK_UserID')
    max_images = int(read_config('config.ini', 'Main', 'MaxImages'))
    sleep_time = int(read_config('config.ini', 'Main', 'SleepTime'))

    my_yandex = YandexDisk(yandex_token)
    my_vk = VK(vk_token)

    size_list = []
    image_types = 'wzyxms'
    my_yandex.make_dir(directory)
    json_data = []
    errors, success, in_progress = 0, 0, 0
    # читаю список фоток, обрезаю лишние
    profile_photos, images_count = my_vk.get_user_photos(vk_id)
    profile_photos = profile_photos[:min(len(profile_photos), max_images)]

    print('Upload to Yandex.Disk started')
    for index, image_set in enumerate(profile_photos):
        likes = str(image_set['likes']['count'])
        image_date = datetime.utcfromtimestamp(image_set['date']).strftime('%Y-%m-%d')

        # читаю доступные размеры фотографии
        [size_list.append(image['type']) for image in image_set['sizes']]

        # выбираю наибольший размер и загружаю на Я.Д.
        for image_type in image_types:
            if image_type in size_list:
                position = size_list.index(image_type)
                source_path = image_set['sizes'][position]['url']
                destination_path = f'{directory}/{image_date} - {likes}.jpg'
                res = my_yandex.upload_by_url(source_path, destination_path)
                status_url = res.json()['href']
                if res.status_code > 299:
                    print(f'({index + 1}/{max_images}) Error uploading file {image_date} - {likes}.jpg')
                else:
                    print(f'({index + 1}/{max_images}) File \'{image_date} - {likes}.jpg\' upload in progress')
                sleep(sleep_time)
                result = my_yandex.check_status(status_url)
                if result == 'success':
                    json_data.append({'file_name': f'{image_date} - {likes}.jpg', 'size': image_type})
                    success += 1
                elif result == 'failed':
                    errors += 1
                else:
                    in_progress += 1
                size_list.clear()
                break
        with open('result.json', 'w') as my_json:
            json.dump(json_data, my_json, indent=2)
    print(f'Upload complete. {success} files uploaded to Yandex.Disk, {in_progress} in progress, errors - {errors}')
    print('result.json created')
