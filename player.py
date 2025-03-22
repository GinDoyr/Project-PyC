import arcade


class Player():
    def __init__(self, sprite, bullet_sprite, bullet_audio):
        self.sprite = sprite
        self.bullet_sprite = bullet_sprite
        self.bullet_audio = bullet_audio
        self.lives = 3
        # maybe do the abilities here, not in the game loop? idk, laaaater
