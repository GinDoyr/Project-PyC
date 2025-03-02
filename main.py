import arcade
import arcade.clock
from arcade.math import rotate_point
from arcade.gui import (
    UIManager,
    UITextureButton,
    UIFlatButton,
    UIBoxLayout,
    UIView,
)
import file_mngr.conf_mngr as conf
from tkinter.filedialog import askopenfilename
import shutil
import player
import game_loop
import math


win_title = "Project: PyC"
settings = conf.load_settings()
win_width = int(conf.set_settings("Settings", "win_width"))
win_height = int(conf.set_settings("Settings", "win_height"))
TEX_RED_BUTTON_NORMAL = arcade.load_texture(":resources:gui_basic_assets/button/red_normal.png")
button_conf_norm = arcade.load_texture(":resources:gui_basic_assets/button/red_normal.png")
TEX_RED_BUTTON_HOVER = arcade.load_texture(":resources:gui_basic_assets/button/red_hover.png")
TEX_RED_BUTTON_PRESS = arcade.load_texture(":resources:gui_basic_assets/button/red_press.png")
window = arcade.Window(win_width, win_height, win_title, resizable=True)
window.center_window()


class Main_menu(arcade.View):
    def __init__(self):
        super().__init__()

        # misc
        self.background_color = arcade.color.BLACK
        self.resize_count = 0
        self.clocker = arcade.clock.Clock()

        # sound
        self.curr_audio = None
        self.bg_music_pre = conf.set_settings("Settings", "bg_music")
        self.bg_music = arcade.load_sound(self.bg_music_pre)
        self.bg_volume = float(conf.set_settings("Settings", "bg_volume"))

        # flags
        self.bg_flag = False
        self.resize_flag = False
        self.shoot_flag = False
        self.recharge_flag = False
        self.test_flag = False
        self.mouse_flag = True
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.rotation_l = False
        self.rotation_r = False

        # player stuff
        # PLEASE MAKE SURE SPRITE LOOKS UP! mb make a confirm window to adjust the import sprite angle?
        self.player_sprite = conf.set_settings("Settings", "player_sprite")
        self.pl_bullet_sprite = conf.set_settings("Settings", "pl_bul_sprite")
        self.pl_bullet_audio = conf.set_settings("Settings", "pl_bul_audio")
        self.pl_crsh_sprite = conf.set_settings("Settings", "pl_crsh_sprite")
        self.pl_crsh = arcade.Sprite(self.pl_crsh_sprite)
        self.pl_bullet_audio_compl = arcade.load_sound(self.pl_bullet_audio)
        self.pl_bullet_speed = 5
        self.pl_bullet_recharge = 12
        self.player = player.Player(self.player_sprite, self.pl_bullet_sprite, self.pl_bullet_audio_compl, 0.5, 0.5)
        self.player.center_x = window.center_x
        self.player.center_y = window.center_y
        self.pl_bul_hitbox = arcade.Sprite("assets/sprites/misc/very_important_1x1.png")
        self.pl_bul_hitbox.bottom = self.player.top

        # sprite lists and appends
        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(self.player)
        self.sprite_list.append(self.pl_crsh)
        self.sprite_list.append(self.pl_bul_hitbox)
        self.pl_bul_hitbox.visible = False
        self.entities_list = arcade.SpriteList()

        # gui
        self.ui = UIManager()
        self.menu_buttons = self.ui.add(UIBoxLayout())
        self.button = self.menu_buttons.add(
            UITextureButton(
                text="Hello Привет",
                texture=TEX_RED_BUTTON_NORMAL,
                texture_hovered=TEX_RED_BUTTON_HOVER,
                texture_pressed=TEX_RED_BUTTON_PRESS))
        self.button_conf = self.menu_buttons.add(
            UITextureButton(
                text="Settings",
                texture=button_conf_norm,
                texture_hovered=TEX_RED_BUTTON_HOVER,
                texture_pressed=TEX_RED_BUTTON_PRESS))
        self.settings_buttons = self.ui.add(UIBoxLayout())
        self.volume_up = self.settings_buttons.add(
            UIFlatButton(text="Volume +10")
        )
        self.volume_text = self.settings_buttons.add(
            UIFlatButton(text=f"Volume: {int(self.bg_volume*100)}")
        )
        self.volume_down = self.settings_buttons.add(
            UIFlatButton(text="Volume -10")
        )
        self.confirm_vol = self.settings_buttons.add(
            UIFlatButton(text="Save changes and exit settings", multiline=True)
        )
        self.load_bg = self.settings_buttons.add(
            UIFlatButton(text="Load background music", multiline=True)
        )
        self.select_bg = self.settings_buttons.add(
            UIFlatButton(text="Select loaded bg music", multiline=True)
        )
        self.bg_curr = self.settings_buttons.add(
            UIFlatButton(text=f"Current music: {str(self.bg_music_pre)[self.bg_music_pre.rfind('/')+1:-4]}", multiline=True)
        )
        self.settings_buttons.visible = False
        # im hoping to somehow minimize this centering part but idk how to rn
        self.sett_cent_w = 0
        self.sett_cent_h = 0
        self.main_cent_w = 0
        self.main_cent_h = 0
        for i in self.menu_buttons.children:
            if self.main_cent_w == 0:
                self.main_cent_w = i.width
            self.main_cent_h += i.height
        for i in self.settings_buttons.children:
            if self.sett_cent_w == 0:
                self.sett_cent_w = i.width
            self.sett_cent_h += i.height
        self.menu_buttons_center = (self.window.center_x-(self.main_cent_w//2), self.window.center_y-(self.main_cent_h//2))
        self.settings_buttons_center = (self.window.center_x - (self.sett_cent_w // 2), self.window.center_y - (self.sett_cent_h // 2))
        self.menu_buttons.center = self.menu_buttons_center
        self.settings_buttons.center = self.settings_buttons_center
        self.volume_text.disabled = True

    def on_show_view(self) -> None:
        self.ui.enable()

    def on_hide_view(self) -> None:
        self.ui.disable()

    # def resize_screen(self, change_x: int, change_y: int, move_x: int, move_y: int, move_loc: str,
    #                   method: str = 'middle', speed: int = 1) -> None:
    #     """
    #     :param change_x: change the resulting window width
    #     :param change_y: change the resulting window height
    #     :param move_x: move the window by x
    #     :param move_y:move the window by y
    #     :param move_loc: top, down, left, right. f.e: if you choose left, the screen moves from the right to the left
    #     :param method: how should the resize happen
    #     :param speed: how fast should the resize happen
    #     :return: hopefully a working resize function
    #     """
    #     pass

    def on_draw(self):
        """
        Render the screen.
        """
        self.clear()

        if self.resize_flag and self.resize_count <= 24:
            window.width += 4
            window.height -= 4
            self.resize_count += 1
        elif self.resize_count >= 25 and self.resize_count != 50:
            if self.resize_count == 25:
                print(window.get_size())
                print(window.get_location())
            window.width -= 4
            window.height += 4
            self.menu_buttons.move(-4, 0) # to move buttons you have to move the anchor, not its elements! either move the whole set of buttons or do each button with their own anchor
            window.set_location(window.get_location()[0] + 4, window.get_location()[1])
            self.resize_count += 1
            if self.resize_count == 50:
                print(window.get_size())
                print(window.get_location())
        else:
            self.resize_flag = False
            self.resize_count = 0

        self.ui.draw()

        if self.test_flag:
            self.sprite_list.draw()
            self.sprite_list.draw_hit_boxes()
            self.entities_list.draw()

    def create_bullets(self):
        arcade.play_sound(self.player.bullet_audio, volume=0.2)
        bullet = arcade.Sprite(self.player.bullet_sprite)
        angle = math.radians(self.player.angle)
        bullet.angle = math.degrees(angle)
        bullet.change_y = self.pl_bullet_speed * math.cos(angle)
        bullet.change_x = self.pl_bullet_speed * math.sin(angle)
        bullet.position = self.pl_bul_hitbox.position
        self.entities_list.append(bullet)

    def update_crosshair(self, x, y):
        self.pl_crsh.center_x = x
        self.pl_crsh.center_y = y

    def update_bullets(self):
        self.entities_list.update()
        for entity in self.entities_list:
            if entity.bottom > window.height or entity.top < 0 or entity.right < 0 or entity.left > window.width:
                entity.remove_from_sprite_lists()

    def rotate_around_point(self, sprite, point, degrees):
        """
        Rotate the sprite around a point by the set amount of degrees

        You could remove the change_angle keyword and/or angle change
        if you know that sprites will always or never change angle.

        Args:
            point:
                The point that the sprite will rotate about
            degrees:
                How many degrees to rotate the sprite
        """
        # there's still smth to do here. try out anything you can think of
        sprite.position = rotate_point(
            sprite.center_x, sprite.center_y,
            point[0], point[1], degrees)
        print(sprite.position)

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.sprite_list.update(delta_time)

        @self.volume_down.event("on_click") #try a slider for the volume! there was a widget for it, look up in the examples GUI Widget Gallery
        def on_click(event):
            if round(self.bg_volume, 1) > 0:
                self.bg_volume = round(self.bg_volume - 0.1, 1)
                if self.curr_audio is not None:
                    self.curr_audio.volume = round(self.curr_audio.volume - 0.1, 1)
                self.volume_text.text = f"Volume: {int(self.bg_volume*100)}"

        @self.volume_up.event("on_click")
        def on_click(event):
            if round(self.bg_volume, 1) < 1:
                self.bg_volume = round(self.bg_volume + 0.1, 1)
                if self.curr_audio is not None:
                    self.curr_audio.volume = round(self.curr_audio.volume + 0.1, 1)
                self.volume_text.text = f"Volume: {int(self.bg_volume*100)}"

        @self.confirm_vol.event("on_click")
        def on_click(event):
            self.settings_buttons.visible = False
            self.menu_buttons.visible = True
            conf.update_setting("Settings", "bg_volume", str(self.bg_volume))

        @self.load_bg.event("on_click")
        def on_click(event):
            filename = askopenfilename()
            try:
                if not conf.check_path(f'assets/music/{filename[filename.rfind("/")+1:]}') and (filename.endswith('.mp3') or filename.endswith('.wav')):
                    shutil.copy(filename, 'assets/music')
                    print('loaded')
                else:
                    print("either alr loaded or incorrect file type")
            except:
                print("ERROR! idk what honestly")
            print(filename[filename.rfind("/")+1:], filename)

        @self.button_conf.event("on_click")
        def on_click(event):
            self.settings_buttons.visible = True
            self.menu_buttons.visible = False

        @self.button.event("on_click")
        def on_click(event):
            self.resize_flag = True

        if not self.recharge_flag:
            self.clocker.tick(delta_time)
            if self.clocker.ticks_since(0) <= (60 // self.pl_bullet_recharge) * (self.clocker.ticks // (60 // self.pl_bullet_recharge)):
                self.recharge_flag = True
                self.clocker.tick(0)

        if self.shoot_flag and self.recharge_flag:
            self.create_bullets()
            self.recharge_flag = False

        self.update_bullets()

    def update_player_speed(self):

        self.player.change_x = 0
        self.player.change_y = 0
        self.pl_bul_hitbox.change_y = 0
        self.pl_bul_hitbox.change_x = 0

        if self.up_pressed and not self.down_pressed:
            self.player.change_y = 2
            self.pl_bul_hitbox.change_y = self.player.change_y
        elif self.down_pressed and not self.up_pressed:
            self.player.change_y = -2
            self.pl_bul_hitbox.change_y = self.player.change_y
        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -2
            self.pl_bul_hitbox.change_x = self.player.change_x
        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = 2
            self.pl_bul_hitbox.change_x = self.player.change_x

    def update_player_angle(self, x, y):
        x_angle = x - self.player.center_x
        y_angle = y - self.player.center_y
        angle = math.atan2(-y_angle, x_angle)
        prev_angle = self.player.angle
        self.player.angle = math.degrees(angle) + 90
        self.rotate_around_point(self.pl_bul_hitbox, self.player.position, self.player.angle - prev_angle)

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        if key == arcade.key.P:
            if self.bg_flag:
                arcade.stop_sound(self.curr_audio)
                self.bg_flag = False
            elif not self.bg_flag:
                self.curr_audio = self.bg_music.play()
                self.curr_audio.volume = self.bg_volume
                self.bg_flag = True

        if key == arcade.key.L:
            self.test_flag, self.mouse_flag = not self.test_flag, not self.mouse_flag
            window.set_mouse_visible(self.mouse_flag)

        if key == arcade.key.H:
            self.menu_buttons.center_on_screen()
            self.settings_buttons.center_on_screen()

        if self.test_flag:
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
        """
        Called whenever the user lets off a previously pressed key.
        """
        if self.test_flag:
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

        if self.test_flag:
            self.update_crosshair(x, y)
            self.update_player_angle(x, y)


    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass


def main():
    game = Main_menu()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
