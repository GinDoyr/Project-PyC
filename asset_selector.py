import arcade
from arcade.gui import (UIManager, UIBoxLayout, UIDropdown, UIFlatButton, UISlider, UILabel, UITextureButton)
from arcade.gui.experimental import UIScrollArea
from tkinter.filedialog import askopenfilename
import shutil
import file_mngr.conf_mngr as conf


dicts = {'Sprites': {'Player': ['Sprite', 'Bullet', 'Crosshair'],
                   'Enemies': ['Enemy1', 'Enemy1 explosion', 'Enemy2', 'Enemy2 fire', 'Enemy3',
                               'Enemy3 fire', 'Boss', 'Boss charge', 'Boss laser'],
                    'Other': ['Background', 'Walls', 'Lives']},
         'Audio': {'Player': ['Bullet', 'Dash', 'Death'],
                   'Enemies': ['Enemy1 rush', 'Enemy1 explosion', 'Enemy1 death', 'Enemy2 death',
                               'Enemy3 death', 'Boss charge', 'Boss fire', 'Boss death'],
                   'Other': ['Live lost', 'Live regained'],
                   'Music': ['Main menu', 'Game', 'Boss']}}


def return_assets_dicts():
    return dicts


class AssetSelector(arcade.View):
    def __init__(self, call, main_menu):
        super().__init__()

        # call check
        if call == 'Sprites':
            dropdown_options = dicts.get('Sprites')
        elif call == 'Audio':
            dropdown_options = dicts.get('Audio')
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
        self.__curr_audio = None # for some reason i decided to private all the stuff here, thought it might be better to do like this instead of leaving all in public?
        self.__bg_music = arcade.load_sound("assets/audio/music/misc/14. The World Machine.mp3", streaming=True)
        self.__pause_bg = False

        # gui ini
        self.__ui = UIManager()

        # top buttons
        self.__topright = self.__ui.add(UIBoxLayout(vertical=False))
        self.__dropdown1 = UIDropdown(default=list(dropdown_options.keys())[0], options=list(dropdown_options.keys()))
        self.__dropdown2 = UIDropdown(default=dropdown_options.get('Player')[0], options=dropdown_options.get('Player'))
        self.__topright.add(self.__dropdown1)
        self.__topright.add(self.__dropdown2)
        child_width = 0
        for i in self.__topright.children:
            child_width += i.width
        wid = self.window.width
        self.__topright.move(wid * 2 // 3 + (wid // 3 - child_width) // 2, self.window.height * 15 // 16) # this one's required to be like that cause how else would i know children width
        if self.__topright.left+child_width > wid:
            print('OUT THE WINDOW!! if this happened that means i was too lazy to make the rescalable window')

        # top left buttons
        self.__topleft = self.__ui.add(UIBoxLayout(x=10, y=self.window.height * 15//16, space_between=10, vertical=False))
        self.__sel_file = self.__topleft.add(UILabel(text='Selected: '))

        # bottom right buttons
        self.__botright = self.__ui.add(UIBoxLayout(x=wid * 2 // 3 + (wid // 3 - child_width) // 2, y=10, vertical=False))
        self.__save_button = self.__botright.add(UIFlatButton(width=child_width//2, text='Save changes'))
        self.__exit_button = self.__botright.add(UIFlatButton(width=child_width//2, text='Back to main menu'))

        # bottom left buttons
        self.__botleft = self.__ui.add(UIBoxLayout(y=10, vertical=False))
        self.__load = self.__botleft.add(UIFlatButton(width=child_width//2, text='Load new'))
        self.__remove = self.__botleft.add(UIFlatButton(width=child_width//2, text='Remove selected'))
        self.__bg_button = self.__botleft.add(UIFlatButton(width=child_width//2, text='Stop music'))
        self.__botleft.move(wid*2//3 - child_width*3//2 - 10)
        # dont forget the player for the music! also do the normal resizing and position

        # audio buttons and some ini
        if call == 'Audio':
            self.__player = None
            self.__cur_sound = None
            self.__pause_flag = False
            self.__volume = 0.5
            self.__audio_btns = self.__ui.add(UIBoxLayout(x=10, y=10, vertical=False))
            self.__ps_res_btn = self.__audio_btns.add(UIFlatButton(text='Waiting...'))
            self.__volume_btn = UIBoxLayout()
            self.__volume_text = self.__volume_btn.add(UILabel(text='Volume: 50%'))
            self.__volume_slider = self.__volume_btn.add(UISlider(value=50, width=100))
            self.__audio_btns.add(self.__volume_btn)
            self.__volume_len = self.__topleft.add(UILabel(text='Length: '))

            @self.__ps_res_btn.event('on_click')
            def on_click(event):
                if self.__player is not None:
                    if arcade.Sound.is_playing(self, self.__player):
                        print('pausing')
                        self.__pause_flag = True
                        self.__player.pause()
                        self.__ps_res_btn.text = 'Resume'
                    elif not arcade.Sound.is_playing(self, self.__player):
                        print('resuming')
                        if not self.__pause_flag:
                            print('restarting audio as it finished!')
                            self.__player = self.__cur_sound.play(volume=self.__volume)
                        else:
                            self.__player.play()
                            self.__pause_flag = False
                        self.__ps_res_btn.text = 'Pause'

            @self.__volume_slider.event('on_change')
            def on_change(event):
                self.__volume = round(self.__volume_slider.value) / 100
                if self.__player is not None:
                    self.__player.volume = self.__volume
                self.__volume_text.text = f'Volume: {int(self.__volume * 100)}%'

        # scale by y here, i dunno where to put it lol
        self.__scale_y = round(((self.__topright.bottom - self.__exit_button.height - 30) / self.window.height) * self.window.height) + self.__exit_button.height + 19

        # sprite list
        if call == 'Sprites':
            self.__sprite_list = arcade.SpriteList()
            self.__hb_flag = False
            spr_path = conf.set_settings('Sprites', 'player_sprite')
            self.__sprite = arcade.Sprite(spr_path)
            self.__sel_file.text = f"Selected: {spr_path[spr_path.rfind('/')+1:]}"
            self.__sprite.position = (self.window.width // 3, (self.__scale_y + self.__exit_button.height + 21) // 2)
            self.__sprite_list.append(self.__sprite)
            self.__spr_size = self.__sprite.size
            self.__spr_resolution = self.__topleft.add(UILabel(text=f'Resolution: {self.__spr_size}'))
            self.__zoom_txt = self.__topleft.add(UILabel(text='Zoom: '))
            self.__zoom_slider = self.__topleft.add(UISlider(value=50, width=100))

            @self.__zoom_slider.event("on_change")
            def on_change(event):
                print(round(self.__zoom_slider.value/100, 2) + 0.5)
                self.__sprite.size = (self.__spr_size[0]*(round(self.__zoom_slider.value/100, 2) + 0.5), self.__spr_size[1]*(round(self.__zoom_slider.value/100, 2) + 0.5))

        # select box
        self.__vertical_list = UIBoxLayout(size_hint=(1, 0), space_between=1)
        for i in conf.return_contents(f'assets/{call.lower()}/{self.__dropdown1.value}/{self.__dropdown2.value}'):
            button = UIFlatButton(height=30, size_hint=(1, None), text=f"{i}")
            self.__vertical_list.add(button)
            button.on_click = self.__selector_click

        # scroll area
        scale_y = (self.__topright.bottom - self.__exit_button.height - 30) / self.window.height
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
            # ik this is probably a very inefficient way to do this but idk how else to do it rn honestly
            if self.__previous_option1 != self.__dropdown1.value:
                self.__topright.remove(self.__dropdown2)
                self.__dropdown2 = UIDropdown(
                    default=dropdown_options.get(self.__dropdown1.value)[0], options=dropdown_options.get(self.__dropdown1.value))
                self.__topright.add(self.__dropdown2)
                self.__vertical_list.clear()
                for i in conf.return_contents(f'assets/{call.lower()}/{self.__dropdown1.value.lower()}/{self.__dropdown2.value.lower()}'):
                    button = UIFlatButton(height=30, size_hint=(1, None), text=f"{i}")
                    self.__vertical_list.add(button)
                    button.on_click = self.__selector_click
                self.__previous_option1 = self.__dropdown1.value
                self.__previous_option2 = self.__dropdown2.value

        @self.__bg_button.event("on_click")
        def on_click(event):
            if arcade.Sound.is_playing(self, player=self.__curr_audio):
                self.__curr_audio.pause()
                self.__pause_bg = True
                self.__bg_button.text = 'Resume music'
            else:
                self.__curr_audio.play()
                self.__pause_bg = False
                self.__bg_button.text = 'Pause music'

        @self.__load.event("on_click")
        def on_click(event):
            filename = askopenfilename()
            try:
                if not conf.check_path(f'assets/{call.lower()}/{self.__dropdown1.value}/{self.__dropdown2.value}/{filename[filename.rfind("/")+1:]}'):
                    if call == 'Audio' and filename.endswith(('.mp3', '.wav')):
                        shutil.copy(filename, f'assets/{call.lower()}/{self.__dropdown1.value}/{self.__dropdown2.value}')
                        print(f'loaded {filename}')
                        self.__vertical_list.clear()
                        for i in conf.return_contents(
                                f'assets/{self.__call.lower()}/{self.__dropdown1.value.lower()}/{self.__dropdown2.value.lower()}'):
                            button = UIFlatButton(height=30, size_hint=(1, None), text=f"{i}")
                            self.__vertical_list.add(button)
                            button.on_click = self.__selector_click

                    elif call == 'Sprites' and filename.endswith(('.jpg', '.png', '.gif', '.jpeg')):
                        shutil.copy(filename, f'assets/{call.lower()}/{self.__dropdown1.value}/{self.__dropdown2.value}')
                        print(f'loaded {filename}')
                        self.__vertical_list.clear()
                        for i in conf.return_contents(
                                f'assets/{self.__call.lower()}/{self.__dropdown1.value.lower()}/{self.__dropdown2.value.lower()}'):
                            button = UIFlatButton(height=30, size_hint=(1, None), text=f"{i}")
                            self.__vertical_list.add(button)
                            button.on_click = self.__selector_click
                    else:
                        print(f'incorrect file type! call: {call}; file: {filename}')
                else:
                    print(f"already loaded {filename} or closed the window")
            except Exception as e:
                print("ERROR! idk what honestly: ", e)

        # misc
        self.__call = call
        self.__previous_option1 = ''
        self.__previous_option2 = ''

    def __selector_click(self, event):

        if self.__call == 'Sprites':
            self.__sprite_list.clear()
            self.__sprite = arcade.Sprite(f'assets/sprites/{self.__dropdown1.value.lower()}/{self.__dropdown2.value.lower()}/{event.source.text}')
            self.__sprite.position = (self.window.width//3, (self.__scale_y+self.__exit_button.height+21)//2)
            self.__sel_file.text = f'Selected: {event.source.text}'
            self.__spr_size = self.__sprite.size
            self.__spr_resolution.text = f'Resolution: {self.__spr_size}'
            self.__zoom_slider.value = 50
            self.__sprite_list.append(self.__sprite)
        else:
            if self.__player is not None:
                arcade.stop_sound(self.__player)
            self.__cur_sound = arcade.load_sound(f'assets/audio/{self.__dropdown1.value.lower()}/{self.__dropdown2.value.lower()}/{event.source.text}', streaming=True)
            print(f'launching audio at {self.__volume} volume')
            self.__player = self.__cur_sound.play(volume=self.__volume)
            self.__sel_file.text = f'Selected: {event.source.text}'
            sound_len = self.__cur_sound.get_length()
            ms = round((sound_len-int(sound_len))*100)
            seconds = int(sound_len//1)
            minutes = seconds//60
            seconds -= minutes*60
            if ms < 10:
                ms = '0'+str(ms)
            if seconds < 10:
                seconds = '0'+str(seconds)
            if minutes < 10:
                minutes = '0'+str(minutes)
            ms, seconds, minutes = str(ms), str(seconds), str(minutes)
            self.__volume_len.text = f'Length (mm:ss:ms): {minutes}:{seconds}:{ms}'
            self.__ps_res_btn.text = 'Pause'

    def on_show_view(self):
        self.__ui.enable()
        self.__curr_audio = self.__bg_music.play(volume=0.05)  # loop the music! ed: just c

    def on_hide_view(self):
        self.__ui.disable()
        if self.__call == 'Audio':
            if self.__player is not None:
                arcade.stop_sound(self.__player)
                self.__player = None
        arcade.stop_sound(self.__curr_audio)
        self.__curr_audio = None  # just to be safe

    def on_draw(self):
        self.clear()
        arcade.draw_line(self.window.width*2//3, 0, self.window.width*2//3, self.window.height, arcade.color.WHITE, 1)
        arcade.draw_line(0, self.__exit_button.height+21, self.window.width*2//3, self.__exit_button.height+21, arcade.color.WHITE, 1)
        arcade.draw_line(0, self.__scale_y+1, self.window.width * 2 // 3, self.__scale_y+1, arcade.color.WHITE, 1)
        if self.__call == 'Sprites':
            self.__sprite_list.draw()
            if self.__hb_flag:
                self.__sprite_list.draw_hit_boxes(color=arcade.color.RED)
        self.__ui.draw()

    def on_update(self, delta_time):
        @self.__dropdown2.event("on_change")
        def on_change(event):
            if self.__previous_option2 != self.__dropdown2.value:
                self.__vertical_list.clear()
                for i in conf.return_contents(f'assets/{self.__call.lower()}/{self.__dropdown1.value.lower()}/{self.__dropdown2.value.lower()}'):
                    button = UIFlatButton(height=30, size_hint=(1, None), text=f"{i}")
                    self.__vertical_list.add(button)
                    button.on_click = self.__selector_click
                self.__previous_option2 = self.__dropdown2.value

        if self.__call == 'Audio':
            if self.__player is not None:
                if not self.__cur_sound.is_playing(self.__player) and not self.__pause_flag:
                    self.__ps_res_btn.text = 'Resume'

        if not self.__bg_music.is_playing(self.__curr_audio) and not self.__pause_bg:
            self.__curr_audio = self.__bg_music.play(volume=0.05)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.H:
            self.__hb_flag = not self.__hb_flag