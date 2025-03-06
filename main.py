import arcade
import arcade.clock
from arcade.gui import (
    UIManager,
    UITextureButton,
    UIFlatButton,
    UIBoxLayout,
    UISlider,
    UILabel)
import file_mngr.conf_mngr as conf
import game_loop
import asset_selector


win_title = "Project: PyC"
conf.load_settings()
win_width = int(conf.set_settings("Settings", "win_width"))
win_height = int(conf.set_settings("Settings", "win_height"))
TEX_RED_BUTTON_NORMAL = arcade.load_texture(":resources:gui_basic_assets/button/red_normal.png")
button_conf_norm = arcade.load_texture(":resources:gui_basic_assets/button/red_normal.png")
TEX_RED_BUTTON_HOVER = arcade.load_texture(":resources:gui_basic_assets/button/red_hover.png")
TEX_RED_BUTTON_PRESS = arcade.load_texture(":resources:gui_basic_assets/button/red_press.png")
window = arcade.Window(win_width, win_height, win_title)
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
        self.sfx_volume = float(conf.set_settings("Settings", "sfx_volume"))

        # flags
        self.bg_flag = False
        self.resize_flag = False
        self.menu_center_flag = False
        self.menu_exists = False

        # gui
        self.ui = UIManager()

        # main menu
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
        self.exit_main = self.menu_buttons.add(
            UITextureButton(
                text="Exit",
                texture=button_conf_norm,
                texture_hovered=TEX_RED_BUTTON_HOVER,
                texture_pressed=TEX_RED_BUTTON_PRESS))

        # settings
        self.settings_buttons = self.ui.add(UIBoxLayout())
        self.video_conf = self.settings_buttons.add(UIFlatButton(text='Graphics'))
        self.audio_conf = self.settings_buttons.add(UIFlatButton(text="Audio"))
        self.contrl_conf = self.settings_buttons.add(UIFlatButton(text="Controls"))
        self.assets_conf = self.settings_buttons.add(UIFlatButton(text="Assets"))
        self.back_conf = self.settings_buttons.add(UIFlatButton(text="Back"))

        # audio settings
        self.audio_buttons = self.ui.add(UIBoxLayout())
        self.mus_text = self.audio_buttons.add(UILabel(text=f'Music: {int(self.bg_volume * 100)}%'))
        self.mus_slider = self.audio_buttons.add(UISlider(value=self.bg_volume*100, width=250))
        self.sfx_text = self.audio_buttons.add(UILabel(text=f'Sound effects: {int(self.sfx_volume * 100)}%'))
        self.sfx_slider = self.audio_buttons.add(UISlider(value=self.sfx_volume*100, width=250))
        self.confirm_vol = self.audio_buttons.add(UIFlatButton(text="Save changes", multiline=True))
        self.back_vol = self.audio_buttons.add(UIFlatButton(text="Back"))

        # assets selection
        self.assets_buttons = self.ui.add(UIBoxLayout())
        self.audio_assets = self.assets_buttons.add(UIFlatButton(text="Audio"))
        self.sprites_assets = self.assets_buttons.add(UIFlatButton(text="Sprites"))
        self.back_assets = self.assets_buttons.add(UIFlatButton(text="Back"))

        # button flags
        self.settings_buttons.visible = False
        self.audio_buttons.visible = False
        self.assets_buttons.visible = False

        # gui defs
        # main menu buttons
        @self.start.event("on_click")
        def on_click(event):
            game = game_loop.GameLoop(self)
            window.show_view(game)

        @self.button.event("on_click")
        def on_click(event):
            self.resize_flag = True

        @self.button_conf.event("on_click")
        def on_click(event):
            self.settings_buttons.visible = True
            self.menu_buttons.visible = False

        @self.exit_main.event("on_click")
        def on_click(event):
            print("closing game")
            window.close()

        # settings buttons
        @self.video_conf.event("on_click")
        def on_click(event):
            print('graphics WIP')

        @self.audio_conf.event("on_click")
        def on_click(event):
            self.settings_buttons.visible = False
            self.audio_buttons.visible = True

        @self.contrl_conf.event("on_click")
        def on_click(event):
            # self.settings_buttons.visible = False
            print('controls WIP')

        @self.assets_conf.event("on_click")
        def on_click(event):
            self.settings_buttons.visible = False
            self.assets_buttons.visible = True

        @self.back_conf.event("on_click")
        def on_click(event):
            self.settings_buttons.visible = False
            self.menu_buttons.visible = True

        # audio buttons
        @self.mus_slider.event('on_change')
        def on_change(event):
            self.bg_volume = round(self.mus_slider.value)/100
            if self.curr_audio is not None:
                self.curr_audio.volume = round(self.bg_volume)
            self.mus_text.text = f'Music: {int(self.bg_volume * 100)}%'

        @self.sfx_slider.event('on_change')
        def on_change(event):
            self.sfx_volume = round(self.sfx_slider.value)/100
            self.sfx_text.text = f'Sound effects: {int(self.sfx_volume * 100)}%'

        @self.confirm_vol.event("on_click")
        def on_click(event):
            conf.update_setting("Settings", "bg_volume", str(self.bg_volume))
            conf.update_setting("Settings", "sfx_volume", str(self.sfx_volume))
            print(f'volume saved to {self.bg_volume}, sfx saved to {self.sfx_volume}')

        @self.back_vol.event("on_click")
        def on_click(event):
            self.audio_buttons.visible = False
            self.settings_buttons.visible = True

        # assets buttons
        @self.audio_assets.event("on_click")
        def on_click(event):
            assets = asset_selector.AssetSelector(self.audio_assets.text, self)
            window.show_view(assets)

        @self.sprites_assets.event("on_click")
        def on_click(event):
            assets = asset_selector.AssetSelector(self.sprites_assets.text, self)
            window.show_view(assets)

        @self.back_assets.event("on_click")
        def on_click(event):
            self.assets_buttons.visible = False
            self.settings_buttons.visible = True

    def on_show_view(self) -> None:
        self.ui.enable()

    def on_hide_view(self) -> None:
        self.ui.disable()
        self.menu_exists = True
        if self.bg_flag:
            arcade.stop_sound(self.curr_audio)
            self.bg_flag = False

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
            self.clear()
            window.set_location(window.get_location()[0] + 4, window.get_location()[1])
            self.resize_count += 1
            if self.resize_count == 50:
                print(window.get_size())
                print(window.get_location())
        else:
            self.resize_flag = False
            self.resize_count = 0

        if self.menu_exists:
            self.menu_buttons.center_on_screen()
            self.settings_buttons.center_on_screen()
            self.audio_buttons.center_on_screen()
            self.assets_buttons.center_on_screen()
            self.menu_exists = False

        self.ui.draw()

        # this finally centers the buttons properly. my god
        if not self.menu_center_flag:
            self.menu_buttons.center_on_screen()
            self.settings_buttons.center_on_screen()
            self.audio_buttons.center_on_screen()
            self.assets_buttons.center_on_screen()
            self.menu_center_flag = True

    def on_update(self, delta_time):
        if self.bg_flag:
            if not self.bg_music.is_playing(self.curr_audio): # tried is_complete here, didnt work for some reason ¯\_(ツ)_/¯
                self.curr_audio = self.bg_music.play(volume=self.bg_volume)

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
                self.curr_audio = self.bg_music.play(volume=self.bg_volume)
                self.bg_flag = True

        if key == arcade.key.H:
            self.menu_buttons.center_on_screen()
            self.settings_buttons.center_on_screen()


def main():
    menu = Main_menu()
    window.show_view(menu)
    arcade.run()


if __name__ == "__main__":
    main()
