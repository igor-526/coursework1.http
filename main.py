import requests
from pprint import pprint
import os


def get_setting(sett):
    settings = {}
    with open("settings.ini") as setting:
        for line in setting.readlines():
            line = (line.strip("\n").split(" : "))
            settings[line[0]] = line[1]
    return settings[sett]


class Vkapi:
    def __init__(self, token: str):
        self.token = token

    def _getalbuminfo(self, album):
        info = []
        response = requests.get('https://api.vk.com/method/photos.get', params={
            'access_token': self.token,
            'v': '5.131',
            'album_id': album,
            'extended': '1',
            'rev': '1',
            'owner_id': get_setting('id'),
            'count': get_setting('photo_count')})
        for photo in response.json()['response']['items']:
            info.append({"likes": photo['likes']['count'], 'date': photo['date'], 'url': photo['sizes'][-1]['url']})
        return info

    def savephotos(self, album):
        info = vk._getalbuminfo(album)
        for photo in info:
            response = requests.get(photo['url'])
            file_path = os.path.join(os.getcwd(), 'photos', f'{photo["likes"]}.jpg')
            if os.path.exists(file_path):
                file_path = os.path.join(os.getcwd(), 'photos', f'{photo["likes"]}_{photo["date"]}.jpg')
                with open(file_path, 'wb') as jpg:
                    jpg.write(response.content)
            else:
                with open(file_path, 'wb') as jpg:
                    jpg.write(response.content)


class Diskapi:
    def __init__(self, token: str):
        self.token = token

    def _getuploadlink(self, path, file, overwrite):
        url = 'https://cloud-api.yandex.net:443/v1/disk/resources/upload'
        headers = {'Content-Type': 'application/json', 'Authorization': self.token}
        response = requests.get(url, headers=headers, params={'path': f'{path}/{file}', 'overwrite': overwrite})
        return response.json()['href']

    def uploadphotos(self):
        for file in (os.listdir('photos')):
            print(file)
            requests.put(yadisk._getuploadlink(get_setting('yandexpath'), file, get_setting('yandexoverwrite')), data=open(f'photos/{file}', 'rb'))

print ('commited')
