import os
import configparser
from asset_selector import return_assets_dicts
import file_mngr.logs_mngr as logmn
config = configparser.ConfigParser()


def check_path(path):
    return os.path.exists(path)


def remove_file(path):
    os.remove(path)


def create_path(path):
    os.makedirs(path)


def return_contents(path):
    return os.listdir(path)


def set_settings(section, setting):
    return config.get(section, setting)


def update_setting(section, setting, value):
    config.set(section, setting, value)
    with open("settings/settings.ini", "w") as config_file:
        config.write(config_file)


def create_sprites_and_audio_paths(dct: dict):
    '''
    this is made specifically for setting sprites and audio paths from a dictionary in asset_selector
    :param dct: dict, where the key is 'Sprites' or 'Audio', with values being other dicts with their relative items
    :return: None
    '''
    change_flag = False
    for section in dct.keys():  # Sprites or Audio
        for setting in dct.get(section):  # Keys for their relative dicts
            for value in dct.get(section).get(setting):
                try:
                    config.read('settings/settings.ini')
                    config.get(section, f'{setting.lower()}_{value.lower()}')
                except:
                    config.read('settings/settings.ini')
                    found_flag = False
                    if not change_flag:
                        change_flag = True
                    for i in return_contents(f'assets/{section.lower()}/{setting.lower()}/{value.lower()}'):
                        if i.startswith('[DEFAULT]'):
                            print(f"setting {section}, '{setting.lower()}_{value.lower()}' to 'assets/{section.lower()}/{setting.lower()}/{value.lower()}/{i}'")
                            logmn.log_info(f"setting {section}, '{setting.lower()}_{value.lower()}' to 'assets/{section.lower()}/{setting.lower()}/{value.lower()}/{i}'")
                            config.set(section, f'{setting.lower()}_{value.lower()}',
                                       f'assets/{section.lower()}/{setting.lower()}/{value.lower()}/{i}')
                            found_flag = True
                            break
                    if not found_flag:
                        print(f"setting {section}, '{setting.lower()}_{value.lower()}' to None")
                        logmn.log_info(f"setting {section}, '{setting.lower()}_{value.lower()}' to None")
                        config.set(section, f'{setting.lower()}_{value.lower()}', 'None')
    if change_flag:
        with open("settings/settings.ini", "w") as c_file:
            config.write(c_file)


def load_settings():
    if not os.path.isfile("settings/settings.ini"):
        print('settings not in dir!')
        logmn.log_warning('settings not in dir!')
        create_settings()
        print('default settings set')
        logmn.log_info('default settings set')
    try:
        config.read("settings/settings.ini")
    except Exception as e:
        print(f'settings corrupted, setting to default... error: {e}')  # i dont really know what should you do to get here but whatever, failsafe rulez
        logmn.log_error('settings corrupted, setting to default...')
        os.remove('settings/setting.ini')
        create_settings()
        print('default settings set')
        logmn.log_info('default settings set')
    print('loading settings...')
    logmn.log_info('loading settings...')
    return config.read("settings/settings.ini")


def create_settings():
    # try doing a failsafe check for max win width and height, do less and less until the possible minimum has been
    # reached, after which a system message pops up with the error, also closing the whole game
    if not os.path.exists("settings"):
        os.makedirs("settings")
        print('created dir settings')
        logmn.log_info('created dir settings')
    config.add_section("Settings")
    config.set("Settings", "win_width", "1280")
    config.set("Settings", "win_height", "720")
    config.set("Settings", "bg_volume", "0.5")
    config.set("Settings", "sfx_volume", "0.5")
    config.add_section("Controls")
    config.set("Controls", "up", "W")
    config.set("Controls", "left", "A")
    config.set("Controls", "down", "S")
    config.set("Controls", "right", "D")
    config.set("Controls", "shoot", "SPACE")
    config.add_section("Audio")
    config.add_section("Sprites")
    create_sprites_and_audio_paths(return_assets_dicts())

    with open("settings/settings.ini", "w") as c_file:
        config.write(c_file)
