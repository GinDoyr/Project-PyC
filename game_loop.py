import arcade
import arcade.clock
from arcade.math import rotate_point
import file_mngr.conf_mngr as conf
import file_mngr.zip_mngr as zipmn
from png_lsb_stuff.gif_to_sprite import gifSprite
from difficulties.diftest import read_and_return_enemies
import player
import enemies
import math
import numpy as np


def rotate_around_point(sprite, point, degrees):
    sprite.position = rotate_point(
        sprite.center_x, sprite.center_y,
        point[0], point[1], degrees)


def random_enemy_xy(enemy_size, width, height, pl_pos, wall):
    '''
    :param enemy_size: enemy width and height
    :param width: area width
    :param height: area height
    :param pl_pos: player position (x, y)
    :param wall: wall from gameview
    :return: random x and y
    '''
    one = np.random.randint(0, 2)
    two = np.random.randint(0, 2)
    enwidth = enemy_size[0]
    enheight = enemy_size[1]
    if (one or not (not one and pl_pos[0] - 300 > wall.width + enwidth)) and pl_pos[0] \
            + 300 < width - wall.width - enwidth:
        x = np.random.randint(pl_pos[0] + 300, width - wall.width - enwidth)
    else:
        x = np.random.randint(wall.width + enwidth, pl_pos[0] - 300)
    if (two or not (not two and pl_pos[1] - 300 > wall.height + enheight)) and pl_pos[1] \
            + 300 < height - wall.height - enheight:
        y = np.random.randint(pl_pos[1] + 300, height - wall.height - enheight)
    else:
        y = np.random.randint(wall.height + enheight, pl_pos[1] - 300)
    try:
        return x, y
    except Exception as e:
        conf.logmn.log_warning(f'failed to create random x, y for enemy! {e}')


def point_enemy_to_player(pl_x, pl_y, en_x, en_y):
    return -math.atan2(pl_y - en_y, pl_x - en_x) + 3.14 / 2


class GameLoop(arcade.View):
    def __init__(self, main_menu, difficulty):
        super().__init__()
        # commented for now, resolve later
        # self.window.width, self.window.height = self.window.width//3, 7*self.window.height//8
        # self.window.center_window()

        conf.logmn.log_info(f'launching game loop, difficulty {difficulty}')
        print(f'launching game loop, difficulty {difficulty}')

        # misc
        self.clocker = arcade.clock.Clock()  # i dunno why all of these are called clockers lol
        # also note: might be a bad thing spamming these clocks, maybe replace them all with one clock and do some like
        # starting ticks for the things that need it? like recharge started on tick 10, set st. tick to 10, and do stuff
        self.danger_clocker = arcade.clock.Clock()
        self.iframes_clocker = arcade.clock.Clock()
        self.death_clocker = arcade.clock.Clock()
        self.pl_dash_clocker = arcade.clock.Clock()  # dude stop with the clockers lol
        self.dash_outlines_clocker = arcade.clock.Clock()
        self.pl_parry_clocker = arcade.clock.Clock()
        self.parry_draw_clocker = arcade.clock.Clock()
        self.wave_rchg_clocker = arcade.clock.Clock()
        self.text_overlay_clocker = arcade.clock.Clock()
        self.boss_shield_clocker = arcade.clock.Clock()
        self.boss_shielded_clocker = arcade.clock.Clock()
        self.boss_attack_clocker = arcade.clock.Clock()
        self.boss_recharge_clocker = arcade.clock.Clock()
        self.main_menu = main_menu
        self.area_x, self.area_y = 2000, 2000
        self.mouse_x, self.mouse_y = self.window.center
        self.score_text = arcade.Text("Score: 0", self.window.width - 10, self.window.height - 25, arcade.color.WHITE,
                                      anchor_x="right", anchor_y='center', font_name='Arcade Normal')
        self.wave_count = 0
        self.wave_text = arcade.Text("Wave: 0", self.window.width - 50 - self.score_text.content_width,
                                     self.window.height-25, arcade.color.WHITE, anchor_x="right", anchor_y='center', font_name='Arcade Normal')

        # sound
        self.curr_audio = None
        self.boss_bg_player = None
        self.warning_player = None
        self.bg_volume = float(conf.set_settings("Settings", "bg_volume"))
        self.sfx_volume = float(conf.set_settings("Settings", "sfx_volume"))

        # flags
        self.bg_flag = False
        self.resize_flag = False
        self.shoot_flag = False # pl bullet ready to shoot todo move to player
        self.recharge_flag = False  # pl bullet recharges
        self.flash_flag = False
        self.mouse_flag = True
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.dash_pressed = False
        self.parry_pressed = False
        self.game_over = False
        self.text_overlay_shown = {}  # serves as a check list, if text is in, then True, yadayada
        self.text_to_show = []
        self.text_complete = []
        self.wave_added = False

        # loading stuff
        # PLEASE MAKE SURE SPRITE LOOKS UP! mb make a confirm window to adjust the import sprite angle?
        if conf.set_settings('Settings', 'resourcepack') != 'None':  # ok so i've made some function but still looks like a mess. or not. idk, but it works :D
            zipmn.load_resourcepack(conf.set_settings('Settings', 'resourcepack'))
            self.bg_music = zipmn.try_loading_from_resourcepack('Audio', 'music_game', streaming=True)
            player_sprite = zipmn.try_loading_from_resourcepack('Sprites', 'player_sprite')
            pl_bullet_sprite = zipmn.try_loading_from_resourcepack('Sprites', 'player_bullet').texture
            self.pl_crsh = zipmn.try_loading_from_resourcepack('Sprites', 'player_crosshair')
            self.pl_lives = zipmn.try_loading_from_resourcepack('Sprites', 'other_lives').texture
            self.pl_dash_audio = zipmn.try_loading_from_resourcepack('Audio', 'player_dash')
            self.pl_dash_chrg_audio = zipmn.try_loading_from_resourcepack('Audio', 'player_dash recharged')
            self.pl_parry_audio = zipmn.try_loading_from_resourcepack('Audio', 'player_parry')
            self.pl_parry_chrg_audio = zipmn.try_loading_from_resourcepack('Audio', 'player_parry recharged')
            self.pl_parry_spark = zipmn.try_loading_from_resourcepack('Sprites', 'player_parry spark', gif_onetime=True, gif_speed=0.5)
            pl_bullet_audio = zipmn.try_loading_from_resourcepack('Audio', 'player_bullet')
            banz_sprite = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_enemy1').texture
            banz_flash = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_enemy1 flash').texture
            banz_death = zipmn.try_loading_from_resourcepack('Audio', "enemies_enemy1 death")
            banz_rush = zipmn.try_loading_from_resourcepack('Audio', 'enemies_enemy1 rush')
            banz_explsound = zipmn.try_loading_from_resourcepack('Audio', 'enemies_enemy1 explosion')
            self.banz_explspr = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_enemy1 explosion',
                                                                    gif_onetime=True, gif_speed=0.5)
            self.banz_deathspr = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_enemy1 death',
                                                                     gif_onetime=True, gif_speed=0.5)
            stshoot_sprite = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_enemy2').texture
            stshoot_fire1spr = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_enemy2 fire', gif_onetime=True,
                                                                   gif_speed=0.5)
            stshoot_fire2spr = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_enemy2 constfire', gif_speed=0.5)
            stshoot_deathspr = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_enemy2 death', gif_onetime=True,
                                                                   gif_speed=0.5)
            stshoot_fire1snd = zipmn.try_loading_from_resourcepack('Audio', 'enemies_enemy2 fire')
            stshoot_fire2snd = zipmn.try_loading_from_resourcepack('Audio', 'enemies_enemy2 constfire')
            stshoot_deathsnd = zipmn.try_loading_from_resourcepack('Audio', 'enemies_enemy2 death')
            self.hitmark = zipmn.try_loading_from_resourcepack('Sprites', 'other_hitmark', gif_onetime=True,
                                                               gif_speed=0.5)
            self.pl_hit = zipmn.try_loading_from_resourcepack('Audio', 'player_hit')
            self.oneup = zipmn.try_loading_from_resourcepack('Sprites', 'other_oneup', gif_speed=0.5)
            self.oneupsnd = zipmn.try_loading_from_resourcepack('Audio', 'other_oneup')
            self.pl_death = zipmn.try_loading_from_resourcepack('Sprites', 'player_death', gif_onetime=True,
                                                                gif_speed=0.1)
            self.pl_deathsnd = zipmn.try_loading_from_resourcepack('Audio', 'player_death')
            self.pl_predeathsnd = zipmn.try_loading_from_resourcepack('Audio', 'player_predeath')
            self.wave_clear_audio = zipmn.try_loading_from_resourcepack('Audio', 'other_wave clear')
            self.pl_wave1spr = zipmn.try_loading_from_resourcepack('Sprites', 'player_wave', gif_onetime=True, gif_speed=0.2)
            self.pl_wave2spr = zipmn.try_loading_from_resourcepack('Sprites', 'player_wave const', gif_speed=0.6)
            self.pl_wavesnd = zipmn.try_loading_from_resourcepack('Audio', 'player_wave')
            boss_spr = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_boss')
            self.boss_deathspr = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_boss death', gif_onetime=True, gif_speed=0.3)
            self.boss_laser = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_boss laser', gif_speed=0.25)
            self.boss_laserchrg = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_boss charge', gif_speed=0.3)
            self.boss_lasersnd = zipmn.try_loading_from_resourcepack('Audio', 'enemies_boss fire')
            self.boss_locking = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_boss locking')
            self.boss_lockedon = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_boss locked', gif_speed=0.3)
            self.boss_deathaud = zipmn.try_loading_from_resourcepack('Audio', 'enemies_boss death')
            self.boss_shieldsspr = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_boss shield', gif_speed=0.3)
            self.boss_chargeaud = zipmn.try_loading_from_resourcepack('Audio', 'enemies_boss charge')
            self.boss_shield_hitaud = zipmn.try_loading_from_resourcepack('Audio', 'enemies_boss shieldhit')
            self.warning_sound = zipmn.try_loading_from_resourcepack('Audio', 'other_warning')
            self.boss_bg_sound = zipmn.try_loading_from_resourcepack('Audio', 'music_boss')
            self.spawn_thunder = zipmn.try_loading_from_resourcepack('Sprites', 'other_spawn thunder', gif_speed=0.5, gif_onetime=True)
            self.spawn_orb = zipmn.try_loading_from_resourcepack('Sprites', 'other_spawn orb', True, 0.5)
        else:
            self.bg_music = arcade.load_sound(conf.set_settings('Audio', 'music_game'), streaming=True)
            player_sprite = arcade.Sprite(conf.set_settings('Sprites', 'player_sprite'))
            pl_bullet_sprite = arcade.Sprite(conf.set_settings('Sprites', 'player_bullet')).texture
            self.pl_crsh = arcade.Sprite(conf.set_settings("Sprites", "player_crosshair"))
            self.pl_lives = arcade.Sprite(conf.set_settings('Sprites', 'other_lives')).texture
            self.pl_dash_audio = arcade.load_sound(conf.set_settings('Audio', 'player_dash'))
            self.pl_dash_chrg_audio = arcade.load_sound(conf.set_settings('Audio', 'player_dash recharged'))
            self.pl_parry_audio = arcade.load_sound(conf.set_settings('Audio', 'player_parry'))
            self.pl_parry_chrg_audio = arcade.load_sound(conf.set_settings('Audio', 'player_parry recharged'))
            self.pl_parry_spark = gifSprite(conf.set_settings('Sprites', 'player_parry spark'), True, 0.5)
            pl_bullet_audio = arcade.load_sound(conf.set_settings("Audio", "player_bullet"))
            banz_sprite = arcade.Sprite(conf.set_settings('Sprites', 'enemies_enemy1')).texture
            banz_flash = arcade.Sprite(conf.set_settings('Sprites', 'enemies_enemy1 flash')).texture
            banz_death = arcade.load_sound(conf.set_settings('Audio', "enemies_enemy1 death"))
            banz_rush = arcade.load_sound(conf.set_settings('Audio', 'enemies_enemy1 rush'))
            banz_explsound = arcade.load_sound(conf.set_settings('Audio', 'enemies_enemy1 explosion'))
            self.banz_explspr = gifSprite(conf.set_settings('Sprites', 'enemies_enemy1 explosion'), True, 0.5)
            self.banz_deathspr = gifSprite(conf.set_settings('Sprites', 'enemies_enemy1 death'), True, 0.5)
            stshoot_sprite = arcade.Sprite(conf.set_settings('Sprites', 'enemies_enemy2')).texture
            stshoot_fire1spr = gifSprite(conf.set_settings('Sprites', 'enemies_enemy2 fire'), True, 0.1)
            stshoot_fire2spr = gifSprite(conf.set_settings('Sprites', 'enemies_enemy2 constfire'), False, 0.25)
            stshoot_deathspr = gifSprite(conf.set_settings('Sprites', 'enemies_enemy2 death'), True, 0.5)
            stshoot_fire1snd = arcade.load_sound(conf.set_settings('Audio', 'enemies_enemy2 fire'))
            stshoot_fire2snd = arcade.load_sound(conf.set_settings('Audio', 'enemies_enemy2 constfire'))
            stshoot_deathsnd = arcade.load_sound(conf.set_settings('Audio', 'enemies_enemy2 death'))
            self.hitmark = gifSprite(conf.set_settings('Sprites', 'other_hitmark'), True, 0.5)
            self.pl_hit = arcade.load_sound(conf.set_settings('Audio', 'player_hit'))
            self.oneup = gifSprite(conf.set_settings('Sprites', 'other_oneup'), False, 0.5)
            self.oneupsnd = arcade.load_sound(conf.set_settings('Audio', 'other_oneup'))
            self.pl_death = gifSprite(conf.set_settings('Sprites', 'player_death'), True, 0.1)
            self.pl_deathsnd = arcade.load_sound(conf.set_settings('Audio', 'player_death'))
            self.pl_predeathsnd = arcade.load_sound(conf.set_settings('Audio', 'player_predeath'))
            self.wave_clear_audio = arcade.load_sound(conf.set_settings('Audio', 'other_wave clear'))
            self.pl_wave1spr = gifSprite(conf.set_settings('Sprites', 'player_wave'), True, 0.2)
            self.pl_wave2spr = gifSprite(conf.set_settings('Sprites', 'player_wave const'), False, 0.6)
            self.pl_wavesnd = arcade.load_sound(conf.set_settings('Audio', 'player_wave'))
            boss_spr = arcade.Sprite(conf.set_settings('Sprites', 'enemies_boss')).texture
            self.boss_deathspr = gifSprite(conf.set_settings('Sprites', 'enemies_boss death'), True, 0.3)
            self.boss_laserst = gifSprite(conf.set_settings('Sprites', 'enemies_boss laser'), False, 0.25)
            self.boss_laserchrg = gifSprite(conf.set_settings('Sprites', 'enemies_boss charge'), False, 0.3)
            self.boss_lasersnd = arcade.load_sound(conf.set_settings('Audio', 'enemies_boss fire'))
            self.boss_locking = arcade.Sprite(conf.set_settings('Sprites', 'enemies_boss locking'))
            self.boss_lockedon = gifSprite(conf.set_settings('Sprites', 'enemies_boss locked'), False, 0.3)
            self.boss_deathaud = arcade.load_sound(conf.set_settings('Audio', 'enemies_boss death'))
            self.boss_shieldsspr = gifSprite(conf.set_settings('Sprites', 'enemies_boss shield'), False, 0.3)
            self.boss_chargeaud = arcade.load_sound(conf.set_settings('Audio', 'enemies_boss charge'))
            self.boss_shield_hitaud = arcade.load_sound(conf.set_settings('Audio', 'enemies_boss shieldhit'))
            self.warning_sound = arcade.load_sound(conf.set_settings('Audio', 'other_warning'))
            self.boss_bg_sound = arcade.load_sound(conf.set_settings('Audio', 'music_boss'))
            self.spawn_thunder = gifSprite(conf.set_settings('Sprites', 'other_spawn thunder'), True, 0.5)
            self.spawn_orb = gifSprite(conf.set_settings('Sprites', 'other_spawn orb'), True, 0.5)

        # player
        pl_bullet_sprite.width, pl_bullet_sprite.height = 10, 28
        player_sprite.width, player_sprite.height = 64, 64
        self.pl_bullet_speed = 10
        self.pl_bullet_recharge = 10  # higher - slower
        self.player = player.Player(player_sprite, pl_bullet_sprite, pl_bullet_audio)
        self.player.sprite.center_x = self.area_x // 2
        self.player.sprite.center_y = self.area_y // 2
        self.pl_bul_hitbox = arcade.SpriteSolidColor(1, 1, self.player.sprite.center_x, color=(0,0,0,0)) # HEEEY I ACTUALLY FOUND OUT WHAT I CAN DO LOL
        self.pl_bul_hitbox.bottom = self.player.sprite.top
        self.pl_hitplayer = None
        self.pl_predeathplayer = None
        self.weapon_chosen = False

        # banzai
        self.banzai = enemies.Banzai(banz_sprite, banz_flash, banz_rush, banz_explsound, banz_death)

        # static shooter
        self.stshoot = enemies.StaticShooter(stshoot_sprite, stshoot_fire1spr, stshoot_fire2spr, stshoot_fire1snd,
                                             stshoot_fire2snd, stshoot_deathspr, stshoot_deathsnd)

        # boss
        self.boss = enemies.Boss(boss_spr)
        self.boss_att_hitbox = arcade.SpriteSolidColor(1, 1, color=(0,0,0,0))
        self.boss_att_hitbox_spacing = 38

        # background attempt
        self.bg_list = arcade.SpriteList()
        if conf.set_settings('Settings', 'resourcepack') != 'None':
            self.bg_texture = zipmn.try_loading_from_resourcepack('Sprites', 'other_background').texture
        else:
            self.bg_texture = arcade.Sprite(conf.set_settings('Sprites', 'other_background')).texture
        for x in range(0, self.area_x, int(self.bg_texture.width)):
            for y in range(0, self.area_y, int(self.bg_texture.height)):
                background = arcade.Sprite(self.bg_texture)
                background.left, background.bottom = x, y
                self.bg_list.append(background)

        # wall attempt...
        self.wall_sprlist = arcade.SpriteList()
        if conf.set_settings('Settings', 'resourcepack') != 'None':
            self.wall_sprite = zipmn.try_loading_from_resourcepack('Sprites', 'other_walls').texture
        else:
            self.wall_sprite = arcade.Sprite(conf.set_settings('Sprites', 'other_walls')).texture
        for x in range(0, self.area_x + int(self.wall_sprite.width), int(self.wall_sprite.width)):
            if x >= self.area_x:
                x = self.area_x
            for y in range(0, self.area_y + int(self.wall_sprite.height), int(self.wall_sprite.height)):
                if y >= self.area_y:
                    y = self.area_y
                if y == 0 or y == self.area_y:
                    wall = arcade.Sprite(self.wall_sprite)
                    wall.position = x, y
                    self.wall_sprlist.append(wall)
                elif x == 0 or x == self.area_x:
                    wall = arcade.Sprite(self.wall_sprite)
                    wall.position = x, y
                    self.wall_sprlist.append(wall)

        # sprite lists
        self.sprite_list = arcade.SpriteList()
        self.banzai_list = arcade.SpriteList()  # i really didnt want to go this way but whatever, for now
        self.stshoot_list = arcade.SpriteList()
        self.boss_sprlist = arcade.SpriteList()
        self.boss_lock_sprlist = arcade.SpriteList()
        self.plbullets_list = arcade.SpriteList()
        self.enbullets_list = arcade.SpriteList()
        self.dash_outlines_list = arcade.SpriteList()  # for dash outlines
        self.oneup_list = arcade.SpriteList()
        self.gif_list = arcade.SpriteList()
        self.parry_sprites = arcade.SpriteList() # add whatever should be drawn when in parry range (player + spark added automatically)
        self.crosshair = arcade.SpriteList()
        self.danger_zones = {}
        self.crosshair.append(self.pl_crsh)
        self.sprite_list.append(self.player.sprite)
        self.sprite_list.append(self.pl_bul_hitbox)
        self.pl_bul_hitbox.visible = False

        # there's the camera
        self.camera_sprites = arcade.Camera2D()
        self.camera_gui = arcade.Camera2D()
        self.camera_sprites.stop_x = 0
        self.camera_sprites.stop_y = 0
        self.camera_sprites.x_set = False
        self.camera_sprites.y_set = False
        self.moving_x = False
        self.moving_y = False

        # score something something! :D
        self.score = 0

        # difficulty
        diff = {0: 'easy', 1: 'medium', 2: 'doom', 3: 'custom'}
        self.difficulty = diff.get(difficulty)
        self.intdifficulty = difficulty
        self.enemies_spawned = False

        # misc x2 bcs im lazy to go up
        self.blackout_delta = 0
        self.parry_success = False
        self.dash_text = arcade.Text("DASH", 180.0, self.window.height - 25, anchor_y="center", anchor_x="center", font_name='Arcade Normal')
        self.dash_width = 100
        self.parry_text = arcade.Text("PARRY", 300.0, self.window.height - 25, anchor_y="center", anchor_x="center", font_name='Arcade Normal')
        self.parry_width = 100
        self.pl_bul_text = arcade.Text('1', 369, self.window.height-25, anchor_y='center', anchor_x='center', font_name='Arcade Normal')
        self.pl_bul_rchg_height = 40
        self.pl_wave_text = arcade.Text('2', 399, self.window.height-25, anchor_y='center', anchor_x='center', font_name='Arcade Normal')
        self.pl_wave_rchg_height = 40

    def scroll_to_player(self):
        x = self.player.sprite.center_x
        y = self.player.sprite.center_y
        if self.moving_x:
            if not self.camera_sprites.x_set:
                if x >= self.area_x - self.window.width // 2:
                    self.camera_sprites.stop_x = self.area_x - self.window.width // 2
                else:
                    self.camera_sprites.stop_x = self.window.width // 2
                self.camera_sprites.x_set = True
            x = self.camera_sprites.stop_x
        else:
            if self.camera_sprites.x_set:
                self.camera_sprites.x_set = False
        if self.moving_y:
            if not self.camera_sprites.y_set:
                if y >= self.area_y - self.window.height // 2:
                    self.camera_sprites.stop_y = self.area_y - self.window.height // 2
                else:
                    self.camera_sprites.stop_y = self.window.height // 2
                self.camera_sprites.y_set = True
            y = self.camera_sprites.stop_y
        else:
            if self.camera_sprites.y_set:
                self.camera_sprites.y_set = False
        self.camera_sprites.position = arcade.math.lerp_2d(self.camera_sprites.position, (x, y), 1)

    def update_winsize(self):
        if self.window.width // 2 - self.player.sprite.center_x > 0:
            self.moving_x = True
        elif self.window.width // 2 + self.player.sprite.center_x > self.area_x:
            self.moving_x = True
        else:
            if self.moving_x:
                self.moving_x = False

        if self.window.height - self.player.sprite.center_y > self.window.height // 2:
            self.moving_y = True
        elif self.window.height // 2 + self.player.sprite.center_y > self.area_y:
            self.moving_y = True
        else:
            if self.moving_y:
                self.moving_y = False

    def update_crosshair(self, x, y):
        self.pl_crsh.center_x = x
        self.pl_crsh.center_y = y

    def update_player_speed(self):
        self.player.sprite.change_x = 0
        self.player.sprite.change_y = 0
        self.pl_bul_hitbox.change_y = 0
        self.pl_bul_hitbox.change_x = 0
        moved = False
        reset_dash = False
        if self.dash_pressed and self.player.dash_recharged:
            dash_score = 0
            if self.up_pressed or self.down_pressed:
                dash_score += 1
            if self.left_pressed or self.right_pressed:
                dash_score += 1
            if dash_score == 0:
                self.player.dash_recharged = False
                reset_dash = True
            else:
                dash_dist = self.player.dash_dist // dash_score
                arcade.play_sound(self.pl_dash_audio, volume=self.sfx_volume)

        if self.up_pressed and not self.down_pressed:
            if self.dash_pressed and self.player.dash_recharged:
                flag = False
                for fin_dist in range(1, dash_dist + 1):
                    self.player.sprite.center_y += fin_dist
                    if not arcade.check_for_collision_with_list(self.player.sprite, self.wall_sprlist):
                        self.player.sprite.change_y = fin_dist
                        self.pl_bul_hitbox.change_y = self.player.sprite.change_y
                        moved = True
                    else: flag = True
                    self.player.sprite.center_y -= fin_dist
                    if flag: break
            else:
                self.player.sprite.center_y += self.player.move_speed
                if not arcade.check_for_collision_with_lists(self.player.sprite,
                                                             [self.wall_sprlist, self.banzai_list, self.stshoot_list]):
                    self.player.sprite.change_y = self.player.move_speed
                    self.pl_bul_hitbox.change_y = self.player.sprite.change_y
                    moved = True
                self.player.sprite.center_y -= self.player.move_speed

        elif self.down_pressed and not self.up_pressed:
            if self.dash_pressed and self.player.dash_recharged:
                flag = False
                for fin_dist in range(1, dash_dist + 1):
                    self.player.sprite.center_y -= fin_dist
                    if not arcade.check_for_collision_with_list(self.player.sprite, self.wall_sprlist):
                        self.player.sprite.change_y = -fin_dist
                        self.pl_bul_hitbox.change_y = self.player.sprite.change_y
                        moved = True
                    else: flag = True
                    self.player.sprite.center_y += fin_dist
                    if flag: break
            else:
                self.player.sprite.center_y -= self.player.move_speed
                if not arcade.check_for_collision_with_lists(self.player.sprite,
                                                             [self.wall_sprlist, self.banzai_list, self.stshoot_list]):
                    self.player.sprite.change_y = -self.player.move_speed
                    self.pl_bul_hitbox.change_y = self.player.sprite.change_y
                    moved = True
                self.player.sprite.center_y += self.player.move_speed

        if self.left_pressed and not self.right_pressed:
            if self.dash_pressed and self.player.dash_recharged:
                flag = False
                for fin_dist in range(1, dash_dist + 1):
                    self.player.sprite.center_x -= fin_dist
                    if not arcade.check_for_collision_with_list(self.player.sprite, self.wall_sprlist):
                        self.player.sprite.change_x = -fin_dist
                        self.pl_bul_hitbox.change_x = self.player.sprite.change_x
                        moved = True
                    else: flag = True
                    self.player.sprite.center_x += fin_dist
                    if flag: break
            else:
                self.player.sprite.center_x -= self.player.move_speed
                if not arcade.check_for_collision_with_lists(self.player.sprite,
                                                             [self.wall_sprlist, self.banzai_list, self.stshoot_list]):
                    self.player.sprite.change_x = -self.player.move_speed
                    self.pl_bul_hitbox.change_x = self.player.sprite.change_x
                    moved = True
                self.player.sprite.center_x += self.player.move_speed

        elif self.right_pressed and not self.left_pressed:
            if self.dash_pressed and self.player.dash_recharged:
                flag = False
                for fin_dist in range(1, dash_dist + 1):
                    self.player.sprite.center_x += fin_dist
                    if not arcade.check_for_collision_with_list(self.player.sprite, self.wall_sprlist):
                        self.player.sprite.change_x = fin_dist
                        self.pl_bul_hitbox.change_x = self.player.sprite.change_x
                        moved = True
                    else: flag = True
                    self.player.sprite.center_x -= fin_dist
                    if flag: break
            else:
                self.player.sprite.center_x += self.player.move_speed
                if not arcade.check_for_collision_with_lists(self.player.sprite,
                                                             [self.wall_sprlist, self.banzai_list, self.stshoot_list]):
                    self.player.sprite.change_x = self.player.move_speed
                    self.pl_bul_hitbox.change_x = self.player.sprite.change_x
                    moved = True
                self.player.sprite.center_x -= self.player.move_speed

        if moved:
            self.update_winsize()
            if self.player.dash_recharged and self.dash_pressed:
                change = (self.player.sprite.change_x, self.player.sprite.change_y)
                outline_distance = 15
                pos = self.player.sprite.position
                x_change, y_change = 0, 0
                if change[0] != 0 and change[1] != 0:
                    outline_distance /= 2
                    if change[0] < 0:
                        x_change = -outline_distance
                    else:
                        x_change = outline_distance
                    if change[1] < 0:
                        y_change = -outline_distance
                    else:
                        y_change = outline_distance
                    while abs(change[0]) >= outline_distance and abs(change[1]) >= outline_distance:
                        outline = arcade.Sprite(self.player.sprite.texture, self.player.sprite.scale, angle=self.player.sprite.angle)
                        pos = (pos[0]+x_change, pos[1]+y_change)
                        outline.position = pos
                        outline.rgb = (61, 122, 197)
                        outline.alpha = 127
                        change = (change[0] - x_change, change[1] - y_change)
                        self.dash_outlines_list.append(outline)
                else:
                    if change[0] != 0:
                        if change[0] < 0:
                            x_change = -outline_distance
                        else:
                            x_change = outline_distance
                    if change[1] != 0:
                        if change[1] < 0:
                            y_change = -outline_distance
                        else:
                            y_change = outline_distance
                    while abs(change[0]) >= outline_distance or abs(change[1]) >= outline_distance:
                        outline = arcade.Sprite(self.player.sprite.texture, self.player.sprite.scale, angle=self.player.sprite.angle)
                        pos = (pos[0]+x_change, pos[1]+y_change)
                        outline.position = pos
                        outline.rgb = (61, 122, 197)
                        outline.alpha = 127
                        change = (change[0] - x_change, change[1] - y_change)
                        self.dash_outlines_list.append(outline)
                self.player.dash_recharged = False
        if reset_dash: self.player.dash_recharged = True

    def update_parry(self):
        self.pl_parry_spark.position = self.player.sprite.position
        if self.parry_pressed and self.player.parry_recharged and not self.game_over:
            arcade.play_sound(self.pl_parry_audio, self.sfx_volume)
            self.pl_parry_spark.current_texture = 0
            self.gif_list.append(self.pl_parry_spark)
            self.player.parry_recharged = False
            circle = arcade.SpriteCircle(self.player.parry_radius, (0, 0, 0, 0))
            circle.position = self.player.sprite.position
            hit = arcade.check_for_collision_with_lists(circle, [self.banzai_list, self.enbullets_list])
            if hit:
                self.parry_success = True
                self.parry_sprites.append(self.player.sprite)
                self.parry_sprites.append(self.pl_parry_spark)
                for i in hit:
                    self.parry_sprites.append(i)
        # todo proper parry logic... good luck lol

    def update_player_angle(self, x, y):
        top = self.area_y - (self.window.height // 2) <= self.player.sprite.center_y
        bottom = self.player.sprite.center_y <= self.window.height // 2
        left = self.player.sprite.center_x <= self.window.width // 2
        right = self.area_x - (self.window.width // 2) <= self.player.sprite.center_x
        # this took me FAR too long than it should've, if only you'd know how many different equations i had tried lol
        if left:
            x_diff = 0
        elif right:
            x_diff = self.camera_sprites.position[0] - self.window.width // 2
        else:
            x_diff = self.player.sprite.center_x - self.window.width // 2
        if bottom:
            y_diff = 0
        elif top:
            y_diff = self.camera_sprites.position[1] - self.window.height // 2
        else:
            y_diff = self.player.sprite.center_y - self.window.height // 2
        x_angle = x + x_diff - self.player.sprite.center_x
        y_angle = y + y_diff - self.player.sprite.center_y
        angle = math.atan2(-y_angle, x_angle)
        prev_angle = self.player.sprite.angle
        self.player.sprite.angle = math.degrees(angle) + 90
        # print(angle)  # dont mind this, planning to finally do that rotation window resizing thingy and i know what's below is something real bad lol
        # if 0 <= angle < 45:
        #     print('1')
        # elif 45 <= angle < 90:
        #     print('2')
        # elif 90 <= angle < 135:
        #     print('3')
        # elif 135 <= angle < 180:
        #     print('4')
        # elif 180 <= angle < 225:
        #     print('5')
        # elif 225 <= angle < 270:
        #     print('6')
        # elif -90 <= angle < -45:
        #     print('7')
        # elif -45 <= angle < 0:
        #     print('8')

        rotate_around_point(self.pl_bul_hitbox, self.player.sprite.position, self.player.sprite.angle - prev_angle)

    def create_bullets(self):
        if not self.weapon_chosen:
            arcade.play_sound(self.player.bullet_audio, volume=self.sfx_volume)
            bullet = arcade.Sprite(self.player.bullet_sprite)
            bullet.damage = 1  # gonna have to do smth with this, since im planning to do different attacks...
            angle = math.radians(self.player.sprite.angle)
            bullet.angle = math.degrees(angle)
            bullet.change_y = self.pl_bullet_speed * math.cos(angle)
            bullet.change_x = self.pl_bullet_speed * math.sin(angle)
            bullet.position = self.pl_bul_hitbox.position
            bullet.type = 0
            self.plbullets_list.append(bullet)
        else:
            # play sound
            wave = gifSprite(texture_list=self.pl_wave1spr.textures, onetime=True, speed=self.pl_wave1spr.speed)
            angle = math.radians(self.player.sprite.angle)
            wave.damage = 3
            wave.angle = math.degrees(angle)
            #wave.player = play some audio (volume=self.sfx_volume)
            wave.change_y = self.player.wave_speed * math.cos(angle)
            wave.change_x = self.player.wave_speed * math.sin(angle)
            wave.position = self.pl_bul_hitbox.position
            wave.startpos = self.pl_bul_hitbox.position
            wave.type = 1
            wave.hit_enemies = []
            self.pl_wavesnd.play(self.sfx_volume)
            self.plbullets_list.append(wave)

    def create_enemy(self, enemy_type=0):
        if enemy_type == 0:  # banzai
            enemy = arcade.Sprite(self.banzai.sprite)
            enemy.scale = 1.5
            enemy.position = random_enemy_xy(enemy.size, self.area_x, self.area_y,
                                                             self.player.sprite.position, self.wall_sprite)
            enemy.index = len(self.banzai_list)
            self.banzai_list.append(enemy)
            thunder = gifSprite(texture_list=self.spawn_thunder.textures, onetime=True, speed=0.5)
            orb = gifSprite(texture_list=self.spawn_orb.textures, onetime=True, speed=0.5)
            orb.position = enemy.position
            thunder.center_x = enemy.center_x
            thunder.bottom = enemy.center_y
            self.gif_list.append(orb)
            self.gif_list.append(thunder)
            enemy.player = None
            enemy.enraged = False
            enemy.speed = self.banzai.speed
            enemy.health = self.banzai.health
        elif enemy_type == -1:
            boss = arcade.Sprite(self.boss.sprite)
            boss.position = (self.area_x//2, self.area_y*3//4)
            if self.intdifficulty != 3:
                boss.health = self.boss.health * (self.intdifficulty+1)
                boss.orig_health = self.boss.orig_health * (self.intdifficulty+1)
            else:
                boss.health = self.boss.health
                boss.orig_health = self.boss.orig_health
            self.boss_sprlist.append(boss)
            self.boss_att_hitbox.position = boss.position
            self.boss_att_hitbox.center_y += self.boss_att_hitbox_spacing
            thunder = gifSprite(texture_list=self.spawn_thunder.textures, onetime=True, speed=0.5)
            orb = gifSprite(texture_list=self.spawn_orb.textures, onetime=True, speed=0.5)
            orb.position = boss.position
            thunder.center_x = boss.center_x
            thunder.bottom = boss.center_y
            self.gif_list.append(orb)
            self.gif_list.append(thunder)
            self.boss_bg_player = self.boss_bg_sound.play(self.bg_volume)
        elif enemy_type == 1:  # static shooter
            enemy = arcade.Sprite(self.stshoot.sprite)
            enemy.position = random_enemy_xy(enemy.size, self.area_x, self.area_y, self.player.sprite.position, self.wall_sprite)
            self.stshoot_list.append(enemy)
            thunder = gifSprite(texture_list=self.spawn_thunder.textures, onetime=True, speed=0.5)
            orb = gifSprite(texture_list=self.spawn_orb.textures, onetime=True, speed=0.5)
            orb.position = enemy.position
            thunder.center_x = enemy.center_x
            thunder.bottom = enemy.center_y
            self.gif_list.append(orb)
            self.gif_list.append(thunder)
            enemy.timer = arcade.clock.Clock()
            enemy.health = self.stshoot.health
            enemy.player = None
            enemy.recharge = False
        elif enemy_type == 2:  # dynamic shooter
            pass

    def update_plbullets(self, delta_time):
        self.plbullets_list.update(delta_time)
        for entity in self.plbullets_list:
            if entity.type == 1:
                if entity.current_texture == len(entity.textures):
                    # sadly the only way working properly is removing one entity and replacing it with another :(
                    wave = gifSprite(texture_list=self.pl_wave2spr.textures, onetime=False, speed=self.pl_wave2spr.speed)
                    wave.type = 2
                    wave.damage = 3
                    wave.change_x = entity.change_x
                    wave.change_y = entity.change_y
                    wave.angle = entity.angle
                    wave.position = entity.position
                    wave.startpos = entity.startpos
                    wave.hit_enemies = entity.hit_enemies
                    self.plbullets_list.append(wave)
                    entity.remove_from_sprite_lists()
                elif arcade.math.get_distance(*entity.startpos, *entity.position) >= self.player.wave_distance:  # shouldn't happen, but whateever
                    entity.remove_from_sprite_lists()
            elif entity.type == 2:
                if arcade.math.get_distance(*entity.startpos, *entity.position) >= self.player.wave_distance:
                    entity.remove_from_sprite_lists()
            hit = arcade.check_for_collision_with_list(entity, self.wall_sprlist)
            if hit:
                hitmark = gifSprite(texture_list=self.hitmark.textures, onetime=self.hitmark.onetime,
                                    speed=self.hitmark.speed)
                hitmark.center_x, hitmark.center_y = entity.center_x, entity.center_y
                self.gif_list.append(hitmark)
                try:
                    entity.player.pause()
                except:
                    pass
                entity.remove_from_sprite_lists()

    def update_enemy(self, delta_time):
        for banz in self.banzai_list:
            angle = -math.atan2(self.player.sprite.center_y - banz.center_y,
                                self.player.sprite.center_x - banz.center_x) + 3.14 / 2
            banz.angle = math.degrees(angle)
            banz.center_x += banz.change_x
            banz.center_y += banz.change_y
            x_diff = self.player.sprite.center_x - banz.position[0]
            y_diff = self.player.sprite.center_y - banz.position[1]
            angle = math.atan2(y_diff, x_diff)
            if ((x_diff ** 2 + y_diff ** 2) <= self.banzai.rage_area ** 2) and not banz.enraged:
                banz.speed *= 2
                banz.enraged = True
                banz.timer = arcade.clock.Clock()
                if banz.player is None:
                    banz.player = arcade.play_sound(self.banzai.sound_charge, volume=self.sfx_volume)
            banz.change_x = math.cos(angle) * banz.speed
            banz.change_y = math.sin(angle) * banz.speed
            if banz.enraged:
                self.danger_zones[banz.index] = ['banz', banz.position]
                dist = arcade.math.get_distance(*self.player.sprite.position, *banz.position)
                volume = (self.banzai.rage_aud_area - dist) / self.banzai.rage_aud_area
                if volume < 0: volume = 0.0
                if volume > 1: volume = 1.0
                volume *= self.sfx_volume
                banz.player.volume = volume
                banz.timer.tick(delta_time)
                if self.flash_flag:
                    banz.texture = self.banzai.flash
                else:
                    banz.texture = self.banzai.sprite
                if banz.timer.ticks >= 180 or arcade.check_for_collision(banz, self.player.sprite):
                    arcade.play_sound(self.banzai.explosion_snd, volume=self.sfx_volume)
                    if (x_diff ** 2 + y_diff ** 2) <= self.banzai.explosion_radius ** 2 and not self.player.iframes:
                        self.player.lives -= 1
                        if self.player.lives > 0:
                            self.pl_hitplayer = self.pl_hit.play(self.sfx_volume)
                            self.player.iframes = True
                        else:
                            self.death_clocker.tick(0)
                            self.game_over = True
                    explosion = gifSprite(texture_list=self.banz_explspr.textures, onetime=self.banz_explspr.onetime,
                                          speed=self.banz_explspr.speed)  # messy, but works
                    explosion.center_x, explosion.center_y = banz.position
                    explosion.update(delta_time)
                    self.gif_list.append(explosion)
                    banz.player.pause()
                    banz.remove_from_sprite_lists()
                    self.danger_zones.pop(banz.index)
        for sts in self.stshoot_list:
            if not sts.recharge:
                sts.timer.tick(delta_time)
                if sts.timer.ticks % 240 == 0:
                    sts.recharge = True
            x_diff = self.player.sprite.center_x - sts.center_x
            y_diff = self.player.sprite.center_y - sts.center_y
            if sts.recharge and (x_diff ** 2 + y_diff ** 2 <= self.stshoot.shoot_area ** 2):
                angle = -math.atan2(y_diff, x_diff) + 3.14 / 2
                fire1 = gifSprite(texture_list=self.stshoot.fire1.textures, onetime=self.stshoot.fire1.onetime,
                                  speed=self.stshoot.fire1.speed)
                fire1.angle = math.degrees(angle)
                x_diff = self.player.sprite.center_x - sts.position[0]
                y_diff = self.player.sprite.center_y - sts.position[1]
                angle = math.atan2(y_diff, x_diff)
                fire1.player = self.stshoot.fire1snd.play(volume=self.sfx_volume)
                fire1.change_x = 4 * math.cos(angle)
                fire1.change_y = 4 * math.sin(angle)
                fire1.position = sts.position
                fire1.type = 'fire1'
                self.enbullets_list.append(fire1)
                sts.recharge = False
        for boss in self.boss_sprlist:
            angle = -math.atan2(self.player.sprite.center_y - boss.center_y,
                                self.player.sprite.center_x - boss.center_x) + 3.14 / 2
            prev_angle = boss.angle
            if self.boss.shielded:
                # todo play shielded sound
                if self.boss_shieldsspr not in self.gif_list:
                    self.gif_list.append(self.boss_shieldsspr)
                self.boss_shieldsspr.position = boss.position
            if self.boss.attack_recharged:
                self.boss.attacking = True
                self.boss.attack_recharged = False
            if self.boss.attacking:
                if not self.boss.tick_set:
                    self.boss.st_attack_tick = self.boss_attack_clocker.ticks
                    self.boss.tick_set = True
                if self.boss_laserchrg not in self.gif_list:
                    self.gif_list.append(self.boss_laserchrg)
                    self.boss_chargeaud.play(volume=self.sfx_volume)
                self.boss_laserchrg.position = self.boss_att_hitbox.position
                ticks_since = self.boss_attack_clocker.ticks_since(self.boss.st_attack_tick)
                if ticks_since < (self.boss.lsr_charge_time*3)//4:
                    boss.angle = math.degrees(angle)
                    rotate_around_point(self.boss_att_hitbox, boss.position, math.degrees(angle) - prev_angle)
                    if self.boss_locking not in self.boss_lock_sprlist:
                        self.boss_lock_sprlist.append(self.boss_locking)
                    self.boss_locking.position = self.player.sprite.position
                elif ticks_since % self.boss.lsr_charge_time == 0 and ticks_since != 0:
                    self.boss.lasering = True
                    self.boss.attacking = False
                    self.boss.tick_set = False
                    self.boss.st_attack_tick = self.boss_attack_clocker.ticks
                    self.boss_lock_sprlist.clear()
                    self.boss_lasersnd.play(self.sfx_volume)
                elif ticks_since >= (self.boss.lsr_charge_time*3)//4:
                    if self.boss_locking in self.boss_lock_sprlist:
                        self.boss_lockedon.position = self.boss_locking.position
                        self.boss_locking.remove_from_sprite_lists()
                        self.boss_lock_sprlist.append(self.boss_lockedon)
                        angle = -math.atan2(self.boss_lockedon.center_y - boss.center_y,
                                    self.boss_lockedon.center_x - boss.center_x) + 3.14 / 2
                        boss.angle = math.degrees(angle)
                        rotate_around_point(self.boss_att_hitbox, boss.position, math.degrees(angle) - prev_angle)
            elif self.boss.lasering:
                if not self.boss.tick_set:
                    self.boss.st_attack_tick = self.boss_attack_clocker.ticks
                    self.boss_laserchrg.remove_from_sprite_lists()
                    self.boss.tick_set = True
                ticks_since = self.boss_attack_clocker.ticks_since(self.boss.st_attack_tick)
                if ticks_since % self.boss.lsr_shoot_time == 0 and ticks_since != 0:
                    self.enbullets_list.clear()  # todo most likely move to specific list for boss bullets, since you're planning to also spawn enemies with the boss
                    self.boss.lasering = False
                    self.boss.tick_set = False
                    #todo play finish sound? like some charge down
                else:
                    if not self.enbullets_list: # sadly i couldnt finish the gradually appearing laser, had a lot of math problems
                        textures = self.boss_laserst.textures
                        speed = self.boss_laserst.speed
                        beam = gifSprite(texture_list=textures, speed=speed)
                        beam.bottom = boss.center_y+self.boss_att_hitbox_spacing
                        beam.center_x = boss.center_x
                        rotate_around_point(beam, boss.position, boss.angle)
                        beam.angle = boss.angle
                        beam.type = 'beam'
                        self.enbullets_list.append(beam)
            else:
                boss.angle = math.degrees(angle)
                rotate_around_point(self.boss_att_hitbox, boss.position, math.degrees(angle) - prev_angle)

    def update_enbullets(self, delta_time):
        self.enbullets_list.update(delta_time)
        for entity in self.enbullets_list:
            deleted = False
            hit = arcade.check_for_collision_with_list(entity, self.wall_sprlist)
            if hit:
                try:
                    entity.player.pause()
                except:
                    pass
                if entity.type == 'fire1' or entity.type == 'fire2':
                    entity.remove_from_sprite_lists()
                    deleted = True
            playerhits = arcade.check_for_collision_with_list(entity, self.sprite_list)
            if playerhits:
                try:
                    entity.player.pause()
                except:
                    pass
                if not self.player.iframes:
                    self.player.lives -= 1
                    if self.player.lives > 0:
                        self.pl_hitplayer = self.pl_hit.play(self.sfx_volume)
                        self.player.iframes = True
                    else:
                        self.death_clocker.tick(0)
                        self.game_over = True
                if entity.type == 'fire1' or entity.type == 'fire2':
                    entity.remove_from_sprite_lists()
                    deleted = True
            if entity.type == 'fire1' and not deleted:
                if entity.current_texture == len(entity.textures):
                    fire2 = gifSprite(texture_list=self.stshoot.fire2.textures, onetime=self.stshoot.fire2.onetime,
                                      speed=self.stshoot.fire2.speed)
                    fire2.change_x = entity.change_x
                    fire2.change_y = entity.change_y
                    fire2.angle = entity.angle
                    fire2.type = 'fire2'
                    fire2.position = entity.position
                    dist = arcade.math.get_distance(*self.player.sprite.position,*entity.position)
                    volume = self.stshoot.fire_sound_area / dist
                    if volume > 1:
                        volume = 1.0
                    volume *= self.sfx_volume
                    entity.player.volume = volume
                    if self.stshoot.fire1snd.is_playing(entity.player):
                        arcade.stop_sound(entity.player)
                        fire2.player = self.stshoot.fire2snd.play(volume=volume)
                    else:
                        fire2.player = self.stshoot.fire2snd.play(volume=volume)
                    self.enbullets_list.append(fire2)
                    entity.remove_from_sprite_lists()
            elif entity.type == 'fire2' and not deleted:
                entity.change_x *= 1.03
                entity.change_y *= 1.03
                dist = arcade.math.get_distance(*self.player.sprite.position, *entity.position)
                volume = (self.stshoot.fire_sound_area-dist)/self.stshoot.fire_sound_area
                if volume < 0: volume = 0.0
                if volume > 1: volume = 1.0
                volume *= self.sfx_volume
                entity.player.volume = volume
                if not self.stshoot.fire2snd.is_playing(entity.player):
                    entity.player = self.stshoot.fire2snd.play(volume=volume)

    def check_hit_enemy(self, delta_time):
        for pl_bullet in self.plbullets_list:
            banzai = arcade.check_for_collision_with_list(pl_bullet, self.banzai_list)
            for enemy in banzai:
                if pl_bullet.type == 1 or pl_bullet.type == 2:
                    if enemy not in pl_bullet.hit_enemies:
                        enemy.health -= pl_bullet.damage
                        hitmark = gifSprite(texture_list=self.hitmark.textures, onetime=self.hitmark.onetime,
                                            speed=self.hitmark.speed)
                        hitmark.center_x, hitmark.center_y = pl_bullet.center_x, pl_bullet.center_y
                        hitmark.update(delta_time)
                        self.gif_list.append(hitmark)
                        pl_bullet.hit_enemies.append(enemy)
                else:
                    enemy.health -= pl_bullet.damage
                    hitmark = gifSprite(texture_list=self.hitmark.textures, onetime=self.hitmark.onetime,
                                        speed=self.hitmark.speed)  # messy, but works
                    hitmark.center_x, hitmark.center_y = pl_bullet.center_x, pl_bullet.center_y
                    hitmark.update(delta_time)
                    self.gif_list.append(hitmark)
                    pl_bullet.remove_from_sprite_lists()
                if enemy.health <= 0:
                    death = gifSprite(texture_list=self.banz_deathspr.textures, onetime=self.banz_deathspr.onetime,
                                      speed=self.banz_deathspr.speed)
                    death.center_x, death.center_y = enemy.position
                    death.update(delta_time)
                    self.gif_list.append(death)
                    self.create_oneup(*enemy.position)
                    enemy.remove_from_sprite_lists()
                    self.score += 5
                    if not enemy.enraged:
                        arcade.play_sound(self.banzai.death_sound, self.sfx_volume)
                    else:
                        arcade.play_sound(self.banzai.explosion_snd, self.sfx_volume)
                        if (self.player.sprite.center_x ** 2 + self.player.sprite.center_y ** 2) <= self.banzai.explosion_radius ** 2 and not self.player.iframes:
                            self.player.lives -= 1
                            if self.player.lives > 0:
                                self.pl_hitplayer = self.pl_hit.play(self.sfx_volume)
                                self.player.iframes = True
                            else:
                                self.death_clocker.tick(0)
                                self.game_over = True
                        self.danger_zones.pop(enemy.index)
            sts = arcade.check_for_collision_with_list(pl_bullet, self.stshoot_list)
            for enemy in sts:
                if pl_bullet.type == 1 or pl_bullet.type == 2:
                    if enemy not in pl_bullet.hit_enemies:
                        enemy.health -= pl_bullet.damage
                        hitmark = gifSprite(texture_list=self.hitmark.textures, onetime=self.hitmark.onetime,
                                            speed=self.hitmark.speed)
                        hitmark.center_x, hitmark.center_y = pl_bullet.center_x, pl_bullet.center_y
                        hitmark.update(delta_time)
                        self.gif_list.append(hitmark)
                        pl_bullet.hit_enemies.append(enemy)
                else:
                    enemy.health -= pl_bullet.damage
                    hitmark = gifSprite(texture_list=self.hitmark.textures, onetime=self.hitmark.onetime,
                                        speed=self.hitmark.speed)  # messy, but works
                    hitmark.center_x, hitmark.center_y = pl_bullet.center_x, pl_bullet.center_y
                    hitmark.update(delta_time)
                    self.gif_list.append(hitmark)
                    pl_bullet.remove_from_sprite_lists()
                if enemy.health <= 0:
                    death = gifSprite(texture_list=self.stshoot.deathspr.textures,
                                      onetime=self.stshoot.deathspr.onetime,
                                      speed=self.stshoot.deathspr.speed)
                    death.center_x, death.center_y = enemy.position
                    death.update(delta_time)
                    self.gif_list.append(death)
                    self.create_oneup(*enemy.position)
                    enemy.remove_from_sprite_lists()
                    self.score += 20
                    arcade.play_sound(self.stshoot.death_sound, self.sfx_volume)
            boss = arcade.check_for_collision_with_list(pl_bullet, self.boss_sprlist)
            for enemy in boss:
                if pl_bullet.type == 1 or pl_bullet.type == 2:
                    if enemy not in pl_bullet.hit_enemies:
                        if not self.boss.shielded:
                            enemy.health -= pl_bullet.damage
                        hitmark = gifSprite(texture_list=self.hitmark.textures, onetime=self.hitmark.onetime,
                                            speed=self.hitmark.speed)
                        hitmark.center_x, hitmark.center_y = pl_bullet.center_x, pl_bullet.center_y
                        hitmark.update(delta_time)
                        self.gif_list.append(hitmark)
                        pl_bullet.hit_enemies.append(enemy)
                else:
                    if not self.boss.shielded:
                        enemy.health -= pl_bullet.damage
                    else:
                        self.boss_shield_hitaud.play(volume=self.sfx_volume)
                    hitmark = gifSprite(texture_list=self.hitmark.textures, onetime=self.hitmark.onetime,
                                        speed=self.hitmark.speed)  # messy, but works
                    hitmark.center_x, hitmark.center_y = pl_bullet.center_x, pl_bullet.center_y
                    hitmark.update(delta_time)
                    self.gif_list.append(hitmark)
                    pl_bullet.remove_from_sprite_lists()
                if enemy.health <= 0:
                    death = gifSprite(texture_list=self.boss_deathspr.textures,
                                      onetime=self.boss_deathspr.onetime,
                                      speed=self.boss_deathspr.speed)
                    death.center_x, death.center_y = enemy.position
                    death.update(delta_time)
                    self.gif_list.clear()
                    self.gif_list.append(death)
                    self.enbullets_list.clear()
                    self.boss_lock_sprlist.clear()
                    self.create_oneup(*enemy.position, True)
                    enemy.remove_from_sprite_lists()
                    if self.intdifficulty == 3: multiply = 1
                    else: multiply = self.intdifficulty
                    self.score += 200 * multiply
                    arcade.play_sound(self.boss_deathaud, volume=self.sfx_volume)

    def create_oneup(self, x, y, ignore_chance=False):
        if (np.random.randint(0, 10) == 1) or ignore_chance:
            oneup = gifSprite(texture_list=self.oneup.textures, speed=self.oneup.speed)
            oneup.movespeed = 4
            oneup.lifetime = 1500
            oneup.clock = arcade.clock.Clock()
            oneup.center_x = x
            oneup.center_y = y
            dx = np.random.randint(0, 2)
            dy = np.random.randint(0, 2)
            if dx:
                oneup.change_x = oneup.movespeed
            else:
                oneup.change_x = -oneup.movespeed
            if dy:
                oneup.change_y = oneup.movespeed
            else:
                oneup.change_y = -oneup.movespeed
            oneup.update()
            self.oneup_list.append(oneup)

    def move_oneup(self, delta_time):
        for oneup in self.oneup_list:
            oneup.clock.tick(delta_time)
            if oneup.clock.ticks_since(0) >= oneup.lifetime:
                self.oneup_list.remove(oneup)
            elif oneup.clock.ticks_since(0) >= (oneup.lifetime - 300):
                if oneup.clock.ticks_since(0) % 10 == 0:
                    if oneup.alpha == 255: oneup.alpha = 0
                    else: oneup.alpha = 255
            if arcade.check_for_collision_with_list(oneup, self.sprite_list):
                self.oneupsnd.play(volume=self.sfx_volume)
                if self.player.lives < 5:
                    self.player.lives += 1
                else:
                    self.score += 100
                self.oneup_list.remove(oneup)
            else:
                if oneup.center_x <= self.wall_sprite.width:
                    oneup.change_x = oneup.movespeed
                elif oneup.center_x >= self.area_x - self.wall_sprite.width:
                    oneup.change_x = -oneup.movespeed
                if oneup.center_y <= self.wall_sprite.height:
                    oneup.change_y = oneup.movespeed
                elif oneup.center_y >= self.area_y - self.wall_sprite.height:
                    oneup.change_y = -oneup.movespeed

    def spawn_enemies(self):
        if self.wave_count % 5 != 0:
            curr_enemies = read_and_return_enemies(self.difficulty)
            if curr_enemies.get(0) != 0:
                for _ in range(curr_enemies.get(0)):
                    self.create_enemy(0)
            if curr_enemies.get(1) != 0:
                for _ in range(curr_enemies.get(1)):
                    self.create_enemy(1)
            if curr_enemies.get(2) != 0:
                for _ in range(curr_enemies.get(2)):
                    self.create_enemy(2)
        else:
            self.create_enemy(-1)

    def overlay_text(self, text_type):
        if text_type == 'clear':
            if text_type in self.text_overlay_shown.keys():
                st_tick = self.text_overlay_shown.get(text_type)[2]
                if self.text_overlay_clocker.ticks_since(st_tick) % 120 == 0 and self.text_overlay_clocker.ticks_since(
                        st_tick) != 0:
                    self.text_overlay_shown.pop(text_type)
                    self.text_complete.append(text_type)
                else:
                    if self.boss_bg_player is not None:
                        if self.boss_bg_player.volume != 0.0:
                            self.boss_bg_player.volume -= self.bg_volume/60
                            if self.boss_bg_player.volume < 0.0:
                                self.boss_bg_player.volume = 0.0
                            if self.boss_bg_player.volume == 0.0:
                                self.boss_bg_player.pause()
                                self.boss_bg_player = None
                    text, box, _ = self.text_overlay_shown.get(text_type)
                    x = box.x
                    height = box.height
                    width = box.width
                    if box.x != self.window.center_x:
                        x -= 12
                        if box.x < self.window.center_x: x = self.window.center_x
                    if box.height != 50:
                        height += 2
                    if box.width != self.window.width:
                        width += 24
                    box = arcade.rect.XYWH(x, self.window.center_y + 100, width, height)
                    arcade.draw_rect_filled(box, arcade.color.BLACK)
                    if box.height >= 20 and text.x != self.window.center_x:
                        text.x -= 12
                        if text.x < self.window.center_x: text.x = self.window.center_x
                    text.draw()
                    self.text_overlay_shown[text_type] = [text, box, st_tick]
            else:
                text = arcade.Text('Wave clear!', self.window.width+200, self.window.center_y+100,
                                    font_size=20, anchor_x="center", anchor_y="center", font_name='Arcade Normal')
                box = arcade.rect.XYWH(self.window.width, self.window.center_y+100, 0, 0)
                st_tick = self.text_overlay_clocker.ticks
                self.text_overlay_shown[text_type] = [text, box, st_tick]

        elif text_type == 'warning':
            if text_type in self.text_overlay_shown.keys():
                st_tick = self.text_overlay_shown.get(text_type)[2]
                if self.text_overlay_clocker.ticks_since(st_tick) % 120 == 0 and self.text_overlay_clocker.ticks_since(
                        st_tick) != 0:
                    self.text_overlay_shown.pop(text_type)
                    self.text_complete.append(text_type)
                else:
                    if not self.warning_sound.is_playing(self.warning_player):
                        self.warning_player = self.warning_sound.play(self.sfx_volume)
                    if self.curr_audio.volume != 0.0:
                        self.curr_audio.volume -= self.bg_volume / 60
                        if self.curr_audio.volume < 0.0:
                            self.curr_audio.volume = 0.0
                        if self.curr_audio.volume == 0.0:
                            self.curr_audio.pause()
                    text1, text2 = self.text_overlay_shown.get(text_type)[0]
                    box1, box2 = self.text_overlay_shown.get(text_type)[1]
                    x1 = box1.x
                    height1 = box1.height
                    width1 = box1.width
                    x2 = box2.x
                    height2 = box2.height
                    width2 = box2.width
                    if box1.x != self.window.center_x:
                        x1 += 12
                        if box1.x > self.window.center_x: x1 = self.window.center_x
                    if box1.height != 50:
                        height1 += 2
                    if box1.width != self.window.width:
                        width1 += 24
                    if box2.x != self.window.center_x:
                        x2 -= 12
                        if box2.x < self.window.center_x: x2 = self.window.center_x
                    if box2.height != 50:
                        height2 += 2
                    if box2.width != self.window.width:
                        width2 += 24
                    box1 = arcade.rect.XYWH(x1, self.window.center_y + 100, width1, height1)
                    box2 = arcade.rect.XYWH(x2, self.window.center_y - 100, width2, height2)
                    arcade.draw_rect_filled(box1, arcade.color.BLACK)
                    arcade.draw_rect_filled(box2, arcade.color.BLACK)
                    if box1.height >= 20 and text1.x != self.window.center_x:
                        text1.x += 12
                        if text1.x > self.window.center_x: text1.x = self.window.center_x
                    if box2.height >= 20 and text2.x != self.window.center_x:
                        text2.x -= 12
                        if text2.x < self.window.center_x: text2.x = self.window.center_x
                    text1.draw()
                    text2.draw()
                    self.text_overlay_shown[text_type] = [[text1, text2], [box1, box2], st_tick]
            else:
                self.warning_player = self.warning_sound.play(self.sfx_volume)
                text1 = arcade.Text('Warning! Warning! Warning!', -300, self.window.center_y+100,
                                    font_size=20, anchor_x="center", anchor_y="center", font_name='Arcade Normal')
                text2 = arcade.Text('Warning! Warning! Warning!', self.window.width+300, self.window.center_y-100,
                                    font_size=20, anchor_x="center", anchor_y="center", font_name='Arcade Normal')
                box1 = arcade.rect.XYWH(0, self.window.center_y+100, 0, 0)
                box2 = arcade.rect.XYWH(self.window.width, self.window.center_y-100, 0, 0)
                st_tick = self.text_overlay_clocker.ticks
                self.text_overlay_shown[text_type] = [[text1, text2],[box1,box2], st_tick]
        elif text_type == 'wave count':
            if text_type in self.text_overlay_shown.keys():
                st_tick = self.text_overlay_shown.get(text_type)[2]
                if self.text_overlay_clocker.ticks_since(st_tick) % 120 == 0 and self.text_overlay_clocker.ticks_since(st_tick) != 0:
                    self.text_overlay_shown.pop(text_type)
                    self.text_complete.append(text_type)
                else:
                    self.curr_audio.play()
                    if self.curr_audio.volume != self.bg_volume:
                        self.curr_audio.volume += self.bg_volume / 60
                        if self.curr_audio.volume > self.bg_volume:
                            self.curr_audio.volume = self.bg_volume
                    text, box, _ = self.text_overlay_shown.get(text_type)
                    x = box.x
                    height = box.height
                    width = box.width
                    if box.x != self.window.center_x:
                        x += 12
                        if box.x > self.window.center_x: x = self.window.center_x
                    if box.height != 50:
                        height += 2
                    if box.width != self.window.width:
                        width += 24
                    box = arcade.rect.XYWH(x, self.window.center_y - 100, width, height)
                    arcade.draw_rect_filled(box, arcade.color.BLACK)
                    if box.height >= 20 and text.x != self.window.center_x:
                        text.x += 12
                        if text.x > self.window.center_x: text.x = self.window.center_x
                    text.draw()
                    self.text_overlay_shown[text_type] = [text, box, st_tick]
            else:
                text = arcade.Text(f"Incoming wave: {self.wave_count+1}", -200, self.window.center_y-100,
                                    font_size=20, anchor_x="center", anchor_y="center", font_name='Arcade Normal')
                box = arcade.rect.XYWH(0, self.window.center_y-100, 0, 0)
                st_tick = self.text_overlay_clocker.ticks
                self.text_overlay_shown[text_type] = [text, box, st_tick]

    def on_show_view(self):
        self.window.set_mouse_visible(False)
        if self.curr_audio is None:
            self.curr_audio = self.bg_music.play(volume=self.bg_volume, loop=True)

    def on_hide_view(self):
        self.window.set_mouse_visible(True)
        print('paused game')
        conf.logmn.log_info('paused game')

    def on_draw(self):
        self.clear()
        self.camera_sprites.use()
        if self.death_clocker.ticks_since(0) % 30 == 0 or not self.game_over:
            self.bg_list.draw()
            if self.danger_zones:
                for ind in self.danger_zones.keys():
                    i = self.danger_zones.get(ind)
                    if i[0] == 'banz':
                        if self.flash_flag:  # lame execution, but it'll be fine for now
                            arcade.draw_circle_filled(i[1][0], i[1][1], self.banzai.explosion_radius, (255, 0, 0, 64))
                            arcade.draw_circle_outline(i[1][0], i[1][1], self.banzai.explosion_radius, (255, 0, 0, 192))
            if self.player.iframes:
                if self.player.iframes_draw:
                    self.sprite_list.draw()
            else:
                self.sprite_list.draw()
            # maybe for later debug hitbox show???
            # arcade.draw_circle_outline(self.player.sprite.center_x, self.player.sprite.center_y, self.banzai.rage_area, arcade.color.BLUE)
            if self.player.parry_recharged and not self.game_over:
                arcade.draw_circle_outline(*self.player.sprite.position, self.player.parry_radius, (228, 125, 0, 127))
            self.banzai_list.draw()
            self.stshoot_list.draw()
            self.boss_sprlist.draw()
            self.plbullets_list.draw()
            self.enbullets_list.draw()
            self.dash_outlines_list.draw()
            self.oneup_list.draw()
            self.gif_list.draw()
            self.boss_lock_sprlist.draw()
            self.wall_sprlist.draw()
            if self.parry_success:
                arcade.draw_rect_filled(arcade.rect.XYWH(*self.camera_sprites.position, *self.window.size), (255, 255, 255, 127))
                self.parry_sprites.draw()

            self.camera_gui.use()  # for later gui use
            self.crosshair.draw()

            arcade.draw_rect_filled(
                arcade.rect.XYWH(self.window.width // 2, self.window.height - 25, self.window.width, 50),
                (0, 0, 0, 128))
            arcade.draw_rect_outline(
                arcade.rect.XYWH(self.window.width // 2, self.window.height - 25, self.window.width + 2, 50),
                arcade.color.GOLDEN_BROWN, 2)
            if self.player.lives != 0:
                for i in range(self.player.lives + 1):
                    live = arcade.Sprite(self.pl_lives)  # when adding lives do a max of 5 lives!
                    if i + 1 == 1:
                        live.left = 16
                        live.center_y = self.window.height - 25
                    else:
                        live.left = (i + 1) * 16 - (i + 1) * 8
                        live.center_y = self.window.height - 25
                    arcade.draw_sprite(live)

            arcade.draw_rect_filled(arcade.rect.XYWH(180, self.window.height - 25, self.dash_width, 40), (61, 122, 197))
            arcade.draw_rect_outline(arcade.rect.XYWH(180, self.window.height - 25, 100, 40), arcade.color.WHITE, 2)
            arcade.draw_rect_filled(arcade.rect.XYWH(300, self.window.height-25, self.parry_width, 40), (228, 125, 0))
            arcade.draw_rect_outline(arcade.rect.XYWH(300, self.window.height - 25, 100, 40), arcade.color.WHITE, 2)
            self.dash_text.draw()
            self.parry_text.draw()
            arcade.draw_rect_filled(arcade.rect.XYWH(370, self.window.height - 45, 20, self.pl_bul_rchg_height, arcade.types.vector_like.AnchorPoint.BOTTOM_CENTER), (255, 156, 0))
            arcade.draw_rect_outline(arcade.rect.XYWH(370, self.window.height-25, 20, 40), arcade.color.WHITE, 2)
            arcade.draw_rect_filled(arcade.rect.XYWH(400, self.window.height - 45, 20, self.pl_wave_rchg_height, arcade.types.vector_like.AnchorPoint.BOTTOM_CENTER),
                                    (255, 156, 0))
            arcade.draw_rect_outline(arcade.rect.XYWH(400, self.window.height - 25, 20, 40), arcade.color.WHITE, 2)
            self.pl_wave_text.draw()
            self.pl_bul_text.draw()
            self.wave_text.draw()
            self.score_text.draw()

            if self.text_to_show:
                for text in self.text_to_show:
                    if text not in self.text_complete:
                        self.overlay_text(text)

            if self.boss_sprlist:
                for boss in self.boss_sprlist:
                    arcade.draw_rect_filled(arcade.rect.XYWH(self.window.center_x, self.window.height - 85, (self.window.width*3//4)*(boss.health/boss.orig_health), 50), (255, 0, 0, 127))
                    arcade.draw_rect_outline(arcade.rect.XYWH(self.window.center_x, self.window.height - 85, self.window.width*3//4, 50), arcade.color.WHITE)

            if self.game_over:
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(self.window.center_x, self.window.center_y, self.window.width, self.window.height),
                    (0, 0, 0, self.blackout_delta))
        else:
            self.sprite_list.draw()

    def on_update(self, delta_time):
        if self.death_clocker.ticks_since(0) >= 30 or (not self.game_over and not self.parry_success):
            if not self.enemies_spawned:
                if self.wave_count != 0 and 'clear' not in self.text_to_show:
                    self.text_to_show.append('clear')
                if 'clear' in self.text_complete or (self.wave_count == 0 and ('wave count' not in self.text_to_show or 'wave count' in self.text_complete)):
                    if (self.wave_count+1) % 5 == 0 and 'warning' not in self.text_to_show:
                        self.text_to_show.append('warning')
                    elif 'wave count' not in self.text_to_show and (self.wave_count+1) % 5 != 0:
                        self.text_to_show.append('wave count')
                    if self.text_to_show == self.text_complete:
                        self.wave_count += 1
                        self.spawn_enemies()
                        self.enemies_spawned = True
                        self.wave_text.text = f"Wave: {self.wave_count}"
                        self.text_to_show.clear()
                        self.text_complete.clear()
            if not self.banzai_list and not self.stshoot_list and not self.boss_sprlist and 'clear' not in self.text_to_show and self.wave_count != 0:
                arcade.play_sound(self.wave_clear_audio, self.sfx_volume)
                self.score += 100
                self.enemies_spawned = False
            if self.danger_zones:
                self.danger_clocker.tick(delta_time)
                if self.danger_clocker.ticks_since(0) % 6 == 0:
                    self.flash_flag = not self.flash_flag

            if not self.recharge_flag:
                self.clocker.tick(delta_time)
                self.pl_bul_rchg_height = 40 * ((self.clocker.ticks_since(0) - (self.pl_bullet_recharge * (
                        self.clocker.ticks_since(0) // self.pl_bullet_recharge))) / self.pl_bullet_recharge)
                if self.clocker.ticks_since(0) % self.pl_bullet_recharge == 0:
                    self.recharge_flag = True
                    self.pl_bul_rchg_height = 40

            if not self.player.wave_recharged:
                self.wave_rchg_clocker.tick(delta_time)
                self.pl_wave_rchg_height = 40 * ((self.wave_rchg_clocker.ticks_since(0) - (self.player.wave_recharge * (
                        self.wave_rchg_clocker.ticks_since(0) // self.player.wave_recharge))) / self.player.wave_recharge)
                if self.wave_rchg_clocker.ticks_since(0) % self.player.wave_recharge == 0:
                    self.player.wave_recharged = True
                    self.pl_wave_rchg_height = 40

            if self.text_to_show:
                self.text_overlay_clocker.tick(delta_time)

            if self.dash_outlines_list:
                self.dash_outlines_clocker.tick(delta_time)
                if self.dash_outlines_clocker.ticks_since(0) % 2 == 0:
                    self.dash_outlines_list.pop(0)

            if not self.boss.attack_recharged and not self.boss.attacking and not self.boss.lasering:
                self.boss_recharge_clocker.tick(delta_time)
                if self.boss_recharge_clocker.ticks_since(0) % self.boss.recharge_time == 0:
                    self.boss.attack_recharged = True

            if not self.boss.shielded and self.wave_count != 0 and self.wave_count % 5 == 0:
                self.boss_shield_clocker.tick(delta_time)
                if self.boss_shield_clocker.ticks_since(0) % self.boss.shield_rchg == 0:
                    self.boss.shielded = True
            elif self.boss.shielded and self.wave_count != 0 and self.wave_count % 5 == 0:
                self.boss_shielded_clocker.tick(delta_time)
                if self.boss_shielded_clocker.ticks_since(0) % self.boss.shield_time == 0:
                    self.boss.shielded = False
                    self.gif_list.remove(self.boss_shieldsspr)

            if self.boss.attacking or self.boss.lasering:
                self.boss_attack_clocker.tick(delta_time)

            if not self.player.dash_recharged:
                self.pl_dash_clocker.tick(delta_time)
                self.dash_width = 100 * ((self.pl_dash_clocker.ticks_since(0) - (self.player.dash_rechtime * (
                            self.pl_dash_clocker.ticks_since(
                                0) // self.player.dash_rechtime))) / self.player.dash_rechtime)
                if self.pl_dash_clocker.ticks_since(0) % self.player.dash_rechtime == 0:
                    self.player.dash_recharged = True
                    self.dash_width = 100
                    arcade.play_sound(self.pl_dash_chrg_audio, self.sfx_volume)

            if not self.player.parry_recharged:
                self.pl_parry_clocker.tick(delta_time)
                self.parry_width = 100 * ((self.pl_parry_clocker.ticks_since(0) - (self.player.parry_rechtime * (
                            self.pl_parry_clocker.ticks_since(
                                0) // self.player.parry_rechtime))) / self.player.parry_rechtime)
                if self.pl_parry_clocker.ticks_since(0) % self.player.parry_rechtime == 0:
                    self.player.parry_recharged = True
                    self.parry_width = 100
                    arcade.play_sound(self.pl_parry_chrg_audio, self.sfx_volume)

            if not self.game_over:
                if self.shoot_flag:
                    if not self.weapon_chosen and self.recharge_flag:
                        self.create_bullets()
                        self.recharge_flag = False
                    elif self.weapon_chosen and self.player.wave_recharged:
                        self.create_bullets()
                        self.player.wave_recharged = False
                self.update_player_angle(self.pl_crsh.center_x, self.pl_crsh.center_y)
                self.update_player_speed()
                self.update_enemy(delta_time)
                self.score_text.text = f"Score: {self.score}"

            self.sprite_list.update(delta_time)
            self.move_oneup(delta_time)
            if self.player.iframes:
                self.iframes_clocker.tick(delta_time)
                if self.iframes_clocker.ticks % self.player.iframes_len == 0:
                    self.player.iframes = False
                    self.player.iframes_draw = True
                if self.iframes_clocker.ticks % 6 == 0:
                    self.player.iframes_draw = not self.player.iframes_draw

            self.update_plbullets(delta_time)
            self.check_hit_enemy(delta_time)
            self.oneup_list.update(delta_time)
            self.boss_lock_sprlist.update(delta_time)
            self.gif_list.update(delta_time)
            self.update_parry()
            self.update_enbullets(delta_time)
            self.update_crosshair(self.mouse_x, self.mouse_y)
            self.wave_text.x = self.window.width - 50 - self.score_text.content_width
            self.scroll_to_player()

            if self.game_over:
                if self.blackout_delta != 255:
                    if self.blackout_delta < 30:
                        self.blackout_delta += 0.5
                    else:
                        self.blackout_delta += 1
                else:
                    print("we're done, go to results (do a results view screen instead of main menu)")  # todo just read it man
                    self.window.show_view(self.main_menu)
        elif self.parry_success:
            self.parry_draw_clocker.tick(delta_time)
            if self.parry_draw_clocker.ticks_since(0) % 30 == 0:
                self.parry_success = False
                self.parry_sprites.clear()
        elif self.game_over:
            if self.pl_predeathplayer is None:
                self.pl_predeathplayer = self.pl_predeathsnd.play(volume=self.sfx_volume)
            if self.bg_music.is_playing(self.curr_audio):
                self.bg_music.stop(self.curr_audio)
            self.death_clocker.tick(delta_time)
            if self.death_clocker.ticks_since(0) % 30 == 0:
                self.sprite_list.clear()
                self.pl_death.center_x = self.player.sprite.center_x
                self.pl_death.center_y = self.player.sprite.center_y
                self.gif_list.append(self.pl_death)
                self.pl_deathsnd.play(volume=self.sfx_volume)

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.ESCAPE and not self.game_over:
            pause = PauseView(self)
            self.window.show_view(pause)
        if key == arcade.key.A:
            self.left_pressed = True
        if key == arcade.key.D:
            self.right_pressed = True
        if key == arcade.key.W:
            self.up_pressed = True
        if key == arcade.key.S:
            self.down_pressed = True
        if key == arcade.key.LSHIFT:
            self.dash_pressed = True
        if key == arcade.key.F:
            self.parry_pressed = True
        if key == arcade.key.TAB:
            self.weapon_chosen = not self.weapon_chosen
        if key == arcade.key.KEY_1:
            self.weapon_chosen = False
        if key == arcade.key.KEY_2:
            self.weapon_chosen = True
        if key == arcade.key.P:
            self.banzai_list.clear()
            self.stshoot_list.clear()
            self.boss_sprlist.clear()
            self.danger_zones.clear()
            self.enbullets_list.clear()
        if key == arcade.key.O:
            self.banzai_list.clear()
            self.stshoot_list.clear()
            self.boss_sprlist.clear()
            self.danger_zones.clear()
            self.enbullets_list.clear()
            self.wave_count += 3
        # if key == arcade.key.U:
        #     self.create_enemy(1)
        # if key == arcade.key.I:
        #     self.create_enemy(2)
        if key == arcade.key.SPACE:
            self.shoot_flag = True

    def on_key_release(self, key, key_modifiers):
        if key == arcade.key.A:
            self.left_pressed = False
        if key == arcade.key.D:
            self.right_pressed = False
        if key == arcade.key.W:
            self.up_pressed = False
        if key == arcade.key.S:
            self.down_pressed = False
        if key == arcade.key.LSHIFT:
            self.dash_pressed = False
        if key == arcade.key.F:
            self.parry_pressed = False
        if key == arcade.key.SPACE:
            self.shoot_flag = False

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button, key_modifiers):
        self.shoot_flag = True

    def on_mouse_release(self, x, y, button, key_modifiers):
        self.shoot_flag = False


class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game = game_view

    def on_draw(self):
        self.clear()

        self.game.camera_sprites.use()
        self.game.bg_list.draw()
        self.game.sprite_list.draw()
        self.game.banzai_list.draw()
        self.game.boss_sprlist.draw()
        self.game.stshoot_list.draw()
        self.game.wall_sprlist.draw()
        self.game.plbullets_list.draw()
        self.game.enbullets_list.draw()
        self.game.gif_list.draw()

        self.game.camera_gui.use()
        arcade.draw_rect_filled(
            arcade.rect.XYWH(self.window.width // 2, self.window.height - 25, self.window.width, 50),
            (0, 0, 0, 128))
        arcade.draw_rect_outline(
            arcade.rect.XYWH(self.window.width // 2, self.window.height - 25, self.window.width + 2, 50),
            arcade.color.GOLDEN_BROWN, 2)
        for i in range(self.game.player.lives + 1):
            live = arcade.Sprite(self.game.pl_lives)  # when adding lives do a max of 5 lives!
            if i + 1 == 1:
                live.left = (i + 1) * 16
                live.center_y = self.window.height - 25
            else:
                live.left = (i + 1) * 16 - (i + 1) * 8
                live.center_y = self.window.height - 25
            arcade.draw_sprite(live)
        arcade.draw_rect_filled(arcade.rect.XYWH(180, self.window.height - 25, self.game.dash_width, 40), (61, 122, 197))
        arcade.draw_rect_outline(arcade.rect.XYWH(180, self.window.height - 25, 100, 40), arcade.color.WHITE, 2)
        arcade.draw_rect_filled(arcade.rect.XYWH(300, self.window.height-25, self.game.parry_width, 40), (228, 125, 0))
        arcade.draw_rect_outline(arcade.rect.XYWH(300, self.window.height - 25, 100, 40), arcade.color.WHITE, 2)
        self.game.dash_text.draw()
        self.game.parry_text.draw()
        arcade.draw_rect_filled(arcade.rect.XYWH(370, self.window.height - 45, 20, self.game.pl_bul_rchg_height, arcade.types.vector_like.AnchorPoint.BOTTOM_CENTER), (255, 156, 0))
        arcade.draw_rect_outline(arcade.rect.XYWH(370, self.window.height-25, 20, 40), arcade.color.WHITE, 2)
        arcade.draw_rect_filled(arcade.rect.XYWH(400, self.window.height - 45, 20, self.game.pl_wave_rchg_height, arcade.types.vector_like.AnchorPoint.BOTTOM_CENTER),
                                (255, 156, 0))
        arcade.draw_rect_outline(arcade.rect.XYWH(400, self.window.height - 25, 20, 40), arcade.color.WHITE, 2)
        self.game.pl_wave_text.draw()
        self.game.pl_bul_text.draw()
        self.game.wave_text.draw()
        self.game.score_text.draw()

        # no in-game elements past this point
        arcade.draw_rect_filled(
            arcade.rect.XYWH(self.window.width // 2, self.window.height // 2, self.window.width, self.window.height),
            [0, 0, 0, 128])
        arcade.Text("PAUSED", self.window.center_x, self.window.center_y + 50,
                    arcade.color.WHITE, font_size=50, anchor_x="center", font_name='Arcade Normal').draw()
        arcade.Text("Esc - Return to game",
                    self.window.center_x,
                    self.window.center_y,
                    arcade.color.WHITE,
                    font_size=20,
                    anchor_x="center", font_name='Arcade Normal').draw()
        arcade.Text("Enter - Main menu",
                    self.window.center_x,
                    self.window.center_y - 30,
                    arcade.color.WHITE,
                    font_size=20,
                    anchor_x="center", font_name='Arcade Normal').draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            print('unpaused game')
            conf.logmn.log_info('unpaused game')
            self.window.show_view(self.game)
        elif key == arcade.key.ENTER:
            print('closing game')
            conf.logmn.log_info('closing game')
            arcade.stop_sound(self.game.curr_audio)
            try:
                arcade.stop_sound(self.game.boss_bg_player)
            except:
                pass
            self.window.show_view(self.game.main_menu)

    def on_key_release(self, key, modifiers):
        self.game.on_key_release(key, modifiers)
