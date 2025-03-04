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
from arcade import Section, SectionManager
from arcade.types import Color
import arcade.gui

INFO_BAR_HEIGHT = 40
PANEL_WIDTH = 200
SPRITE_SPEED = 1

COLOR_LIGHT = Color.from_hex_string("#D9BBA0")
COLOR_DARK = Color.from_hex_string("#0D0D0D")
COLOR_1 = Color.from_hex_string("#2A1459")
COLOR_2 = Color.from_hex_string("#4B89BF")
COLOR_3 = Color.from_hex_string("#03A688")


class InfoBar(Section):
    """This is the top bar of the screen where info is showed"""

    def on_draw(self):
        # draw game info
        arcade.draw_lrbt_rectangle_filled(self.left, self.right, self.bottom, self.top, COLOR_DARK)
        arcade.draw_lrbt_rectangle_outline(
            self.left, self.right, self.bottom, self.top, COLOR_LIGHT
        )
        arcade.draw_text(
            "Hello",
            self.left + 20,
            self.top - self.height / 1.6,
            COLOR_LIGHT,
        )

        arcade.draw_text(
            "Hello 2",
            self.left + 220,
            self.top - self.height / 1.6,
            COLOR_LIGHT,
        )
        arcade.draw_text(
            "Hello three (there)",
            self.left + 480,
            self.top - self.height / 1.6,
            COLOR_LIGHT,
        )

    def on_resize(self, width: int, height: int):
        # stick to the top
        self.width = width
        self.bottom = height - self.view.info_bar.height


class Panel(Section):
    """This is the Panel to the right where buttons and info is showed"""

    def __init__(self, left: int, bottom: int, width: int, height: int, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        # create buttons
        self.button_stop = self.new_button(arcade.color.ARSENIC)
        self.button_toggle_info_bar = self.new_button(COLOR_1)

        self.button_show_modal = self.new_button(COLOR_2)
        # to show the key that's actually pressed
        self.pressed_key: int | None = None

    @staticmethod
    def new_button(color):
        # helper to create new buttons
        return arcade.SpriteSolidColor(100, 50, color=color)

    def draw_button_stop(self):
        arcade.draw_text(
            "Press button to stop the ball", self.left + 10, self.top - 40, COLOR_LIGHT, 10
        )
        arcade.draw_sprite(self.button_stop)

    def draw_button_toggle_info_bar(self):
        arcade.draw_text(
            "Press to toggle info_bar", self.left + 10, self.top - 140, COLOR_LIGHT, 10
        )
        arcade.draw_sprite(self.button_toggle_info_bar)

    def on_draw(self):
        arcade.draw_lrbt_rectangle_filled(self.left, self.right, self.bottom, self.top, COLOR_DARK)
        arcade.draw_lrbt_rectangle_outline(
            self.left, self.right, self.bottom, self.top, COLOR_LIGHT
        )
        self.draw_button_stop()
        self.draw_button_toggle_info_bar()

        if self.pressed_key:
            arcade.draw_text(
                f"Pressed key code: {self.pressed_key}",
                self.left + 10,
                self.top - 240,
                COLOR_LIGHT,
                9,
            )

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.button_stop.collides_with_point((x, y)):
            print('stop :)')
        elif self.button_toggle_info_bar.collides_with_point((x, y)):
            self.view.info_bar.enabled = not self.view.info_bar.enabled

    def on_resize(self, width: int, height: int):
        # stick to the right
        self.left = width - self.width
        self.height = height - self.view.info_bar.height
        self.button_stop.position = self.left + self.width / 2, self.top - 80

        pos = self.left + self.width / 2, self.top - 180
        self.button_toggle_info_bar.position = pos

    def on_key_press(self, symbol: int, modifiers: int):
        self.pressed_key = symbol

    def on_key_release(self, _symbol: int, _modifiers: int):
        self.pressed_key = None


class Map(Section):
    """This represents the place where the game takes place"""

    def __init__(self, left: int, bottom: int, width: int, height: int, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.sprite_list = arcade.SpriteList()
        self.pressed_key: int | None = None

    def on_update(self, delta_time):
        self.sprite_list.update()

    def on_draw(self):
        arcade.draw_lrbt_rectangle_filled(self.left, self.right, self.bottom, self.top, COLOR_DARK)
        arcade.draw_lrbt_rectangle_outline(
            self.left, self.right, self.bottom, self.top, COLOR_LIGHT
        )
        self.sprite_list.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        self.pressed_key = symbol

    def on_key_release(self, _symbol: int, _modifiers: int):
        self.pressed_key = None

    def on_resize(self, width: int, height: int):
        self.width = width - self.view.panel.width
        self.height = height - self.view.info_bar.height


class AssetSelector(arcade.View):
    def __init__(self):
        super().__init__()

        # we set accept_keyboard_events to False (default to True)
        self.info_bar = InfoBar(
            0,
            self.window.height - INFO_BAR_HEIGHT,
            self.window.width,
            INFO_BAR_HEIGHT,
            accept_keyboard_keys=False,
        )

        # as prevent_dispatch is on by default, we let pass the events to the
        # following Section: the map
        self.panel = Panel(
            self.window.width - PANEL_WIDTH,
            0,
            PANEL_WIDTH,
            self.window.height - INFO_BAR_HEIGHT,
            prevent_dispatch={False},
        )
        self.map = Map(0, 0, self.window.width - PANEL_WIDTH, self.window.height - INFO_BAR_HEIGHT)

        # add the sections
        self.section_manager = SectionManager(self)
        self.section_manager.add_section(self.info_bar)
        self.section_manager.add_section(self.panel)
        self.section_manager.add_section(self.map)

    def on_show_view(self) -> None:
        self.section_manager.enable()

    def on_hide_view(self) -> None:
        self.section_manager.disable()

    def on_draw(self):
        self.clear()


def main():
    window = arcade.Window(resizable=True)
    game = AssetSelector()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
