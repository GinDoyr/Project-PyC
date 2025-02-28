import arcade


class Enemy(arcade.Sprite):
    def __init__(self, sprite, scale_x, scale_y):
        super().__init__(sprite, scale=(scale_x, scale_y))


class Banzai(Enemy):
    def __init__(self, sprite, scale_x, scale_y, sound, death_sound, health):
        self.sound = sound
        self.death_sound = death_sound
        self.health = health
        super().__init__(sprite, scale_x, scale_y)
