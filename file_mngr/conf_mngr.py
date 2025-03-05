import os
import configparser

config = configparser.ConfigParser()


def check_path(path):
    return os.path.exists(path)

def create_path(path):
    return os.makedirs(path)

def return_contents(path):
    return os.listdir(path)


def set_settings(section, setting):
    return config.get(section, setting)


def update_setting(section, setting, value):
    config.set(section, setting, value)
    with open("settings/settings.ini", "w") as config_file:
        config.write(config_file)


def load_settings():
    if not os.path.isfile("settings/settings.ini"):
        print('settings not in dir!')
        create_settings()
        print('default settings set')
    try:
        config.read("settings/settings.ini")
    except:
        print('settings corrupted, settings to default...')
        create_settings()
        print('default settings set')
    print('loading settings!')
    return config.read("settings/settings.ini")


def create_settings():
    # try doing a failsafe check for max win width and height, do less and less until the possible minimum has been
    # reached, after which a system message pops up with the error, also closing the whole game
    if not os.path.exists("settings"):
        os.makedirs("settings")
    config.add_section("Settings")
    config.set("Settings", "win_width", "1280")
    config.set("Settings", "win_height", "720")
    config.set("Settings", "bg_music", "assets/audio/music/main menu/cuboidd_[MC Detour].mp3")
    config.set("Settings", "bg_volume", "0.5")
    config.set("Settings", "player_sprite", "assets/sprites/player/kestrel-cruiser-type-b-body.png")
    config.set("Settings", "pl_bul_sprite", "assets/sprites/entities/player_bullet.png")
    config.set("Settings", "pl_bul_audio", "assets/sounds/pew.wav")
    config.set("Settings", "pl_crsh_sprite", "assets/sprites/player/crosshair.png")
    config.add_section("Controls")
    config.set("Controls", "up", "W")
    config.set("Controls", "left", "A")
    config.set("Controls", "down", "S")
    config.set("Controls", "right", "D")
    config.set("Controls", "shoot", "SPACE")

    with open("settings/settings.ini", "w") as c_file:
        config.write(c_file)
