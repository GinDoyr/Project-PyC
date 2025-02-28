import arcade
from PIL import Image


class Player(arcade.Sprite):
    def __init__(self, sprite, bullet_sprite, bullet_audio, scale_x, scale_y):
        self.bullet_sprite = bullet_sprite
        self.bullet_audio = bullet_audio
        # self.points = [spriteidk what to write here bruuuh]
        super().__init__(sprite, scale=(scale_x, scale_y))
