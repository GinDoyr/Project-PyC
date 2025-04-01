import arcade
import arcade.clock
from arcade.math import rotate_point
from arcade.gui import (
    UIManager,
    UIBoxLayout,
    UILabel)
import file_mngr.conf_mngr as conf
import file_mngr.zip_mngr as zipmn
import player
import enemies
import math
import numpy as np


# look into this on how to do animations
# Load animation for the sprite widget
# frame_textures = []
# for i in range(8):
#     tex = arcade.load_texture(f":resources:images/animated_characters/female_adventurer/femaleAdventurer_walk{i}.png")
#     frame_textures.append(tex)
# TEX_ANIMATED_CHARACTER = arcade.TextureAnimation([arcade.TextureKeyframe(frame) for frame in frame_textures])
# sprite = arcade.TextureAnimationSprite(animation=TEX_ANIMATED_CHARACTER)
# sprite.scale = 0.5
# sprite_row = box.add(UIBoxLayout(vertical=False, size_hint=(1, 0.1)))
# sprite_row.add(
#     UILabel("UISpriteWidget", font_name=DETAILS_FONT, font_size=16, size_hint=(0.3, 0))
# )
# sprite_row.add(UISpriteWidget(sprite=sprite, width=sprite.width, height=sprite.height))

def rotate_around_point(sprite, point, degrees):
    sprite.position = rotate_point(
        sprite.center_x, sprite.center_y,
        point[0], point[1], degrees)


def random_enemy_xy(width, height, pl_pos, wall):
    '''
    :param width: area width
    :param height: area height
    :param pl_pos: player position (x, y)
    :param wall: wall from gameview
    :return: random x and y
    '''
    one = np.random.randint(0, 2)
    two = np.random.randint(0, 2)
    if (one or not (not one and pl_pos[0]-300 > wall.width)) and pl_pos[0]+300 < width - wall.width:
        x = np.random.randint(pl_pos[0]+300, width - wall.width)
    else:
        x = np.random.randint(wall.width, pl_pos[0]-300)
    if (two or not (not two and pl_pos[1]-300 > wall.height)) and pl_pos[1]+300 < height - wall.height:
        y = np.random.randint(pl_pos[1]+300, height - wall.height)
    else:
        y = np.random.randint(wall.height, pl_pos[1]-300)
    try:
        return x, y
    except Exception as e:
        conf.logmn.log_warning(f'failed to create random x, y for enemy! {e}')


def point_enemy_to_player(pl_x, pl_y, en_x, en_y):
    return -math.atan2(pl_y - en_y, pl_x - en_x) + 3.14 / 2


