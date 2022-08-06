import requests
import os
import shutil
import json
import sys
import time


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


def getbase():
    photobase = os.listdir(os.getcwd())
    to_remove = ['main.py', 'requiremеnts.txt', 'README.md', 'settings.ini']
    for obj in photobase:
        if obj[0] == '.':
            to_remove.append(obj)
    for obj in to_remove:
        photobase.remove(obj)
    return photobase


def base():
    photobase = getbase()
    if not photobase:
        print("Ваша база данных пуста!")
        return
    else:
        for num, folder in enumerate(photobase):
            print(f'{num}. {folder}')
    return


def initvk(token):
    vk = Vkapi(token)
    response = vk.getinfo()
    if token == 'not found':
        print('Ошибка: токен VK отсутствует!')
        initvk(write_setting('vktoken', input("Введите токен VK: ")))
        return 'retry'
    if 'error' in response:
        print(f'Ошибка: {response["error"]["error_msg"]}')
        write_setting('vktoken', input("Введите токен VK: "))
        return 'retry'
    else:
        print(f'Добро пожаловать, {response["response"][0]["first_name"]}!')
        return 'passed'


def vkdownload():
    initresult = initvk(get_setting('vktoken'))
    while initresult == 'retry':
        initresult = initvk(get_setting('vktoken'))
    if initresult == 'passed':
        vk = Vkapi(get_setting('vktoken'))
        profiles = vk.getfriends()
        myid = vk.getinfo()['response'][0]['id']
        profiles[0]['id'] = myid
        settings = {}
        for listid, profile in enumerate(profiles):
            print(f'{listid}. {profile["name"]}')
        print()
        settings['listid'] = profiles[int(input("С чьим профилем будем работать? "))]['id']
        print()
        albums = vk.getalbums(settings['listid'])
        for albid, album in enumerate(albums):
            print(f'{albid}. {album["name"]} | {album["count"]} фотографий')
        print()
        settings['albumid'] = albums[int(input("Какой альбом будем выгружать? "))]['id']
        print()
        settings['count'] = input("Какое количество фотографий будем выгружать? ")
        print()
        settings['path'] = input("В какую папку будем выгружать? ")
        if settings['path'] in os.listdir(os.getcwd()):
            shutil.rmtree(os.path.join(os.getcwd(), settings['path']))
        os.mkdir(settings['path'])
        os.mkdir(f'{settings["path"]}/json')
        vk.savephotos(vk.getalbuminfo(settings['listid'], settings['albumid'], settings['count']), settings['path'])
        menu(0)


def yaupload():
    initresult = yandexinit(get_setting('yandextoken'))
    while initresult == 'retry':
        initresult = yandexinit(get_setting('yandextoken'))
    if initresult == 'passed':
        photobase = getbase()
        settings = {"folderpath": "", 'yandexpath': "", "overwrite": ""}
        if not photobase:
            print('Ошибка! Ваша база данных пуста! Для начала загрузите фото!')
            return
        else:
            print()
            print('Ваша база данных:')
            for num, folder in enumerate(photobase):
                print(f'{num}. {folder}')
            settings['folderpath'] = photobase[int(input("Какую папку будем загружать?(номер) "))]
        settings['yandexpath'] = input("В какую папку на Яндекс.Диск будем загружать? ")
        if input("Разрешить перезапись файлов?(y/n): ") == 'y':
            settings["overwrite"] = 'true'
        else:
            settings["overwrite"] = 'false'
        yadisk = Diskapi(get_setting('yandextoken'))
        yadisk.newfolder(settings['yandexpath'])
        toupload = os.listdir(settings["folderpath"])
        for file in toupload:
            if '.jpg' not in file:
                toupload.remove(file)
        for counter, file in enumerate(toupload):
            uploadfile = (os.path.join(os.getcwd(), settings["folderpath"], file))
            href = yadisk.getuploadlink(settings["yandexpath"], file, settings["overwrite"])
            yadisk.uploadphotos(href, uploadfile)
            print(f'| {int(counter / len(toupload) * 100)}% | Файл {file} успешно загружен!')
        print("| 100% | Задание успешно выполнено!")
        if 'json' in os.listdir(settings["folderpath"]):
            if input("Загрузить json? (y/n): ") == 'y':
                yadisk.newfolder(f'{settings["yandexpath"]}/json')
                jsonpath = os.listdir(os.path.join(os.getcwd(), settings["folderpath"], 'json'))
                for count, file in enumerate(jsonpath):
                    uploadfile = (os.path.join(os.getcwd(), f'{settings["folderpath"]}/json', file))
                    href = yadisk.getuploadlink(f'{settings["yandexpath"]}/json', file, settings["overwrite"])
                    yadisk.uploadphotos(href, uploadfile)
                    print(f'| {int(count / len(jsonpath) * 100)}% | Файл {file} успешно загружен!')
                print("| 100% | Задание успешно выполнено!")


