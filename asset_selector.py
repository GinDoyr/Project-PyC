import arcade
from arcade.gui import (UIManager, UIBoxLayout, UIDropdown, UIFlatButton, UITextureButton)
from arcade.gui.experimental import UIScrollArea
import file_mngr.conf_mngr as conf


class AssetSelector(arcade.View):
    def __init__(self, call, main_menu):
        super().__init__()

        # call check
        if call == 'Sprites':
            dropdown_options = {'Player': ['Sprite', 'Bullet', 'Crosshair'], 'Enemies': ['Enemy1', 'Enemy2'],
                                'Other': ['Background', 'Walls', 'Lives']}
        elif call == 'Audio':
            dropdown_options = {'Player': ['Bullet', 'Dash', 'Death'], 'Enemies': ['Enemy1 rush', 'Enemy1 death', 'Enemy2 death'],
                                'Other': ['Live lost', 'Live regained'], 'Music': ['Main menu', 'Game', 'Boss']}
        else:
            print('INCORRECT CALL!')
            self.window.close()  # idk i'd rather just crash the game lol¯\_(ツ)_/¯
            exit()
        for i in dropdown_options:
            for v in dropdown_options.get(i):
                if not conf.check_path(f'assets/{call.lower()}/{i.lower()}/{v.lower()}'):
                    conf.create_path(f'assets/{call.lower()}/{i.lower()}/{v.lower()}')
                    print(f'created assets/{call.lower()}/{i.lower()}/{v.lower()}')

        # sound
        self.__curr_audio = None
        self.__bg_music = arcade.load_sound("assets/audio/music/misc/14. The World Machine.mp3", streaming=True)

        # gui ini
        self.__ui = UIManager()

        # top buttons
        self.anchor = self.__ui.add(UIBoxLayout(vertical=False))
        self.__dropdown1 = UIDropdown(
            default=list(dropdown_options.keys())[0], options=list(dropdown_options.keys()))
        self.__dropdown2 = UIDropdown(
            default=dropdown_options.get('Player')[0], options=dropdown_options.get('Player'))
        self.anchor.add(self.__dropdown1)
        self.anchor.add(self.__dropdown2)
        child_width = 0
        for i in self.anchor.children:
            child_width += i.width
        wid = self.window.width
        self.anchor.move(wid*2//3+(wid//3 - child_width)//2, self.window.height*15//16)
        if self.anchor.left+child_width > wid:
            print('OUT THE WINDOW!! if this happened that means i was too lazy to make the rescalable window')

        # bottom buttons
        self.__anchor2 = self.__ui.add(UIBoxLayout(vertical=False))
        self.__save_button = self.__anchor2.add(
            UIFlatButton(width=child_width//2, text='Save changes')
        )
        self.__exit_button = self.__anchor2.add(
            UIFlatButton(width=child_width//2, text='Back to main menu')
        )
        self.__anchor2.move(wid*2//3+(wid//3 - child_width)//2, 10)

        # select box
        self.__vertical_list = UIBoxLayout(size_hint=(1, 0), space_between=1)
        for i in conf.return_contents(f'assets/{call.lower()}/{self.__dropdown1.value}/{self.__dropdown2.value}'):
            button = UIFlatButton(height=30, size_hint=(1, None), text=f"{i[:-4]}")
            self.__vertical_list.add(button)
            button.on_click = self.__selector_click
        self.__previous_option1 = ''
        self.__previous_option2 = ''

        # scroll area
        scale_y = (self.anchor.bottom-self.__exit_button.height-30)/self.window.height
        v_scroll_area = self.__ui.add(UIBoxLayout(x=wid*2//3, y=self.__exit_button.height + 20, vertical=False, size_hint=(1/3, scale_y)))
        scroll_layout = v_scroll_area.add(UIScrollArea(size_hint=(1, 1)))
        scroll_layout.with_border(color=arcade.uicolor.WHITE)
        scroll_layout.add(self.__vertical_list)
        scroll_layout.invert_scroll = True

        # gui buttons calls
        @self.__exit_button.event("on_click")
        def on_click(event):
            self.window.show_view(main_menu)

        @self.__dropdown1.event("on_change")
        def on_change(event):
            print('change1')
            # ik this is probably a very inefficient way to do this but idk how else to do it rn honestly
            if self.__previous_option1 != self.__dropdown1.value:
                self.anchor.remove(self.__dropdown2)
                self.__dropdown2 = UIDropdown(
                    default=dropdown_options.get(self.__dropdown1.value)[0], options=dropdown_options.get(self.__dropdown1.value))
                self.anchor.add(self.__dropdown2)
                self.__vertical_list.clear()
                for i in conf.return_contents(f'assets/{call.lower()}/{self.__dropdown1.value.lower()}/{self.__dropdown2.value.lower()}'):
                    button = UIFlatButton(height=30, size_hint=(1, None), text=f"{i[:-4]}")
                    self.__vertical_list.add(button)
                    button.on_click = self.__selector_click
                self.__previous_option1 = self.__dropdown1.value
                self.__previous_option2 = self.__dropdown2.value

        # misc
        self.__call = call

    def __selector_click(self, event):
        print(event.source.text)

    def on_show_view(self):
        self.__ui.enable()
        self.__curr_audio = self.__bg_music.play(volume=0.05)

    def on_hide_view(self):
        self.__ui.disable()
        arcade.stop_sound(self.__curr_audio)

    def on_draw(self):
        self.clear()
        arcade.draw_line(self.window.width*2//3, 0, self.window.width*2//3, self.window.height, arcade.color.WHITE, 1)
        self.__ui.draw()

    def on_update(self, delta_time):
        @self.__dropdown2.event("on_change")
        def on_change(event):
            print('change2')
            if self.__previous_option2 != self.__dropdown2.value:
                self.__vertical_list.clear()
                for i in conf.return_contents(
                        f'assets/{self.__call.lower()}/{self.__dropdown1.value.lower()}/{self.__dropdown2.value.lower()}'):
                    button = UIFlatButton(height=30, size_hint=(1, None), text=f"{i[:-4]}")
                    self.__vertical_list.add(button)
                    button.on_click = self.__selector_click
                self.__previous_option2 = self.__dropdown2.value