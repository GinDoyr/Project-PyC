import arcade
import arcade.clock
from arcade.gui import (
    UIManager,
    UITextureButton,
    UIFlatButton,
    UIBoxLayout,
    UIDropdown,
    UISlider,
    UILabel)
from arcade.gui.experimental import UIScrollArea
import file_mngr.conf_mngr as conf
import file_mngr.zip_mngr as zipmn
import game_loop
import asset_selector  # might wanna smh optimize the imports on all the other stuff, look if its possible plz :(

conf.logmn.log_info('starting...')
conf.load_settings()
win_title = "Project: PyC"
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
        conf.logmn.log_info('initializing main menu')

        # misc
        self.background_color = arcade.color.BLACK
        self.resize_count = 0
        self.clocker = arcade.clock.Clock()
        self.rspk_curr = None

        # sound
        self.curr_audio = None
        if conf.set_settings('Settings', 'resourcepack') != 'None':
            zipmn.load_resourcepack(conf.set_settings('Settings', 'resourcepack'))
            temp = conf.set_settings('Settings', 'resourcepack')
            self.rspk_curr = temp[temp.find('/')+1:]
            try:
                self.bg_music = zipmn.load_from_resourcepack(conf.set_settings('Settings', 'resourcepack'), 'Audio',
                                                             'music_main menu')
            except Exception as e:
                print(f'no main menu music in archive! {e}')
                conf.logmn.log_warning(f'no main menu music in archive! {e}')
                self.bg_music = arcade.load_sound(conf.set_settings("Audio", "music_main menu"))
        else:
            self.bg_music = arcade.load_sound(conf.set_settings("Audio", "music_main menu"))
        self.bg_volume = float(conf.set_settings("Settings", "bg_volume"))
        self.sfx_volume = float(conf.set_settings("Settings", "sfx_volume"))

        # flags
        self.bg_flag = False
        self.resize_flag = False
        self.menu_center_flag = False
        self.menu_exists = False
        self.reset_flag = False

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

        # graphics settings
        self.video_buttons = self.ui.add(UIBoxLayout())
        self.video_label = self.video_buttons.add(UILabel(text="Set resolution (still WIP dont even think i'll actually make it)"))
        self.video_drpd = self.video_buttons.add(UIDropdown(default='1280x720', options=['yes', '1280x720']))
        self.back_vid = self.video_buttons.add(UIFlatButton(text="Back"))

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
        self.resourcepacks_assets = self.assets_buttons.add(UIFlatButton(text='Resourcepacks'))
        self.back_assets = self.assets_buttons.add(UIFlatButton(text="Back"))

        # resourcepack selection
        rspk_buttons = self.ui.add(UIBoxLayout(x=self.window.width//4, size_hint=(1, 1)))
        # scroll area
        rspk_list = UIBoxLayout(size_hint=(1, 0), space_between=1)
        for i in conf.return_contents('resourcepacks'):
            button = UIFlatButton(height=30, size_hint=(1, None), text=f"{i}")
            rspk_list.add(button)
            button.on_click = self.select_click

        rspk_buttons_top = UIBoxLayout(size_hint=(1,1), space_between=10, vertical=False)
        v_scroll = rspk_buttons_top.add(UIBoxLayout(vertical=False, size_hint=(1/4, 1/2)))
        scroll_layout = v_scroll.add(UIScrollArea(size_hint=(1, 1)))
        scroll_layout.with_border(color=arcade.uicolor.WHITE)
        scroll_layout.add(rspk_list)
        scroll_layout.invert_scroll = True
        if conf.set_settings('Settings', 'resourcepack') != 'None':
            self.rspk_text = rspk_buttons_top.add(UILabel(width=200, text=f'Selected resourcepack: \n{self.rspk_curr}', multiline=True))
        else:
            self.rspk_text = rspk_buttons_top.add(UILabel(width=200, text=f'Selected resourcepack: \n', multiline=True))

        rspk_buttons_bottom = UIBoxLayout(vertical=False)
        rspk_confirm = rspk_buttons_bottom.add(UIFlatButton(text='Save selected'))
        rspk_remove = rspk_buttons_bottom.add(UIFlatButton(text='Set to default', multiline=True))
        rspk_back = rspk_buttons_bottom.add(UIFlatButton(text='Back'))

        rspk_buttons.add(rspk_buttons_top)
        rspk_buttons.add(rspk_buttons_bottom)

        # button flags
        self.settings_buttons.visible = False
        self.video_buttons.visible = False
        self.audio_buttons.visible = False
        self.assets_buttons.visible = False
        rspk_buttons.visible = False

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
            conf.logmn.log_info("see you next time :)")
            window.close()

        # settings buttons
        @self.video_conf.event("on_click")
        def on_click(event):
            self.settings_buttons.visible = False
            self.video_buttons.visible = True

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

        # graphics buttons
        @self.back_vid.event('on_click')
        def on_click(event):
            self.video_buttons.visible = False
            self.settings_buttons.visible = True

        # audio buttons
        @self.mus_slider.event('on_change')
        def on_change(event):
            self.bg_volume = round(self.mus_slider.value)/100
            if self.curr_audio is not None:
                self.curr_audio.volume = self.bg_volume
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
            conf.logmn.log_info(f'volume saved to {self.bg_volume}, sfx saved to {self.sfx_volume}')

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

        @self.resourcepacks_assets.event('on_click')
        def on_click(event):
            rspk_buttons.visible = True
            rspk_list.clear()
            for i in conf.return_contents('resourcepacks'):
                button = UIFlatButton(height=30, size_hint=(1, None), text=f"{i}")
                rspk_list.add(button)
                button.on_click = self.select_click
            self.assets_buttons.visible = False

        @self.back_assets.event("on_click")
        def on_click(event):
            self.assets_buttons.visible = False
            self.settings_buttons.visible = True

        # resourcepack buttons
        @rspk_confirm.event('on_click')
        def on_click(event):
            if self.rspk_curr is not None:
                print('trying to set resourcepack in settings...')
                conf.logmn.log_info('trying to set resourcepack in settings...')
                try:
                    conf.update_setting("Settings", "resourcepack", f'resourcepacks/{self.rspk_curr}')
                    zipmn.load_resourcepack(conf.set_settings('Settings', 'resourcepack'))
                    try:
                        self.bg_music = zipmn.load_from_resourcepack(conf.set_settings('Settings', 'resourcepack'), 'Audio', 'music_main menu')
                        arcade.stop_sound(self.curr_audio)
                    except Exception as e:
                        print(f'no main menu music in archive! {e}')
                        conf.logmn.log_warning(f'no main menu music in archive! {e}')
                except Exception as e:
                    print(f'failed! {e}')
                    conf.logmn.log_error(f'failed! {e}')

        @rspk_remove.event('on_click')
        def on_click(event):
            if conf.set_settings('Settings', 'resourcepack') != 'None':
                conf.update_setting('Settings', 'resourcepack', 'None')
                conf.create_sprites_and_audio_paths(conf.return_assets_dicts())
                self.bg_music = arcade.load_sound(conf.set_settings("Audio", "music_main menu"))
                if self.curr_audio is not None:
                    arcade.stop_sound(self.curr_audio)
                self.rspk_text.text = f'Selected resourcepack: \n'
                print('reset resourcepack to default (aka None)')
                conf.logmn.log_info('reset resourcepack to default (aka None)')

        @rspk_back.event('on_click')
        def on_click(event):
            rspk_buttons.visible = False
            self.assets_buttons.visible = True

    def select_click(self, event):
        self.rspk_curr = event.source.text
        self.rspk_text.text = f'Selected resourcepack: \n{self.rspk_curr}'

    def on_show_view(self) -> None:
        self.window.width = int(conf.set_settings("Settings", "win_width"))
        self.window.height = int(conf.set_settings("Settings", "win_height"))
        self.window.center_window()
        if self.reset_flag:
            self.__init__()
        self.ui.enable()
        if arcade.load_sound(conf.set_settings("Audio", "music_main menu")) != self.bg_music: # this kinda slows down the return to main menu, but hey, it makes it look like it's doing smth real good eh? :D yeah i might wanna fix it later smh
            self.bg_music = arcade.load_sound(conf.set_settings("Audio", "music_main menu"))
            self.curr_audio = None
            self.bg_flag = False

    def on_hide_view(self) -> None:
        self.reset_flag = True
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
            self.video_buttons.center_on_screen()
            self.audio_buttons.center_on_screen()
            self.assets_buttons.center_on_screen()
            self.menu_exists = False

        self.ui.draw()

        # this finally centers the buttons properly. my god
        if not self.menu_center_flag:
            self.menu_buttons.center_on_screen()
            self.settings_buttons.center_on_screen()
            self.video_buttons.center_on_screen()
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
