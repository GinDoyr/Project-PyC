class Banzai:  # ... what even is the point of this file??? i mean yeah classes but they dont eat up that much space. maybe do some more stuff here, like loading the resources here instead of in game loop?
    def __init__(self, sprite, sound_charge, explosion_snd, death_sound):
        self.sprite = sprite
        self.sound_charge = sound_charge
        # self.explosion_spr = explosion_spr  # add later
        self.explosion_snd = explosion_snd
        self.death_sound = death_sound
        self.health = 8
        self.speed = 5
        self.rage_area = 200


class Shooter:
    def __init__(self, sprite, sound, death_sound):
        self.sprite = sprite
        self.sound = sound
        self.death_sound = death_sound
        self.health = 20


class Boss:
    def __init__(self, sprite, sound, death_sound):
        self.sound = sound
        self.death_sound = death_sound
        self.health = 100
