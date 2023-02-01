import requests
import configparser


class YandexDisk:

    def __init__(self, token: str):
        self.token = token

    def make_dir(self, dir_name):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
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
            'Authorization': 'OAuth {}'.format(self.token)
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


if __name__ == "__main__":
    yandex_token = read_config('config.ini', 'Tokens', 'YandexToken')
    vk_token = read_config('config.ini', 'Tokens', 'VKToken')
    directory = read_config('config.ini', 'Path', 'Directory')
    vk_id = ('config.ini', 'ID', 'VK_ID')
    my_yandex = YandexDisk(yandex_token)
    my_yandex.make_dir(directory)
    print(my_yandex.upload_by_url('https://img2.goodfon.ru/original/1366x768/f/f7/kotyata-ryzhie-podstavka.jpg',
                                  directory))
