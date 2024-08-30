import configparser


def get_config(cfg_path):
    settings = {}
    parser = configparser.ConfigParser()
    parser.read(cfg_path, encoding="utf-8")
    for section in parser:
        for value in parser[section]:
            settings[value] = parser[section][value].strip("'\"")

    return settings
