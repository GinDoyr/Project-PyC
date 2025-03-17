import arcade
import zipfile
import file_mngr.conf_mngr as conf


def load_resourcepack(path):
    '''
    load a resourcepack, aka set the paths in setting.ini for each of the CORRECTLY PLACED asset in the resourcepack
    was meant to be something of a temporary change of paths, but didnt make it work :(
    :param path: path to resourcepack, must be .zip!
    '''
    conf.logmn.log_info(f'trying to load resourcepack: {path}')
    archive = zipfile.ZipFile(path, 'r')
    data = archive.namelist()
    dicts = conf.return_assets_dicts()
    existing_paths = []
    for section in dicts.keys():  # Sprites or Audio
        for setting in dicts.get(section):  # Keys for their relative dicts
            for value in dicts.get(section).get(setting):
                existing_paths.append(f'assets/{section.lower()}/{setting.lower()}/{value.lower()}/')

    conf.load_settings()
    for i in data:
        if not i.endswith('/') and i.startswith(tuple(existing_paths)):
            temp_path = i[i.find('/')+1:].split('/')
            conf.update_setting(temp_path[0].title(), f'{temp_path[1]}_{temp_path[2]}', 'temp/'+i)
            conf.logmn.log_info(f'set a temporary asset from resourcepack {path}: {temp_path[0].title()}, {temp_path[1]}_{temp_path[2]}, temp/{i}')
    conf.logmn.log_info(f'fully loaded and set the assets from resourcepack {path}')


def load_from_resourcepack(rspk_path, section, setting, streaming=False, scale=1.0):
    '''
    load texture/audio from a resourcepack by temporarily extracting the file and assigning it to supported type
    group extraction is planned but highly unlikely
    currently texture supports only static images, as i still haven't figured out how i wanted to do animated stuff
    :param rspk_path: path to resourcepack (should've probably just made it a name but i think path is a bit safer ok)
    :param section: section in settings.ini
    :param setting: setting in settings.ini
    :param streaming: for arcade's audio streaming, default False
    :param scale: for arcade's sprites, default 1.0, change either with a tuple (x,y) or a float
    :return: arcade.Sprite or arcade.Sound depending on what was chosen
    '''
    conf.logmn.log_info(f'starting to load asset on {section}-{setting} from resourcepack {rspk_path}')
    archive = zipfile.ZipFile(rspk_path, 'r')
    asset_path = conf.set_settings(section, setting)
    if asset_path.startswith('temp'):
        conf.logmn.log_info('resourcepack loaded, asset found in setting.ini, extracting...')
        if not conf.check_path('temp'):
            conf.create_path('temp')
        archive.extract(asset_path[asset_path.find('/')+1:], 'temp')
        result = None
        if section == 'Sprites':
            result = arcade.Sprite(asset_path, scale)
        elif section == 'Audio':
            result = arcade.load_sound(asset_path, streaming)
        else:
            conf.logmn.log_error('incorrect section, how the hell did you get here???')
            raise Exception('incorrect section, how the hell did you get here???')
        if result is not None:
            conf.logmn.log_info('loaded the asset, deleting temp file...')
            conf.remove_path('temp', True)
            return result
    else:
        conf.logmn.log_warning('no asset found from resourcepack, abort')
        raise Exception('no asset found from resourcepack, abort')


def try_loading_from_resourcepack(rspk_path, section, setting, streaming=False, scale=1.0):
    """
    BASICALLY load_from_resourcepack, but either returns the found file from pack or sets the one in the settings
    load texture/audio from a resourcepack by temporarily extracting the file and assigning it to supported type
    group extraction is planned but highly unlikely
    currently texture supports only static images, as i still haven't figured out how i wanted to do animated stuff
    :param rspk_path: path to resourcepack (should've probably just made it a name but i think path is a bit safer ok)
    :param section: section in settings.ini
    :param setting: setting in settings.ini
    :param streaming: for arcade's audio streaming, default False
    :param scale: for arcade's sprites, default 1.0, change either with a tuple (x,y) or a float
    :return: arcade.Sprite or arcade.Sound depending on what was chosen
    """
    try:
        return load_from_resourcepack(rspk_path, section, setting, streaming, scale)
    except:
        if section == 'Audio':
            return arcade.load_sound(conf.set_settings(section, setting), streaming=streaming)
        else:
            return arcade.Sprite(conf.set_settings(section, setting), scale=scale)
