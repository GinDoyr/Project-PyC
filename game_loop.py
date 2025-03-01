import arcade
import arcade.clock
import file_mngr.conf_mngr as conf
import player


class GameLoop(arcade.View):
    def __init__(self, window):
        super().__init__()
        self.player_sprite = conf.set_settings("Settings", "player_sprite")
        self.pl_bullet_sprite = conf.set_settings("Settings", "pl_bul_sprite")
        self.pl_bullet_audio = conf.set_settings("Settings", "pl_bul_audio")
        self.pl_bullet_audio_compl = arcade.load_sound(self.pl_bullet_audio)
        self.pl_bullet_speed = 5
        self.pl_bullet_recharge = 12
        self.player = player.Player(self.player_sprite, self.pl_bullet_sprite, self.pl_bullet_audio_compl, 0.5, 0.5)
        self.player.angle = -90
        self.player.center_x = window.center_x
        self.player.center_y = window.center_y
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.test_flag = False
        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(self.player)
        self.entities_list = arcade.SpriteList()
        self.shoot_flag = False
        self.recharge_flag = False
        self.clocker = arcade.clock.Clock()

    def update_player_speed(self):

        self.player.change_x = 0
        self.player.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player.change_y = 2
        elif self.down_pressed and not self.up_pressed:
            self.player.change_y = -2
        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -2
        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = 2

    def create_bullets(self):
        arcade.play_sound(self.player.bullet_audio)
        bullet = arcade.Sprite(self.player.bullet_sprite)
        bullet.change_y = self.pl_bullet_speed
        bullet.center_x = self.player.center_x
        bullet.bottom = self.player.top
        self.entities_list.append(bullet)

    def update_bullets(self):
        self.entities_list.update()
        for entity in self.entities_list:
            if entity.bottom > self.window.height or entity.top < 0 or entity.right < 0 or entity.left > self.window.width:
                entity.remove_from_sprite_lists()

    def on_draw(self):
        """
        Render the screen.
        """
        self.clear()

        if self.test_flag:
            self.sprite_list.draw()
            self.sprite_list.draw_hit_boxes()
            self.entities_list.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.sprite_list.update(delta_time)

        if not self.recharge_flag:
            self.clocker.tick(delta_time)
            if self.clocker.ticks_since(0) <= (60 // self.pl_bullet_recharge) * (
                    self.clocker.ticks // (60 // self.pl_bullet_recharge)):
                self.recharge_flag = True
                self.clocker.tick(0)

        if self.shoot_flag and self.recharge_flag:
            self.create_bullets()
            self.recharge_flag = False

        self.update_bullets()


    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        if key == arcade.key.L:
            self.test_flag = not self.test_flag

        if self.test_flag:
            if key == arcade.key.A:
                self.left_pressed = True
                self.update_player_speed()
            if key == arcade.key.D:
                self.right_pressed = True
                self.update_player_speed()
            if key == arcade.key.W:
                self.up_pressed = True
                self.update_player_speed()
            if key == arcade.key.S:
                self.down_pressed = True
                self.update_player_speed()
            if key == arcade.key.SPACE:
                self.shoot_flag = True

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        if self.test_flag:
            if key == arcade.key.A:
                self.left_pressed = False
                self.update_player_speed()
            if key == arcade.key.D:
                self.right_pressed = False
                self.update_player_speed()
            if key == arcade.key.W:
                self.up_pressed = False
                self.update_player_speed()
            if key == arcade.key.S:
                self.down_pressed = False
                self.update_player_speed()
            if key == arcade.key.SPACE:
                self.shoot_flag = False

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass
