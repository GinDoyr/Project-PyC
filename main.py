import arcade
import arcade.clock
from arcade.gui import (
    UIManager,
    UITextureButton,
    UIFlatButton,
    UIBoxLayout,
    UIView)
import file_mngr.conf_mngr as conf
from tkinter.filedialog import askopenfilename
import shutil
import game_loop


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

        # gui
        self.ui = UIManager()
        self.menu_buttons = self.ui.add(UIBoxLayout())
        self.start = self.menu_buttons.add(
            UITextureButton(
                text="Start Game Loop",
                texture=TEX_RED_BUTTON_NORMAL,
                texture_hovered=TEX_RED_BUTTON_HOVER,
                texture_pressed=TEX_RED_BUTTON_PRESS))
        self.button = self.menu_buttons.add(
            UITextureButton(
                text="Window Size Change",
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

    def on_update(self, delta_time):
        @self.start.event("on_click")
        def on_click(event):
            game = game_loop.GameLoop(self, window)
            window.show_view(game)

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

        if key == arcade.key.H:
            self.menu_buttons.center_on_screen()
            self.settings_buttons.center_on_screen()

    def on_key_release(self, key, key_modifiers):
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        pass


def main():
    menu = Main_menu()
    window.show_view(menu)
    arcade.run()


if __name__ == "__main__":
    main()
