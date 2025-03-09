import arcade


class Player():
    def __init__(self, sprite, bullet_sprite, bullet_audio):
        self.sprite = sprite
        self.bullet_sprite = bullet_sprite
        self.bullet_audio = bullet_audio
