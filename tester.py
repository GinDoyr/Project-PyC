import arcade
from arcade.gui import UIAnchorLayout, UIBoxLayout, UIFlatButton, UIView
from arcade.gui.experimental import UIScrollArea
from arcade.gui.experimental.scroll_area import UIScrollBar
# import psutil
import file_mngr.conf_mngr as conf

window = arcade.Window(title="GUIScrollLayout")


class MyView(UIView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.uicolor.BLUE_BELIZE_HOLE

        # create a layout with two columns
        root = self.add_widget(UIAnchorLayout())
        content_left = UIAnchorLayout(size_hint=(0.5, 1), x=window.center_x, y=window.center_y)
        root.add(content_left, anchor_x="left", anchor_y="center")
        self.player1 = None
        self.player2 = None

        # create the list, which should be scrolled vertically
        self.vertical_list = UIBoxLayout(size_hint=(1, 0), space_between=1)
        for i in conf.return_contents('assets/music'):
            button = UIFlatButton(height=30, size_hint=(1, None), text=f"{i[:-4]}")
            self.vertical_list.add(button)
            button.on_click = self.selector_click

        # the scroll area and the scrollbar are added to a box layout
        # so they are next to each other, this also reduces complexity for the layout
        # implementation
        v_scroll_area = UIBoxLayout(vertical=False, size_hint=(0.8, 0.8))
        content_left.add(v_scroll_area, anchor_x="center", anchor_y="center")

        scroll_layout = v_scroll_area.add(UIScrollArea(size_hint=(1, 1)))
        scroll_layout.with_border(color=arcade.uicolor.WHITE_CLOUDS)
        scroll_layout.add(self.vertical_list)
        v_scroll_area.add(UIScrollBar(scroll_layout))

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()
            return True
        return False

    def selector_click(self, event):
        print("click!")
        print(event.source.text)

    def on_update(self, delta_time):
        # print(psutil.cpu_percent()) # just a small cpu/memory usage check test with sounds, dont forget to uncomment import psutil
        # print(psutil.virtual_memory().percent)
        # player1 = arcade.Sound
        # player2 = arcade.Sound
        # if psutil.cpu_percent() > 90:
        #     if player1 is arcade.Sound:
        #         player1 = arcade.sound.play_sound(arcade.load_sound("assets/sounds/hl/siren.wav"))
        # if psutil.virtual_memory().percent > 76:
        #     if player2 is arcade.Sound:
        #         player2 = arcade.sound.play_sound(arcade.load_sound("assets/sounds/hl/bigwarning.wav"))
        # if player1 is not arcade.Sound:
        #     if arcade.Sound.is_playing(player1):
        #         pass
        #     if arcade.Sound.is_complete(player1):
        #         player1 = arcade.Sound
        # if player2 is not arcade.Sound:
        #     if arcade.Sound.is_playing(player2):
        #         pass
        #     if arcade.Sound.is_complete(player2):
        #         player2 = arcade.Sound
        pass


def main():
    window.show_view(MyView())
    window.run()


if __name__ == "__main__":
    main()
