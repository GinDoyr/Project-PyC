import zipfile, arcade
from file_mngr.conf_mngr import return_assets_dicts, remove_path, create_path, load_settings, set_settings, remove_file, update_setting

archive = zipfile.ZipFile('resourcepacks/assets.zip', 'r')
data = archive.namelist()
dicts = return_assets_dicts()
existing_paths = []
print(dicts)
for section in dicts.keys():  # Sprites or Audio
    for setting in dicts.get(section):  # Keys for their relative dicts
        for value in dicts.get(section).get(setting):
            print(section, setting, value)
            existing_paths.append(f'assets/{section.lower()}/{setting.lower()}/{value.lower()}/')
data_full_paths = []

load_settings()
for i in data:
    if not i.endswith('/') and i.startswith(tuple(existing_paths)):
        temp_path = i[i.find('/')+1:].split('/')
        print(temp_path)
        update_setting(temp_path[0].title(), f'{temp_path[1]}_{temp_path[2]}', 'temp/'+i)
        data_full_paths.append(i)
print(data_full_paths)


# this is where the fun begins
create_path('temp')
archive.extract(data_full_paths[0], 'temp')
sprite = arcade.Sprite(set_settings('Sprites', 'player_sprite'))
remove_file('temp/'+data_full_paths[0])
remove_path('temp', True)

class view(arcade.View):
    def __init__(self):
        super().__init__()

        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(sprite)
        sprite.position = self.center

    def on_update(self, delta_time: float):
        self.sprite_list.update(delta_time)
        self.sprite_list.update_animation()

    def on_draw(self):
        self.clear()
        self.sprite_list.draw()

window = arcade.Window(1000, 500)
view = view()
window.show_view(view)
arcade.run()