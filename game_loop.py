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
        # commented for now, resolve later
        # self.window.width, self.window.height = self.window.width//4, 7*self.window.height//8
        # self.window.center_window()

        conf.logmn.log_info('launching game loop')

        # misc
        self.clocker = arcade.clock.Clock()
        self.main_menu = main_menu
        self.mouse_x, self.mouse_y = 3000, 3000

        # sound
        self.curr_audio = None
        if conf.set_settings('Settings', 'resourcepack') != 'None':
            zipmn.load_resourcepack(conf.set_settings('Settings', 'resourcepack'))
            self.bg_music = zipmn.try_loading_from_resourcepack(conf.set_settings('Settings', 'resourcepack'), 'Audio', 'music_game', streaming=True)
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
        if conf.set_settings('Settings', 'resourcepack') != 'None':  # ok so i've made some function but still looks like a mess. or not. idk, but it works :D
            player_sprite = zipmn.try_loading_from_resourcepack('Sprites', 'player_sprite', scale=0.2)
            pl_bullet_sprite = zipmn.try_loading_from_resourcepack('Sprites', 'player_bullet', scale=2.0)
            self.pl_crsh = zipmn.try_loading_from_resourcepack('Sprites', 'player_crosshair')
            pl_bullet_audio = zipmn.try_loading_from_resourcepack('Audio', 'player_bullet')
        else:
            player_sprite = arcade.Sprite(conf.set_settings('Sprites', 'player_sprite'), scale=0.2)
            pl_bullet_sprite = arcade.Sprite(conf.set_settings('Sprites', 'player_bullet'), scale=2.0)
            self.pl_crsh = arcade.Sprite(conf.set_settings("Sprites", "player_crosshair"))
            pl_bullet_audio = arcade.load_sound(conf.set_settings("Audio", "player_bullet"))
        self.pl_bullet_speed = 10
        self.pl_bullet_recharge = 6  # higher - faster
        self.player = player.Player(player_sprite, pl_bullet_sprite, pl_bullet_audio)
        self.pl_speed = 10
        self.player.sprite.center_x = 1500
        self.player.sprite.center_y = 1500
        self.pl_bul_hitbox = arcade.Sprite("assets/sprites/misc/very_important_1x1.png")
        self.pl_bul_hitbox.bottom = self.player.sprite.top
        self.pl_bul_hitbox.center_x = self.player.sprite.center_x

        # background attempt and init of main sprite list
        self.bg_list = arcade.SpriteList()
        if conf.set_settings('Settings', 'resourcepack') != 'None':
            self.bg_texture = zipmn.try_loading_from_resourcepack('Sprites', 'other_background').texture
        else:
            self.bg_texture = arcade.Sprite(conf.set_settings('Sprites', 'other_background')).texture
        for x in range(0, 3000, int(self.bg_texture.width)):
            for y in range(0, 3000, int(self.bg_texture.height)):
                background = arcade.Sprite(self.bg_texture)
                background.left, background.bottom = x, y
                self.bg_list.append(background)

        # wall attempt...
        self.wall_sprlist = arcade.SpriteList()
        if conf.set_settings('Settings', 'resourcepack') != 'None':
            self.wall_sprite = zipmn.try_loading_from_resourcepack('Sprites', 'other_walls').texture
        else:
            self.wall_sprite = arcade.Sprite(conf.set_settings('Sprites', 'other_walls')).texture
        for x in range(0, 3000 + int(self.wall_sprite.width), int(self.wall_sprite.width)):
            if x >= 3000:
                x = 3000 - self.wall_sprite.width
            for y in range(0, 3000 + int(self.wall_sprite.height), int(self.wall_sprite.height)):
                if y >= 3000:
                    y = 3000 - self.wall_sprite.height
                if y == 0 or y == 3000 - self.wall_sprite.height:
                    wall = arcade.Sprite(self.wall_sprite)
                    wall.left, wall.bottom = x, y
                    self.wall_sprlist.append(wall)
                elif x == 0 or x == 3000 - self.wall_sprite.width:
                    wall = arcade.Sprite(self.wall_sprite)
                    wall.left, wall.bottom = x, y
                    self.wall_sprlist.append(wall)


        # sprite lists
        self.sprite_list = arcade.SpriteList()
        self.entities_list = arcade.SpriteList()
        self.crosshair = arcade.SpriteList()
        self.crosshair.append(self.pl_crsh)
        self.sprite_list.append(self.player.sprite)
        self.sprite_list.append(self.pl_bul_hitbox)
        self.pl_bul_hitbox.visible = False

        # there's the camera (wip, as is everything)
        self.camera_sprites = arcade.Camera2D()
        self.camera_gui = arcade.Camera2D()

    def scroll_to_player(self): # taken from arcade camera example
        """
        Scroll the window to the player.

        if CAMERA_SPEED is 1, the camera will immediately move to the desired
        position. Anything between 0 and 1 will have the camera move to the
        location with a smoother pan.
        """

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
            if self.player.sprite.top + self.pl_speed <= 6000 - self.wall_sprite.height:  # to do: normal collision with wall sprite list instead of this bruteforce lol. although it works... idk
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
            if self.player.sprite.right + self.pl_speed <= 6000 - self.wall_sprite.width:
                self.player.sprite.change_x = self.pl_speed
                self.pl_bul_hitbox.change_x = self.player.sprite.change_x

    def update_player_angle(self, x, y):
        if self.player.sprite.center_x > 1500:  # alr, to do: replace all these 1500 numbers with normal vars and do this updating correctly. peace
            x_angle = x - (self.player.sprite.center_x - 1500)
            print(x_angle)!
        y_angle = y - self.player.sprite.center_y
        angle = math.atan2(-y_angle, x_angle)
        prev_angle = self.player.sprite.angle
        self.player.sprite.angle = math.degrees(angle) + 90
        angle = self.player.sprite.angle
        # print(angle)  # dont mind this, planning to finally do that rotation thingy and i know what's below is something real bad lol
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

        rotate_around_point(self.pl_bul_hitbox, self.player.sprite.position, angle - prev_angle)

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
            if entity.top > 3000 - self.wall_sprite.height or entity.bottom < self.wall_sprite.height or entity.left < self.wall_sprite.width or entity.right > 3000 - self.wall_sprite.width:
                # ... this is just awful. i really, REALLY need to make this better somehow. later, as is everything :P
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
        self.camera_sprites.use()
        self.bg_list.draw()
        self.sprite_list.draw()
        self.wall_sprlist.draw()
        self.entities_list.draw()
        self.camera_gui.use()  # for later gui use
        self.crosshair.draw()


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
        self.update_player_angle(self.pl_crsh.center_x, self.pl_crsh.center_y)
        self.update_player_speed()
        self.scroll_to_player()

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.main_menu)
        if key == arcade.key.A:
            self.left_pressed = True
        if key == arcade.key.D:
            self.right_pressed = True
        if key == arcade.key.W:
            self.up_pressed = True
        if key == arcade.key.S:
            self.down_pressed = True
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
