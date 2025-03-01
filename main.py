"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template
"""
import arcade
import arcade.clock
import file_mngr.conf_mngr as conf
from tkinter.filedialog import askopenfilename
import shutil
import player
import game_loop
from arcade.gui import (
    UIManager,
    UITextureButton,
    UIFlatButton,
    UILabel,
    UIBoxLayout,
    UIView,
)

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

        self.background_color = arcade.color.AMAZON
        self.curr_audio = None
        self.bg_flag = False
        self.resize_flag = False
        self.resize_count = 0
        self.ui = UIManager()
        self.bg_music_pre = conf.set_settings("Settings", "bg_music")
        self.bg_music = arcade.load_sound(self.bg_music_pre)
        self.bg_volume = float(conf.set_settings("Settings", "bg_volume"))
        self.player_sprite = conf.set_settings("Settings", "player_sprite")
        self.pl_bullet_sprite = conf.set_settings("Settings", "pl_bul_sprite")
        self.pl_bullet_audio = conf.set_settings("Settings", "pl_bul_audio")
        self.pl_bullet_audio_compl = arcade.load_sound(self.pl_bullet_audio)
        self.pl_bullet_speed = 5
        self.pl_bullet_recharge = 12
        self.player = player.Player(self.player_sprite, self.pl_bullet_sprite, self.pl_bullet_audio_compl, 0.5, 0.5)
        self.player.angle = -90
        self.player.center_x = window.center_x
        self.player.center_y = window.center_y
        self.test_flag = False
        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(self.player)
        self.entities_list = arcade.SpriteList()
        self.shoot_flag = False
        self.recharge_flag = False
        self.clocker = arcade.clock.Clock()

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
        # about the next thing - I DONT KNOW WHY BUT THIS IS LEGITIMATELY THE ONLY WAY TO CENTER THE BUTTONS PROPERLY
        # WHY? I DONT KNOW!!!
        # edit: IT DOESNT WORK. im gonna do some horrible things to this library if this continues

        self.menu_buttons.center = self.menu_buttons_center
        self.menu_buttons.center_on_screen()
        self.settings_buttons.center = self.settings_buttons_center
        self.settings_buttons.center_on_screen()
        self.menu_buttons_center = self.menu_buttons.center
        self.settings_buttons_center = self.settings_buttons.center
        self.menu_buttons.center = self.menu_buttons_center
        self.settings_buttons.center = self.settings_buttons_center

        self.volume_text.disabled = True

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False


    def reset(self):
        """Reset the game to the initial state."""
        # Do changes needed to restart the game here if you want to support that
        pass

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
        if self.clocker.ticks == 2:
            print('yes') # WHY DOESNT THIS CENTER THE BUTTONS WHYYYYYYYYYYYY
            self.menu_buttons.center = self.menu_buttons_center
            self.settings_buttons.center = self.settings_buttons_center

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
        arcade.play_sound(self.player.bullet_audio)
        bullet = arcade.Sprite(self.player.bullet_sprite)
        bullet.change_y = self.pl_bullet_speed
        bullet.center_x = self.player.center_x
        bullet.bottom = self.player.top
        self.entities_list.append(bullet)

    def update_bullets(self):
        self.entities_list.update()
        for entity in self.entities_list:
            if entity.bottom > win_height or entity.top < 0 or entity.right < 0 or entity.left > win_width:
                entity.remove_from_sprite_lists()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.sprite_list.update(delta_time)
        self.clocker.tick(delta_time)

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

        if not self.recharge_flag and self.clocker.ticks_since(0) <= (60 // self.pl_bullet_recharge) * (self.clocker.ticks // (60 // self.pl_bullet_recharge)):
            self.recharge_flag = True
            print('recharged')

        if self.shoot_flag and self.recharge_flag:
            self.create_bullets()
            self.recharge_flag = False

        self.update_bullets()

    def update_player_speed(self):

        self.player.change_x = 0
        self.player.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player.change_y = 2
        elif self.down_pressed and not self.up_pressed:
            self.player.change_y = -2
        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -2
        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = 2

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        if key == arcade.key.P and not self.bg_flag:
            self.curr_audio = self.bg_music.play()
            self.curr_audio.volume = self.bg_volume
            self.bg_flag = True
        elif key == arcade.key.P and self.bg_flag:
            arcade.stop_sound(self.curr_audio)
            self.bg_flag = False
        if key == arcade.key.L:
            self.test_flag = not self.test_flag
        if key == arcade.key.H:
            self.menu_buttons.center = self.menu_buttons_center
            self.settings_buttons.center = self.settings_buttons_center

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
        """
        Called whenever the mouse moves.
        """
        pass

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
