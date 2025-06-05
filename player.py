class Player:
    def __init__(self, sprite, bullet_sprite, bullet_audio):
        self.sprite = sprite
        self.bullet_sprite = bullet_sprite  # should probably move this to game_loop
        self.bullet_audio = bullet_audio
        self.wave_distance = 400
        self.wave_recharge = 60
        self.wave_speed = 8
        self.wave_recharged = True
        self.move_speed = 10
        self.lives = 3
        self.iframes = False
        self.iframes_len = 120  # ~2 seconds
        self.iframes_draw = True
        self.dash_dist = 150  # distance in pixels
        self.dash_recharged = True
        self.dash_rechtime = 90  # 1.5 seconds, might have a boost?
        self.parry_radius = 100
        self.parry_rechtime = 60
        self.parry_recharged = True
