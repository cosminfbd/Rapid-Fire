import pygame


class SoundManager:
    def __init__(self):
        self.normal_hit = pygame.mixer.Sound("sounds/hit_normal.wav")
        self.bonus_hit = pygame.mixer.Sound("sounds/hit_bonus.wav")
        self.special_hit = pygame.mixer.Sound("sounds/hit_special.wav")
        self.shield_hit = pygame.mixer.Sound("sounds/hit_shield.wav")
        self.explosion = pygame.mixer.Sound("sounds/explosion.wav")

        self.countdown = pygame.mixer.Sound("sounds/countdown.wav")
        self.game_over = pygame.mixer.Sound("sounds/game_over.wav")

        self.normal_hit.set_volume(0.35)
        self.bonus_hit.set_volume(0.40)
        self.special_hit.set_volume(0.45)
        self.shield_hit.set_volume(0.40)
        self.explosion.set_volume(0.18)

        self.countdown.set_volume(0.30)
        self.game_over.set_volume(0.40)

    def play_hit(self, points):
        if points == 1:
            self.normal_hit.play()
        elif points == 3 or points == 4:
            self.bonus_hit.play()
        elif points == 5:
            self.special_hit.play()
        elif points < 0:
            self.explosion.play()

    def play_shield_hit(self):
        self.shield_hit.play()

    def play_countdown(self):
        self.countdown.play()

    def play_game_over(self):
        self.game_over.play()