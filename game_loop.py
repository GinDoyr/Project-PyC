import arcade
import arcade.clock
from arcade.math import rotate_point
import file_mngr.conf_mngr as conf
import file_mngr.zip_mngr as zipmn
import player
import enemies
import math


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


class GameLoop(arcade.View):
    def __init__(self, main_menu):
        super().__init__()

        conf.logmn.log_info('launching game loop')

        # misc
        self.clocker = arcade.clock.Clock()
        self.main_menu = main_menu
        self.mouse_x, self.mouse_y = self.window.center_x, self.window.center_y

        # sound
        self.curr_audio = None
        if conf.set_settings('Settings', 'resourcepack') != 'None':  # and so this is probably going to happen everywhere... i still don't know whether i should make this a func or not
            zipmn.load_resourcepack(conf.set_settings('Settings', 'resourcepack'))
            try:
                self.bg_music = zipmn.load_from_resourcepack(conf.set_settings('Settings', 'resourcepack'), 'Audio', 'music_game', streaming=True)
            except:
                self.bg_music = arcade.load_sound(conf.set_settings("Audio", "music_game"), streaming=True)
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
        if conf.set_settings('Settings', 'resourcepack') != 'None':  # i should definitely make this a function somehow, very bad i keep repeating it over and over
            zipmn.load_resourcepack(conf.set_settings('Settings', 'resourcepack'))
            try:
                self.player_sprite = zipmn.load_from_resourcepack(conf.set_settings('Settings', 'resourcepack'), 'Sprites', 'player_sprite', scale=0.2)
            except:
                self.player_sprite = arcade.Sprite(conf.set_settings('Sprites', 'player_sprite'), scale=0.2)
            try:
                self.pl_bullet_sprite = zipmn.load_from_resourcepack(conf.set_settings('Settings', 'resourcepack'), 'Sprites', 'player_bullet')
            except:
                self.pl_bullet_sprite = arcade.Sprite(conf.set_settings('Sprites', 'player_bullet'))
            try:
                self.pl_crsh = zipmn.load_from_resourcepack(conf.set_settings('Settings', 'resourcepack'), 'Sprites', 'player_crosshair')
            except:
                self.pl_crsh = arcade.Sprite(conf.set_settings("Sprites", "player_crosshair"))
            try:
                self.pl_bullet_audio = zipmn.load_from_resourcepack(conf.set_settings('Settings', 'resourcepack'), 'Audio', 'player_bullet')
            except:
                self.pl_bullet_audio = arcade.load_sound(conf.set_settings("Audio", "player_bullet"))
        else:
            self.player_sprite = arcade.Sprite(conf.set_settings('Sprites', 'player_sprite'), scale=0.2)
            self.pl_bullet_sprite = arcade.Sprite(conf.set_settings('Sprites', 'player_bullet'))
            self.pl_crsh = arcade.Sprite(conf.set_settings("Sprites", "player_crosshair"))
            self.pl_bullet_audio = arcade.load_sound(conf.set_settings("Audio", "player_bullet"))
        self.pl_bullet_speed = 10
        self.pl_bullet_recharge = 6  # higher - faster
        self.player = player.Player(self.player_sprite, self.pl_bullet_sprite, self.pl_bullet_audio)
        self.pl_speed = 10
        self.player.sprite.center_x = self.window.center_x
        self.player.sprite.center_y = self.window.center_y
        self.pl_bul_hitbox = arcade.Sprite("assets/sprites/misc/very_important_1x1.png")
        self.pl_bul_hitbox.bottom = self.player.sprite.top
        self.pl_bul_hitbox.center_x = self.player.sprite.center_x

        # sprite lists
        self.sprite_list = arcade.SpriteList()
        self.entities_list = arcade.SpriteList()
        self.sprite_list.append(self.player.sprite)
        self.sprite_list.append(self.pl_crsh)
        self.sprite_list.append(self.pl_bul_hitbox)
        self.pl_bul_hitbox.visible = False

    def update_crosshair(self, x, y):
        self.pl_crsh.center_x = x
        self.pl_crsh.center_y = y

    def update_player_speed(self):

        self.player.sprite.change_x = 0
        self.player.sprite.change_y = 0
        self.pl_bul_hitbox.change_y = 0
        self.pl_bul_hitbox.change_x = 0

        if self.up_pressed and not self.down_pressed:
            self.player.sprite.change_y = self.pl_speed
            self.pl_bul_hitbox.change_y = self.player.sprite.change_y
        elif self.down_pressed and not self.up_pressed:
            self.player.sprite.change_y = -self.pl_speed
            self.pl_bul_hitbox.change_y = self.player.sprite.change_y
        if self.left_pressed and not self.right_pressed:
            self.player.sprite.change_x = -self.pl_speed
            self.pl_bul_hitbox.change_x = self.player.sprite.change_x
        elif self.right_pressed and not self.left_pressed:
            self.player.sprite.change_x = self.pl_speed
            self.pl_bul_hitbox.change_x = self.player.sprite.change_x

    def update_player_angle(self, x, y):
        x_angle = x - self.player.sprite.center_x
        y_angle = y - self.player.sprite.center_y
        angle = math.atan2(-y_angle, x_angle)
        prev_angle = self.player.sprite.angle
        self.player.sprite.angle = math.degrees(angle) + 90
        rotate_around_point(self.pl_bul_hitbox, self.player.sprite.position, self.player.sprite.angle - prev_angle)

    def create_bullets(self):
        arcade.play_sound(self.player.bullet_audio, volume=float(conf.set_settings('Settings', 'sfx_volume')))
        bullet = arcade.Sprite(self.player.bullet_sprite.texture)
        angle = math.radians(self.player.sprite.angle)
        bullet.angle = math.degrees(angle)
        bullet.change_y = self.pl_bullet_speed * math.cos(angle)
        bullet.change_x = self.pl_bullet_speed * math.sin(angle)
        bullet.position = self.pl_bul_hitbox.position
        self.entities_list.append(bullet)

    def update_bullets(self):
        self.entities_list.update()
        for entity in self.entities_list:
            if entity.bottom > self.window.height or entity.top < 0 or entity.right < 0 or entity.left > self.window.width:
                entity.remove_from_sprite_lists()

    def on_show_view(self):
        self.window.set_mouse_visible(False)
        self.curr_audio = self.bg_music.play(volume=float(conf.set_settings('Settings', 'bg_volume')), loop=True)

    def on_hide_view(self):
        self.window.set_mouse_visible(True)
        arcade.stop_sound(self.curr_audio)
        print('closing game loop')
        conf.logmn.log_info('closing game loop')

    def on_draw(self):
        self.clear()
        self.sprite_list.draw()
        self.entities_list.draw()

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

        self.update_bullets()
        self.update_crosshair(self.mouse_x, self.mouse_y)
        self.update_player_angle(self.mouse_x, self.mouse_y)

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.main_menu)
        if key == arcade.key.A:
            self.left_pressed = True
            self.update_player_speed()
        if key == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()
        if key == arcade.key.W:
            self.up_pressed = True
            self.update_player_speed()
        if key == arcade.key.S:
            self.down_pressed = True
            self.update_player_speed()
        if key == arcade.key.SPACE:
            self.shoot_flag = True

    def on_key_release(self, key, key_modifiers):
        if key == arcade.key.A:
            self.left_pressed = False
            self.update_player_speed()
        if key == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()
        if key == arcade.key.W:
            self.up_pressed = False
            self.update_player_speed()
        if key == arcade.key.S:
            self.down_pressed = False
            self.update_player_speed()
        if key == arcade.key.SPACE:
            self.shoot_flag = False

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button, key_modifiers):
        self.shoot_flag = True

    def on_mouse_release(self, x, y, button, key_modifiers):
        self.shoot_flag = False