def yadownload():
    initresult = yandexinit(get_setting('yandextoken'))
    while initresult == 'retry':
        initresult = yandexinit(get_setting('yandextoken'))
    if initresult == 'passed':
        yadisk = Diskapi(get_setting('yandextoken'))
        yafolders = []
        settings = {'yandexpath': '/'}
        for obj in yadisk.getfilelist(settings['yandexpath']):
            if obj['type'] == 'dir':
                yafolders.append(obj['name'])
        print("Ваши папки на Яндекс.Диске: \n")
        for num, folder in enumerate(yafolders):
            print(f'{num}. {folder}')
        settings['yandexpath'] = yafolders[int(input("С какой папкой будем работать?(номер) "))]
        files = {'images': [], 'other': [], 'json': 'false'}
        for obj in yadisk.getfilelist(settings['yandexpath']):
            if obj['type'] == 'file' and obj['media_type'] == 'image':
                files['images'].append({'filename': obj['name'], 'yapath': obj['path']})
            else:
                if obj['type'] == 'dir' and obj['name'] == 'json':
                    files['json'] = 'true'
                else:
                    files['other'].append({'filename': obj['name'], 'yapath': obj['path']})
        print(f'В папке {len(files["images"])} фотографий, {len(files["other"])} остальных файлов')
        settings['savefolder'] = input("В какую папку будем выгружать фото? ")
        if settings['savefolder'] in os.listdir(os.getcwd()):
            shutil.rmtree(os.path.join(os.getcwd(), settings['path']))
        os.mkdir(settings['savefolder'])
        for file in files['images']:
            print(os.path.join(os.getcwd(), settings['savefolder'], file['filename']))
            yadisk.savefile(yadisk.getdownloadlink(file['yapath']),
                            os.path.join(os.getcwd(), settings['savefolder'], file['filename']))


def vkupload():
    initresult = initvk(get_setting('vktoken'))
    while initresult == 'retry':
        initresult = initvk(get_setting('vktoken'))
    if initresult == 'passed':
        vk = Vkapi(get_setting('vktoken'))
        settings = {}
        photobase = getbase()
        if not photobase:
            print('Ошибка! Ваша база данных пуста! Для начала загрузите фото!')
            menu(0)
        else:
            print()
            print('Ваша база данных:')
            for num, folder in enumerate(photobase):
                print(f'{num}. {folder}')
        settings["folder"] = photobase[int(input("Какую папку будем загружать?(номер) "))]
        settings["tittle"] = input('Введите название для нового альбома: ')
        settings["albumid"] = vk.newalbum(settings['tittle'])
        settings["uploadurl"] = vk.getuploadlink(settings['albumid'])
        files = []
        for file in os.listdir(os.path.join(os.getcwd(), settings["folder"])):
            if '.jpg' in file:
                files.append(os.path.join(os.getcwd(), settings["folder"], file))
        for num, photo in enumerate(files):
            vk.uploadphoto(settings["uploadurl"], photo, settings['albumid'])
            print(f'| {int(num / len(files) * 100)} % | Файл {photo} успешно загружен!')
            time.sleep(0.5)
        print("| 100% | Задание успешно выполнено!")
        menu(0)


