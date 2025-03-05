import arcade
from arcade.gui import (UIManager, UIBoxLayout, UIDropdown, UIFlatButton, UITextureButton)


class AssetSelector(arcade.View):
    def __init__(self, call, main_menu):
        super().__init__()

        # menu save
        self.main_menu = main_menu

        # call check
        if call == 'Sprites':
            dropdown_options = {'Player': ['Sprite', 'Bullet'], 'Enemies': ['Enemy1', 'Enemy2'],
                                'Other': ['Background', 'Walls', 'Lives']}
        elif call == 'Audio':
            dropdown_options = {'Player': ['Bullet', 'Dash', 'Death'], 'Enemies': ['Enemy1 rush', 'Enemy1 death', 'Enemy2 death'],
                                'Other': ['Main menu bg', 'Live lost', 'Live regained', 'Game bg']}
        else:
            print('INCORRECT CALL!')
            self.window.close()  # idk i'd rather just crash the game lol¯\_(ツ)_/¯
            exit()

        # gui ini
        self.ui = UIManager()
        self.anchor = self.ui.add(UIBoxLayout(vertical=False))
        self.dropdown1 = UIDropdown(
            default=list(dropdown_options.keys())[0], options=list(dropdown_options.keys()))
        self.dropdown2 = UIDropdown(
            default=dropdown_options.get('Player')[0], options=dropdown_options.get('Player'))
        self.anchor.add(self.dropdown1)
        self.anchor.add(self.dropdown2)
        child_width = 0
        for i in self.anchor.children:
            child_width += i.width
        wid = self.window.width
        self.anchor.move(wid*2//3+(wid//3 - child_width)//2, self.window.height*15//16)
        if self.anchor.left+child_width > wid:
            print('OUT THE WINDOW!! if this happened that means i was too lazy to make the rescalable window')

        self.anchor2 = self.ui.add(UIBoxLayout(vertical=False))
        self.save_button = self.anchor2.add(
            UIFlatButton(width=child_width//2, text='Save changes')
        )
        self.exit_button = self.anchor2.add(
            UIFlatButton(width=child_width//2, text='Back to main menu')
        )
        self.anchor2.move(wid*2//3+(wid//3 - child_width)//2, 10)

        # gui buttons calls
        @self.exit_button.event("on_click")
        def on_click(event):
            self.window.show_view(self.main_menu)

        @self.dropdown1.event("on_change")
        def on_change(event):
            # ik this is probably a very inefficient way to do this but idk how else to do it rn honestly
            self.anchor.remove(self.dropdown2)
            self.dropdown2 = UIDropdown(
                default=dropdown_options.get(self.dropdown1.value)[0], options=dropdown_options.get(self.dropdown1.value))
            self.anchor.add(self.dropdown2)

    def on_show_view(self):
        self.ui.enable()

    def on_hide_view(self):
        self.ui.disable()

    def on_draw(self):
        self.clear()
        arcade.draw_line(self.window.width*2//3, 0, self.window.width*2//3, self.window.height, arcade.color.WHEAT, 1)
        self.ui.draw()

    def on_update(self, delta_time):
        @self.dropdown2.event("on_change")
        def on_change(event):
            print(self.dropdown2.value)
        # do stuff here ok