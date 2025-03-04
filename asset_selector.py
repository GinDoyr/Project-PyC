# arcade.view class with selectable sprites/sounds and their previews
# the code below is just an example code to toy with

"""
Section Example 3:

This shows how sections work with a very small example

What's key here is to understand how sections can isolate code that otherwise
 goes packed together in the view.
Also, note that events are received on each section only based on the
 section configuration. This way you don't have to check every time if the mouse
 position is on top of some area.

Note:
 - Event dispatching (two sections will receive on_key_press and on_key_release)
 - Prevent dispatching to allow some events to stop propagating
 - Event draw, update and event delivering order based on section_manager
   sections list order
 - Section "enable" property to show or hide sections
 - Modal Sections: sections that draw last but capture all events and also stop
   other sections from updating.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sections_demo_3
"""
import arcade
import arcade.gui


class AssetSelector(arcade.View):
    def __init__(self):
        super().__init__()

        # good luck
        dropdown_options = ['Player', 'Enemies', 'Other']
        drop_opt_player = ['Sprite', 'Bullet']
        drop_opt_enemies = ['Enemy1', 'Enemy2']
        drop_opt_other = ['Background', 'Walls', 'Lives']

        self.ui = arcade.gui.UIManager()
        self.anchor = self.ui.add(arcade.gui.UIBoxLayout())
        self.dropdown1 = arcade.gui.UIDropdown(
            default=dropdown_options[0], options=dropdown_options)

        self.anchor.add(self.dropdown1)

        @self.dropdown1.event("on_change")
        def on_change(event):
            print(self.dropdown1.value)

    def on_show_view(self) -> None:
        self.ui.enable()

    def on_hide_view(self) -> None:
        self.ui.disable()

    def on_draw(self):
        self.clear()
        self.anchor.center_on_screen()
        self.ui.draw()

    def on_update(self, delta_time):
        pass # do stuff here ok

def main():
    window = arcade.Window(resizable=True)
    game = AssetSelector()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