def yandexinit(token):
    yadisk = Diskapi(token)
    response = yadisk.getinfo()
    if token == 'not found':
        print('Ошибка! Токен Яндекс не найден')
        write_setting('yandextoken', input('Введите Ваш токен Яндекс: '))
        return'retry'
    if 'error' in response:
        print(f'Ошибка! {response["error"]}')
        write_setting('yandextoken', input('Введите Ваш токен Яндекс: '))
        return 'retry'
    else:
        print(f'Авторизация успешна! Логин: {response["user"]["login"]}')
        return 'passed'


def menu(choise):
    while choise != 'q':
        print('1. Выгрузить фотографии из альбома VK\n'
              '2. Выгрузить фотографии из Яндекс.Диск\n'
              '3. Выгрузить фотографии из Google Drive\n'
              '4. Загрузить фотографии в альбом VK\n'
              '5. Загрузить фотографии в папку Яндекс.Диск\n'
              '6. Загрузить фотографии в папку Google Drive\n'
              '7. Локальная база данных\n'
              '8. Удалить токен VK API\n'
              '9. Удалить токен Yandex.Polygon\n'
              '10. Удалить токен Google Drive\n'
              'q. Выход из программы\n')
        choise = input("Выберите пункт меню: ")
        if choise == '1':
            print()
            vkdownload()
            break
        if choise == '2':
            print()
            yadownload()
            break
        if choise == '3':
            print()
            print("К сожалению, функция в стадии разработки :(")
            break
        if choise == '4':
            print()
            vkupload()
            break
        if choise == '5':
            print()
            yaupload()
            break
        if choise == '6':
            print()
            print("К сожалению, функция в стадии разработки :(")
            break
        if choise == '7':
            print()
            base()
            break
        if choise == '8':
            print()
            write_setting('vktoken', '')
            print("Токен успешно удалён")
            break
        if choise == '9':
            print()
            write_setting('yandextoken', '')
            print("Токен успешно удалён")
            break
        if choise == '10':
            print()
            write_setting('googletoken', '')
            print("Токен успешно удалён")
            break
    else:
        print('До свидания!')
        sys.exit()


