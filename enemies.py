class Banzai:  # ... what even is the point of this file??? i mean yeah classes but they dont eat up that much space. maybe do some more stuff here, like loading the resources here instead of in game loop?
    def __init__(self, sprite, flash, sound_charge, explosion_snd, death_sound):
        self.sprite = sprite
        self.flash = flash
        self.sound_charge = sound_charge
        self.explosion_snd = explosion_snd
        self.death_sound = death_sound
        self.health = 8
        self.speed = 4
        self.rage_aud_area = 600
        self.rage_area = 150
        self.explosion_radius = 60


class StaticShooter:
    def __init__(self, sprite, fire1, fire2, fire1snd, fire2snd, deathspr, death_sound):
        self.sprite = sprite
        self.fire1 = fire1
        self.fire2 = fire2
        self.fire1snd = fire1snd
        self.fire2snd = fire2snd
        self.deathspr = deathspr
        self.death_sound = death_sound
        self.health = 20
        self.fire_sound_area = 700
        self.shoot_area = 1000


class Boss:
    def __init__(self, sprite):
        self.sprite = sprite
        self.health = 100
        self.move_speed = 20
        self.move_change_tick = 60
        self.orig_health = self.health # for use in bossbar
        self.shielded = False
        self.attack_recharged = False
        self.attacking = False
        self.lasering = False
        self.st_attack_tick = 0
        self.tick_set = False
        self.shield_rchg = 540
        self.shield_time = 270
        self.lsr_charge_time = 240
        self.lsr_shoot_time = 180
        self.lsr_last_x = 0
        self.lsr_last_y = 0
        self.recharge_time = 120


