import zipfile
archive = zipfile.ZipFile('resourcepacks/assets.zip', 'r')
data = archive.namelist()
dicts = {'Sprites': {'Player': ['Sprite', 'Bullet', 'Crosshair'],
                     'Enemies': ['Enemy1', 'Enemy1 explosion', 'Enemy2', 'Enemy2 fire', 'Enemy3',
                                 'Enemy3 fire', 'Boss', 'Boss charge', 'Boss laser'],
                     'Other': ['Background', 'Walls', 'Lives']},
         'Audio': {'Player': ['Bullet', 'Dash', 'Death'],
                   'Enemies': ['Enemy1 rush', 'Enemy1 explosion', 'Enemy1 death', 'Enemy2 death',
                               'Enemy3 death', 'Boss charge', 'Boss fire', 'Boss death'],
                   'Other': ['Live lost', 'Live regained'],
                   'Music': ['Main menu', 'Game', 'Boss']}}
print(dicts)
print(data)