class Vkapi:
    def __init__(self, token: str):
        self.token = token

    def getalbuminfo(self, owner_id, album, count):
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
            info.append({"likes": photo['likes']['count'],
                         'id': photo['id'],
                         'url': photo['sizes'][-1]['url'],
                         'date': photo['date']})
        return info

    def savephotos(self, info, path):
        for counter, photo in enumerate(info):
            response = requests.get(photo['url'])
            dir_path = os.path.join(os.getcwd(), path)
            name = photo["likes"]
            if os.path.exists(os.path.join(dir_path, f'{name}.jpg')):
                name = f'{photo["likes"]}_{photo["id"]}'
            with open(os.path.join(dir_path, f'{name}.jpg'), 'wb') as jpg:
                jpg.write(response.content)
            with open(os.path.join(dir_path, 'json', f'{name}.json'), 'w') as jsonfile:
                json.dump({'filename': f'{name}.jpg',
                           'date': photo['date'],
                           'photo_id': photo['id'],
                           'likes': photo['likes']}, jsonfile)
            print(f'| {int(counter / len(info) * 100)}% | Фотография {name}.jpg успешно загружена!')
        print(f'| 100% | Задание успешно выполнено!')

    def getinfo(self):
        response = requests.get('https://api.vk.com/method/users.get',
                                params={'access_token': self.token, 'v': '5.131'})
        return response.json()

    def getfriends(self):
        profiles = [{'name': 'Мой профиль', 'id': ''}]
        response = requests.get('https://api.vk.com/method/friends.get',
                                params={'access_token': self.token, 'v': '5.131', 'fields': 'contacts'})
        for friend in response.json()['response']['items']:
            profiles.append({'name': f'{friend["first_name"]} {friend["last_name"]}', 'id': friend['id']})
        return profiles

    def getalbums(self, ownerid):
        albums = []
        response = requests.get('https://api.vk.com/method/photos.get',
                                params={'access_token': self.token,
                                        'v': '5.131',
                                        'owner_id': ownerid,
                                        'album_id': 'profile'})
        response = response.json()['response']['count']
        albums.append({'name': 'Фотографии профиля', 'id': 'profile', 'count': response})
        response = requests.get('https://api.vk.com/method/photos.get',
                                params={'access_token': self.token, 'v': '5.131', 'owner_id': ownerid,
                                        'album_id': 'wall'})
        response = response.json()['response']['count']
        albums.append({'name': 'Фотографии со стены', 'id': 'wall', 'count': response})
        response = requests.get('https://api.vk.com/method/photos.getAlbums',
                                params={'access_token': self.token, 'v': '5.131', 'owner_id': ownerid})
        for album in response.json()['response']['items']:
            albums.append({'name': album['title'], 'id': album['id'], 'count': album['size']})
        return albums

    def newalbum(self, tittle):
        response = requests.get('https://api.vk.com/method/photos.createAlbum',
                                params={'access_token': self.token, 'v': '5.131', 'title': tittle})
        return response.json()['response']['id']

    def getuploadlink(self, albumid):
        response = requests.get('https://api.vk.com/method/photos.getUploadServer',
                                params={'access_token': self.token, 'v': '5.131', 'album_id': albumid})
        return response.json()['response']['upload_url']

    def uploadphoto(self, upload_url, file, albumid):
        response = requests.post(upload_url, files={'file': open(file, 'rb')})
        requests.get('https://api.vk.com/method/photos.save',
                     params={'access_token': self.token, 'v': '5.131',
                             'aid': response.json()['aid'],
                             'hash': response.json()['hash'],
                             'photos_list': response.json()['photos_list'],
                             'server': response.json()['server'],
                             'album_id': albumid})


class Diskapi:
    def __init__(self, token: str):
        self.token = token

    def getuploadlink(self, path, file, overwrite):
        url = 'https://cloud-api.yandex.net:443/v1/disk/resources/upload'
        headers = {'Content-Type': 'application/json', 'Authorization': self.token}
        response = requests.get(url, headers=headers, params={'path': f'{path}/{file}', 'overwrite': overwrite})
        return response.json()['href']

    def uploadphotos(self, href, path):
        requests.put(href, data=open(path, 'rb'))

    def getinfo(self):
        response = requests.get('https://cloud-api.yandex.net:443/v1/disk',
                                headers={'Content-Type': 'application/json', 'Authorization': self.token})
        return response.json()

    def newfolder(self, path):
        requests.put('https://cloud-api.yandex.net:443/v1/disk/resources',
                     headers={'Content-Type': 'application/json', 'Authorization': self.token},
                     params={'path': path})

    def getfilelist(self, path):
        response = requests.get('https://cloud-api.yandex.net:443/v1/disk/resources',
                                headers={'Content-Type': 'application/json', 'Authorization': self.token},
                                params={'path': path, 'limit': '500'})
        return response.json()['_embedded']['items']

    def getdownloadlink(self, path):
        response = requests.get('https://cloud-api.yandex.net:443/v1/disk/resources/download',
                                headers={'Content-Type': 'application/json', 'Authorization': self.token},
                                params={'path': path})
        return response.json()['href']

    def savefile(self, href, path):
        response = requests.get(href)
        with open(os.path.join(path), 'wb') as jpg:
            jpg.write(response.content)


if __name__ == "__main__":
    menu(0)
