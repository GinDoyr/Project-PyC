import arcade
from PIL import Image


class Player(arcade.Sprite):
    def __init__(self, sprite, bullet_sprite, bullet_audio, scale_x, scale_y):
        self.bullet_sprite = bullet_sprite
        self.bullet_audio = bullet_audio
        super().__init__(sprite, scale=(scale_x, scale_y))