class GameLoop(arcade.View):
    def __init__(self, main_menu):
        super().__init__()
        # commented for now, resolve later
        # self.window.width, self.window.height = self.window.width//4, 7*self.window.height//8
        # self.window.center_window()

        conf.logmn.log_info('launching game loop')

        # misc
        self.clocker = arcade.clock.Clock()
        self.main_menu = main_menu
        self.area_x, self.area_y = 2000, 2000
        self.mouse_x, self.mouse_y = self.window.center

        # sound
        self.curr_audio = None
        if conf.set_settings('Settings', 'resourcepack') != 'None':
            zipmn.load_resourcepack(conf.set_settings('Settings', 'resourcepack'))
            self.bg_music = zipmn.try_loading_from_resourcepack('Audio', 'music_game', streaming=True)
        else:
            self.bg_music = arcade.load_sound(conf.set_settings('Audio', 'music_game'), streaming=True)

        # flags
        self.bg_flag = False
        self.resize_flag = False
        self.shoot_flag = False
        self.recharge_flag = False
        self.mouse_flag = True
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # player stuff
        # PLEASE MAKE SURE SPRITE LOOKS UP! mb make a confirm window to adjust the import sprite angle?
        if conf.set_settings('Settings',
                             'resourcepack') != 'None':  # ok so i've made some function but still looks like a mess. or not. idk, but it works :D
            player_sprite = zipmn.try_loading_from_resourcepack('Sprites', 'player_sprite')
            pl_bullet_sprite = zipmn.try_loading_from_resourcepack('Sprites', 'player_bullet').texture
            self.pl_crsh = zipmn.try_loading_from_resourcepack('Sprites', 'player_crosshair')
            self.pl_lives = zipmn.try_loading_from_resourcepack('Sprites', 'other_lives').texture
            pl_bullet_audio = zipmn.try_loading_from_resourcepack('Audio', 'player_bullet')
            banz_sprite = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_enemy1').texture
            banz_death = zipmn.try_loading_from_resourcepack('Audio', "enemies_enemy1 death")
            banz_rush = zipmn.try_loading_from_resourcepack('Audio', 'enemies_enemy1 rush')
            banz_expl = zipmn.try_loading_from_resourcepack('Audio', 'enemies_enemy1 explosion')
            #banz_explspr = zipmn.try_loading_from_resourcepack('Sprites', 'enemies_enemy1 explosion')
        else:
            player_sprite = arcade.Sprite(conf.set_settings('Sprites', 'player_sprite'))
            pl_bullet_sprite = arcade.Sprite(conf.set_settings('Sprites',
                                                               'player_bullet')).texture  # do this just as a texture since you are using only the texture when creating bullets!!! please!!1 ;(
            self.pl_crsh = arcade.Sprite(conf.set_settings("Sprites", "player_crosshair"))
            self.pl_lives = arcade.Sprite(conf.set_settings('Sprites', 'other_lives')).texture
            pl_bullet_audio = arcade.load_sound(conf.set_settings("Audio", "player_bullet"))
            banz_sprite = arcade.Sprite(conf.set_settings('Sprites', 'enemies_enemy1')).texture
            banz_death = arcade.load_sound(conf.set_settings('Audio', "enemies_enemy1 death"))
            banz_rush = arcade.load_sound(conf.set_settings('Audio', 'enemies_enemy1 rush'))
            banz_expl = arcade.load_sound(conf.set_settings('Audio', 'enemies_enemy1 explosion'))

        # player
        pl_bullet_sprite.width, pl_bullet_sprite.height = 10, 28
        player_sprite.width, player_sprite.height = 64, 64
        self.pl_bullet_speed = 10
        self.pl_bullet_recharge = 6  # higher - faster
        self.player = player.Player(player_sprite, pl_bullet_sprite, pl_bullet_audio)
        self.pl_speed = 10
        self.player.sprite.center_x = self.area_x // 2
        self.player.sprite.center_y = self.area_y // 2
        self.pl_bul_hitbox = arcade.Sprite(
            "assets/sprites/misc/very_important_1x1.png")  # this is the only thing i've come up for the bullet start point. hoping to smh change it later
        self.pl_bul_hitbox.bottom = self.player.sprite.top
        self.pl_bul_hitbox.center_x = self.player.sprite.center_x

        # banzai
        self.banzai = enemies.Banzai(banz_sprite, banz_rush, banz_expl, banz_death)

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
                x = self.area_x - self.wall_sprite.width
            for y in range(0, self.area_y + int(self.wall_sprite.height), int(self.wall_sprite.height)):
                if y >= self.area_y:
                    y = self.area_y - self.wall_sprite.height
                if y == 0 or y == self.area_y - self.wall_sprite.height:
                    wall = arcade.Sprite(self.wall_sprite)
                    wall.left, wall.bottom = x, y
                    self.wall_sprlist.append(wall)
                elif x == 0 or x == self.area_x - self.wall_sprite.width:
                    wall = arcade.Sprite(self.wall_sprite)
                    wall.left, wall.bottom = x, y
                    self.wall_sprlist.append(wall)

        # sprite lists
        self.sprite_list = arcade.SpriteList()
        self.banzai_list = arcade.SpriteList()  # i really didnt want to go this way but whatever, for now
        self.entities_list = arcade.SpriteList()
        self.crosshair = arcade.SpriteList()
        self.crosshair.append(self.pl_crsh)
        self.sprite_list.append(self.player.sprite)
        self.sprite_list.append(self.pl_bul_hitbox)
        self.pl_bul_hitbox.visible = False

        # there's the camera
        self.camera_sprites = arcade.Camera2D()
        self.camera_gui = arcade.Camera2D()

        # score something something! :D
        self.score = 0

    def scroll_to_player(self):
        position = (self.player.sprite.center_x, self.player.sprite.center_y)
        self.camera_sprites.position = arcade.math.lerp_2d(self.camera_sprites.position, position, 1)

    def update_crosshair(self, x, y):
        self.pl_crsh.center_x = x
        self.pl_crsh.center_y = y

    def update_player_speed(self):

        self.player.sprite.change_x = 0
        self.player.sprite.change_y = 0
        self.pl_bul_hitbox.change_y = 0
        self.pl_bul_hitbox.change_x = 0

        if self.up_pressed and not self.down_pressed:
            if self.player.sprite.top + self.pl_speed <= self.area_y - self.wall_sprite.height:  # to do: normal collision with wall sprite list instead of this bruteforce lol. although it works... idk
                self.player.sprite.change_y = self.pl_speed
                self.pl_bul_hitbox.change_y = self.player.sprite.change_y
        elif self.down_pressed and not self.up_pressed:
            if self.player.sprite.bottom - self.pl_speed >= self.wall_sprite.height:
                self.player.sprite.change_y = -self.pl_speed
                self.pl_bul_hitbox.change_y = self.player.sprite.change_y
        if self.left_pressed and not self.right_pressed:
            if self.player.sprite.left - self.pl_speed >= self.wall_sprite.width:
                self.player.sprite.change_x = -self.pl_speed
                self.pl_bul_hitbox.change_x = self.player.sprite.change_x
        elif self.right_pressed and not self.left_pressed:
            if self.player.sprite.right + self.pl_speed <= self.area_x - self.wall_sprite.width:
                self.player.sprite.change_x = self.pl_speed
                self.pl_bul_hitbox.change_x = self.player.sprite.change_x

    def update_player_angle(self, x, y):
        x_angle = x - self.window.center_x
        y_angle = y - self.window.center_y
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
        arcade.play_sound(self.player.bullet_audio, volume=float(conf.set_settings('Settings', 'sfx_volume')))
        bullet = arcade.Sprite(self.player.bullet_sprite)
        angle = math.radians(self.player.sprite.angle)
        bullet.angle = math.degrees(angle)
        bullet.change_y = self.pl_bullet_speed * math.cos(angle)
        bullet.change_x = self.pl_bullet_speed * math.sin(angle)
        bullet.position = self.pl_bul_hitbox.position
        self.entities_list.append(bullet)

    def create_enemy(self, enemy_type=1):
        if enemy_type == 1:
            enemy = arcade.Sprite(self.banzai.sprite)
            enemy
            enemy.scale = 1.5
            enemy.center_x, enemy.center_y = random_enemy_xy(self.area_x, self.area_y, self.player.sprite.position, self.wall_sprite)
            self.banzai_list.append(enemy)
        elif enemy_type == 2:
            pass
        elif enemy_type == 3:
            pass

    def update_bullets(self):
        self.entities_list.update()
        for entity in self.entities_list:
            if entity.top > self.area_y - self.wall_sprite.height or entity.bottom < self.wall_sprite.height or entity.left < self.wall_sprite.width or entity.right > self.area_x - self.wall_sprite.width:
                # ... this is just awful. i really, REALLY need to make this better somehow. later, as is everything :P
                entity.remove_from_sprite_lists()

    def update_enemy_angle(self):
        for banz in self.banzai_list:  # made for right facing banzais, just del the -90
            angle = -math.atan2(self.player.sprite.center_y - banz.center_y, self.player.sprite.center_x - banz.center_x) + 3.14 / 2
            banz.angle = math.degrees(angle)-90

    def update_enemy_speed(self):
        for banz in self.banzai_list:
            banz.center_x += banz.change_x
            banz.center_y += banz.change_y
            x_diff = self.player.sprite.center_x - banz.center_x
            y_diff = self.player.sprite.center_y - banz.center_y
            angle = math.atan2(y_diff, x_diff)
            if x_diff <= self.banzai.rage_area or y_diff <= self.banzai.rage_area:
                banz.change_x *= 2
                banz.change_y *= 2
                ! BRO TH ARE THESE ROCKETS LOL definitely fix this but keep in mind
            else:
                banz.change_x = math.cos(angle) * self.banzai.speed
                banz.change_y = math.sin(angle) * self.banzai.speed

    def on_show_view(self):
        self.window.set_mouse_visible(False)
        if self.curr_audio is None:
            self.curr_audio = self.bg_music.play(volume=float(conf.set_settings('Settings', 'bg_volume')), loop=True)

    def on_hide_view(self):
        self.window.set_mouse_visible(True)
        print('paused game')
        conf.logmn.log_info('paused game')

    def on_draw(self):
        self.clear()
        self.camera_sprites.use()
        self.bg_list.draw()
        self.sprite_list.draw()
        self.banzai_list.draw()
        self.wall_sprlist.draw()
        self.entities_list.draw()
        self.camera_gui.use()  # for later gui use
        self.crosshair.draw()
        arcade.draw_rect_filled(
            arcade.rect.XYWH(self.window.width // 2, self.window.height - 25, self.window.width, 50),
            arcade.color.BLACK)
        arcade.draw_rect_outline(
            arcade.rect.XYWH(self.window.width // 2, self.window.height - 25, self.window.width + 2, 50),
            arcade.color.GOLDEN_BROWN, 2)
        for i in range(self.player.lives + 1):
            live = arcade.Sprite(self.pl_lives)  # when adding lives do a max of 5 lives!
            if i + 1 == 1:
                live.left = (i + 1) * 16
                live.center_y = self.window.height - 25
            else:
                live.left = (i + 1) * 16 - (i + 1) * 8
                live.center_y = self.window.height - 25
            arcade.draw_sprite(live)
        arcade.Text(f"Score: {self.score}", self.window.width - 10, self.window.height - 25, arcade.color.WHITE,
                    anchor_x="right", anchor_y='center').draw()

    def on_update(self, delta_time):
        self.sprite_list.update(delta_time)

        if not self.recharge_flag:
            self.clocker.tick(delta_time)
            if self.clocker.ticks_since(0) <= (60 // self.pl_bullet_recharge) * (
                    self.clocker.ticks // (60 // self.pl_bullet_recharge)):
                self.recharge_flag = True
                self.clocker.tick(0)

        if self.shoot_flag and self.recharge_flag:
            self.create_bullets()
            self.recharge_flag = False

        self.update_enemy_angle()
        self.update_enemy_speed()
        self.update_bullets()
        self.update_crosshair(self.mouse_x, self.mouse_y)
        self.update_player_angle(self.pl_crsh.center_x, self.pl_crsh.center_y)
        self.update_player_speed()
        self.scroll_to_player()

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.ESCAPE:
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
        if key == arcade.key.U:
            self.create_enemy()
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
        self.game.wall_sprlist.draw()
        self.game.entities_list.draw()

        self.game.camera_gui.use()
        arcade.draw_rect_filled(
            arcade.rect.XYWH(self.window.width // 2, self.window.height - 25, self.window.width, 50),
            arcade.color.BLACK)
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
        arcade.Text(f"Score: {self.game.score}", self.window.width - 10, self.window.height - 25, arcade.color.WHITE,
                    anchor_x="right", anchor_y='center').draw()

        arcade.draw_rect_filled(
            arcade.rect.XYWH(self.window.width // 2, self.window.height // 2, self.window.width, self.window.height),
            [0, 0, 0, 128])
        arcade.Text("PAUSED", self.window.center_x, self.window.center_y + 50,
                    arcade.color.WHITE, font_size=50, anchor_x="center").draw()
        arcade.Text("Esc - Return to game",
                    self.window.center_x,
                    self.window.center_y,
                    arcade.color.WHITE,
                    font_size=20,
                    anchor_x="center").draw()
        arcade.Text("Enter - Main menu",
                    self.window.center_x,
                    self.window.center_y - 30,
                    arcade.color.WHITE,
                    font_size=20,
                    anchor_x="center").draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            print('unpaused game')
            conf.logmn.log_info('unpaused game')
            self.window.show_view(self.game)
        elif key == arcade.key.ENTER:
            print('closing game')
            conf.logmn.log_info('closing game')
            arcade.stop_sound(self.game.curr_audio)
            self.window.show_view(self.game.main_menu)

    def on_key_release(self, key, modifiers):
        self.game.on_key_release(key, modifiers)
