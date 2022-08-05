import requests
from pprint import pprint
import os
import shutil
import json
import sys


def get_setting(sett):
    settings = {}
    with open("settings.ini") as setting:
        for line in setting.readlines():
            line = (line.strip("\n").split(" : "))
            settings[line[0]] = line[1]
    if sett in settings:
        return settings[sett]
    else:
        return 'not found'


def write_setting(sett, value):
    settings = {}
    with open("settings.ini") as setting:
        for line in setting.readlines():
            line = (line.strip("\n").split(" : "))
            settings[line[0]] = line[1]
    settings[sett] = value
    with open("settings.ini", "w") as setting:
        setting.write('')
    for line in settings:
        with open("settings.ini", "a") as setting:
            setting.write(f'{line} : {settings[line]}\n')
    return value


def initvk(token):
    vk = Vkapi(get_setting('vktoken'))
    if token == 'not found':
        print('Ошибка: токен VK отсутствует!')
        initvk(write_setting('vktoken', input("Введите токен VK: ")))
    else:
        if 'error' in vk.getinfo():
            print(f'Ошибка: {vk.getinfo()["error"]["error_msg"]}')
            initvk(write_setting('vktoken', input("Введите токен VK: ")))
        else:
            print(f'Добро пожаловать, {vk.getinfo()["response"][0]["first_name"]}!')
            return 'initpass'


def downloadalbum():
    vk = Vkapi(get_setting('vktoken'))
    profiles = vk.getfriends()
    myid = vk.getinfo()['response'][0]['id']
    profiles[0]['id'] = myid
    settings = {}
    for id, profile in enumerate(profiles):
        print(f'{id}. {profile["name"]}')
    print()
    settings['id'] = profiles[int(input("С чьим профилем будем работать? "))]['id']
    print()
    albums = vk.getalbums(settings['id'])
    for id, album in enumerate(albums):
        print(f'{id}. {album["name"]} | {album["count"]} фотографий')
    print()
    settings['albumid'] = albums[int(input("Какой альбом будем выгружать? "))]['id']
    print()
    settings['count'] = input("Какое количество фотографий будем выгружать? ")
    shutil.rmtree(os.path.join(os.getcwd(), 'photos'))
    os.mkdir("photos")
    os.mkdir("photos/json")
    vk.savephotos(vk._getalbuminfo(settings['id'], settings['albumid'], settings['count']))


def menu(choise):
    initvk(get_setting('vktoken'))
    while choise != 'q':
        print('1. Выгрузить фотографии из альбома\n'
              '2. Удалить токен VK\n'
              'q. Выход из программы\n')
        choise = input("Выберите пункт меню: ")
        if choise == '1':
            print()
            downloadalbum()
        if choise == '2':
            write_setting('vktoken', '')
            menu(0)
    else:
        print('До свидания!')
        sys.exit()


class Vkapi:
    def __init__(self, token: str):
        self.token = token

    def _getalbuminfo(self, owner_id, album, count):
        info = []
        response = requests.get('https://api.vk.com/method/photos.get', params={
            'access_token': self.token,
            'v': '5.131',
            'album_id': album,
            'extended': '1',
            'rev': '1',
            'owner_id': owner_id,
            'count': count})
        for photo in response.json()['response']['items']:
            info.append({"likes": photo['likes']['count'], 'id': photo['id'], 'url': photo['sizes'][-1]['url'], 'date': photo['date']})
        return info

    def savephotos(self, info):
        for counter, photo in enumerate(info):
            response = requests.get(photo['url'])
            dir_path = os.path.join(os.getcwd(), 'photos')
            name = photo["likes"]
            if os.path.exists(os.path.join(dir_path, f'{name}.jpg')):
                name = f'{photo["likes"]}_{photo["id"]}'
            with open(os.path.join(dir_path, f'{name}.jpg'), 'wb') as jpg:
                jpg.write(response.content)
            with open(os.path.join(dir_path, 'json', f'{name}.json'), 'w') as jsonfile:
                json.dump({'filename': f'{name}.jpg', 'date': photo['date'], 'photo_id': photo['id'], 'likes': photo['likes']}, jsonfile)
            print(f'| {int(counter/len(info)*100)}% | Фотография {name}.jpg успешно загружена!')
        print(f'| 100% | Задание успешно выполнено!')

    def getinfo(self):
        response = requests.get('https://api.vk.com/method/users.get', params={'access_token': self.token, 'v': '5.131'})
        return response.json()

    def getfriends(self):
        profiles = [{'name': 'Мой профиль', 'id': ''}]
        response = requests.get('https://api.vk.com/method/friends.get', params={'access_token': self.token, 'v': '5.131', 'fields': 'contacts'})
        for friend in response.json()['response']['items']:
            profiles.append({'name': f'{friend["first_name"]} {friend["last_name"]}', 'id': friend['id']})
        return profiles

    def getalbums(self, id):
        albums = []
        response = requests.get('https://api.vk.com/method/photos.get',
                                params={'access_token': self.token, 'v': '5.131', 'owner_id': id, 'album_id': 'profile'})
        response = response.json()['response']['count']
        albums.append({'name': 'Фотографии профиля', 'id': 'profile', 'count': response})
        response = requests.get('https://api.vk.com/method/photos.get',
                                params={'access_token': self.token, 'v': '5.131', 'owner_id': id,
                                        'album_id': 'wall'})
        response = response.json()['response']['count']
        albums.append({'name': 'Фотографии со стены', 'id': 'wall', 'count': response})
        response = requests.get('https://api.vk.com/method/photos.getAlbums',
                                params={'access_token': self.token, 'v': '5.131', 'owner_id': id})
        for album in response.json()['response']['items']:
            albums.append({'name': album['title'], 'id': album['id'], 'count': album['size']})
        return albums


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


yadisk = Diskapi('yandextoken')
menu(0)