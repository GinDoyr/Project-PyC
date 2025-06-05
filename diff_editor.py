import arcade
from arcade.gui import (UIManager, UIBoxLayout, UIFlatButton, UIInputText)
from arcade.gui.experimental import UIScrollArea
import file_mngr.conf_mngr as conf
import difficulties.diftest as diff

"""
ok so uuh lil message: at around ~15 enemy spawn waves the editor starts lagging. probable cause is the UIScrollArea,
im not going to try and optimize this as of now, see no need for it, and i really wouldn't even know where to start from
so to anyone wanting to optimize that - good luck mateys
"""

own_style = {
        "normal": arcade.gui.UIFlatButton.UIStyle(),
        "hover": arcade.gui.UIFlatButton.UIStyle(
            font_color=arcade.color.WHITE,
            bg=arcade.color.DARK_BLUE,
            border=arcade.color.GRAY,
        ),
        "press": arcade.gui.UIFlatButton.UIStyle(
            font_color=arcade.color.DARK_BLUE,
            bg=arcade.color.WHITE,
            border=arcade.color.GRAY,
        ),
        "disabled": arcade.gui.UIFlatButton.UIStyle(font_color=arcade.color.WHITE, bg=arcade.color.BLACK)
    }


class DiffEditor(arcade.View):
    def __init__(self, main_menu):
        super().__init__()
        conf.logmn.log_info('launching difficulty editor')

        # sound
        self.curr_audio = None
        self.bg_music = arcade.load_sound("assets/audio/music/misc/14. The World Machine.mp3", streaming=True)
        self.pause_bg = False

        self.ui = UIManager()

        self.diff_images = [arcade.Sprite('difficulties/easy.png', 2),
                            arcade.Sprite('difficulties/medium.png', 2),
                            arcade.Sprite('difficulties/doom.png', 2),
                            arcade.Sprite('difficulties/custom.png', 2)]
        self.diff_sprlist = arcade.SpriteList()
        self.diff_selected = 0
        self.diff_nums = {0: 'easy', 1: 'medium', 2: 'doom', 3: 'custom'}
        self.curr_image = self.diff_images[self.diff_selected]
        self.diff_sprlist.append(self.curr_image)
        self.curr_image.position = self.window.center_x//2, self.window.center_y

        self.botleft = self.ui.add(UIBoxLayout(x=self.curr_image.center_x - 105, y=10, vertical=False, space_between=10))
        self.prev = self.botleft.add(UIFlatButton(width=100, text='Previous'))
        self.next = self.botleft.add(UIFlatButton(width=100, text='Next'))

        self.botright = self.ui.add(UIBoxLayout(x=self.window.width*3//4-260, y=10, vertical=False, space_between=10))
        self.save = self.botright.add(UIFlatButton(width=100, text='Save to selected', multiline=True))
        self.remove = self.botright.add(UIFlatButton(width=100, text='Toggle remove mode', multiline=True))
        self.add = self.botright.add(UIFlatButton(width=100, text='Add new', multiline=True))
        self.reset = self.botright.add(UIFlatButton(width=100, text='Set to default', multiline=True))
        self.back = self.botright.add(UIFlatButton(width=100, text='Back to main menu', multiline=True))

        self.currwidth = self.window.width//8
        self.topright = self.ui.add(UIBoxLayout(x=self.window.width//2, y=self.window.height-50, vertical=False))
        self.id_label = self.topright.add(UIFlatButton(width=self.currwidth, text='ID'))
        self.banz_label = self.topright.add(UIFlatButton(width=self.currwidth, text='Banzai'))
        self.stshoot_label = self.topright.add(UIFlatButton(width=self.currwidth, text='Static shooter', multiline=True))
        self.dynshoot_label = self.topright.add(UIFlatButton(width=self.currwidth, text='Dynamic shooter', multiline=True))
        for i in self.topright.children:
            i.disabled = True
            i.style = own_style

        self.lines = []
        for i in range(4):
            self.lines.append([self.window.center_x+self.currwidth*i, 70])
            self.lines.append([self.window.center_x + self.currwidth * i, self.window.height])
        self.lines.append([0, self.topright.position[1]])
        self.lines.append([self.window.width, self.topright.position[1]])
        self.lines.append([0, 70])
        self.lines.append([self.window.width, 70])

        self.vertical_list = UIBoxLayout()
        self.last_id = 0
        en_list = diff.read_and_return_enemies(self.diff_nums.get(self.diff_selected), True)
        for i in en_list:
            row = UIBoxLayout(vertical=False)
            id = UIFlatButton(width=self.currwidth, text=f"{self.last_id}", style=own_style)
            self.last_id += 1
            row.add(id)
            id.disabled = True
            id.on_click = self.en_remover
            banz = UIInputText(width=self.currwidth, height=id.height, text=f"{i[0]}")
            row.add(banz)
            stshoot = UIInputText(width=self.currwidth, height=id.height, text=f"{i[1]}")
            row.add(stshoot)
            dynshoot = UIInputText(width=self.currwidth, height=id.height, text=f"{i[2]}")
            row.add(dynshoot)
            banz.on_change = self.en_changer
            stshoot.on_change = self.en_changer
            dynshoot.on_change = self.en_changer
            self.vertical_list.add(row)

        # scroll area
        v_scroll_area = self.ui.add(
            UIBoxLayout(x=self.window.width//2, y=70, width=self.currwidth*4))
        scroll_layout = v_scroll_area.add(UIScrollArea(width=self.currwidth*4, height=600))
        scroll_layout.add(self.vertical_list)
        scroll_layout.invert_scroll = True

        self.remove_mode = False

        # gui buttons calls
        @self.back.event("on_click")
        def on_click(event):
            self.window.show_view(main_menu)
            conf.logmn.log_info('closing difficulty editor')

        @self.add.event("on_click")
        def on_click(event):
            row = UIBoxLayout(vertical=False)
            id = UIFlatButton(width=self.currwidth, text=f"{self.last_id}", style=own_style)
            self.last_id += 1
            row.add(id)
            id.disabled = True
            id.on_click = self.en_remover
            banz = UIInputText(width=self.currwidth, height=id.height, text="0")
            row.add(banz)
            stshoot = UIInputText(width=self.currwidth, height=id.height, text="0")
            row.add(stshoot)
            dynshoot = UIInputText(width=self.currwidth, height=id.height, text="0")
            row.add(dynshoot)
            banz.on_change = self.en_changer
            stshoot.on_change = self.en_changer
            dynshoot.on_change = self.en_changer
            self.vertical_list.add(row)

        @self.remove.event("on_click")
        def on_click(event):
            self.remove_mode = not self.remove_mode
            if self.remove_mode:
                for child in self.vertical_list.children:
                    child.children[0].disabled = False

            else:
                for child in self.vertical_list.children:
                    child.children[0].disabled = True

        @self.reset.event("on_click")
        def on_click(event):
            conf.logmn.log_info(f'setting difficulty {self.diff_selected} to default...')
            en_list = diff.get_default(self.diff_selected)
            self.vertical_list.clear()
            self.last_id = 0
            for i in en_list:
                row = UIBoxLayout(vertical=False)
                id = UIFlatButton(width=self.currwidth, text=f"{self.last_id}", style=own_style)
                self.last_id += 1
                row.add(id)
                id.disabled = True
                id.on_click = self.en_remover
                banz = UIInputText(width=self.currwidth, height=id.height, text=f"{i[0]}")
                row.add(banz)
                stshoot = UIInputText(width=self.currwidth, height=id.height, text=f"{i[1]}")
                row.add(stshoot)
                dynshoot = UIInputText(width=self.currwidth, height=id.height, text=f"{i[2]}")
                row.add(dynshoot)
                banz.on_change = self.en_changer
                stshoot.on_change = self.en_changer
                dynshoot.on_change = self.en_changer
                self.vertical_list.add(row)

        @self.save.event("on_click")
        def on_click(event):
            savelist = [self.diff_selected]
            for child in self.vertical_list.children:
                row = []
                for child2 in child.children[1:]:
                    row.append(int(child2.text))
                savelist.append(row)
            conf.logmn.log_info(f'attempting to save enemy list {savelist}')
            diff.encode_difficulties(savelist)
            conf.logmn.log_info('enemy list saved!')

    def en_changer(self, event):
        old = event.old_value
        new = event.new_value
        if new == '':
            event.source.text = '0'
        elif not new.isdigit():
            event.source.text = old
        else:
            new = str(int(new))  # to make SURE it doesnt start with 0
            event.source.text = new

    def en_remover(self, event):
        for child in self.vertical_list.children:
            if child.children[0].text == event.source.text:
                self.vertical_list.remove(child)
                break
        self.last_id = 0
        for child in self.vertical_list.children:
            child.children[0].text = f"{self.last_id}"
            self.last_id += 1

    def on_show_view(self):
        self.ui.enable()
        self.curr_audio = self.bg_music.play(volume=0.05)

    def on_hide_view(self):
        self.ui.disable()
        arcade.stop_sound(self.curr_audio)
        self.curr_audio = None  # just to be safe

    def on_draw(self):
        self.clear()
        self.diff_sprlist.draw()
        self.ui.draw()
        arcade.draw_lines(self.lines, arcade.color.WHITE, 2)

    def on_update(self, delta_time):
        @self.next.event("on_click")
        def on_click(event):
            if self.diff_selected == len(self.diff_images) - 1:
                self.diff_selected = 0
            else:
                self.diff_selected += 1
            self.diff_sprlist.clear()
            self.curr_image = self.diff_images[self.diff_selected]
            self.curr_image.position = self.window.center_x // 2, self.window.center_y
            self.diff_sprlist.append(self.curr_image)
            self.last_id = 0
            self.vertical_list.clear()
            en_list = diff.read_and_return_enemies(self.diff_nums.get(self.diff_selected), True)
            for i in en_list:
                row = UIBoxLayout(vertical=False)
                id = UIFlatButton(width=self.currwidth, text=f"{self.last_id}", style=own_style)
                self.last_id += 1
                row.add(id)
                id.disabled = True
                id.on_click = self.en_remover
                banz = UIInputText(width=self.currwidth, height=id.height, text=f"{i[0]}")
                row.add(banz)
                stshoot = UIInputText(width=self.currwidth, height=id.height, text=f"{i[1]}")
                row.add(stshoot)
                dynshoot = UIInputText(width=self.currwidth, height=id.height, text=f"{i[2]}")
                row.add(dynshoot)
                banz.on_change = self.en_changer
                stshoot.on_change = self.en_changer
                dynshoot.on_change = self.en_changer
                self.vertical_list.add(row)
            self.remove_mode = False

        @self.prev.event("on_click")
        def on_click(event):
            if self.diff_selected == 0:
                self.diff_selected = len(self.diff_images) - 1
            else:
                self.diff_selected -= 1
            self.diff_sprlist.clear()
            self.curr_image = self.diff_images[self.diff_selected]
            self.curr_image.position = self.window.center_x // 2, self.window.center_y
            self.diff_sprlist.append(self.curr_image)
            self.last_id = 0
            self.vertical_list.clear()
            en_list = diff.read_and_return_enemies(self.diff_nums.get(self.diff_selected), True)
            for i in en_list:
                row = UIBoxLayout(vertical=False)
                id = UIFlatButton(width=self.currwidth, text=f"{self.last_id}", style=own_style)
                self.last_id += 1
                row.add(id)
                id.disabled = True
                id.on_click = self.en_remover
                banz = UIInputText(width=self.currwidth, height=id.height, text=f"{i[0]}")
                row.add(banz)
                stshoot = UIInputText(width=self.currwidth, height=id.height, text=f"{i[1]}")
                row.add(stshoot)
                dynshoot = UIInputText(width=self.currwidth, height=id.height, text=f"{i[2]}")
                row.add(dynshoot)
                banz.on_change = self.en_changer
                stshoot.on_change = self.en_changer
                dynshoot.on_change = self.en_changer
                self.vertical_list.add(row)
            self.remove_mode = False
