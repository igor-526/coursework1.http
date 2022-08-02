def get_setting(sett):
    settings = {}
    with open("settings.ini") as setting:
        for line in setting.readlines():
            line = (line.strip("\n").split(" : "))
            settings[line[0]] = line[1]
    return settings[sett]


print(get_setting('yandextoken'))
