import pygame
import random
import math



class Level:
    def __init__(self, id, time_limit, required_score, max_speed, spawn_interval, target_weights, max_targets):
        self.id             = id
        self.start_time     = None
        self.time_limit     = time_limit
        self.required_score = required_score
        self.max_speed      = max_speed
        self.spawn_interval = spawn_interval
        self.target_weights = target_weights # (normal, bonus, special, shielded, bomb)
        self.max_targets    = max_targets

    def start(self):
        self.start_time = pygame.time.get_ticks()

    def time_left(self):
        elapsed_ms = pygame.time.get_ticks() - self.start_time
        elapsed_seconds = elapsed_ms // 1000
        return max(0, self.time_limit - elapsed_seconds)
    
    def progress(self): # value in [0, 1]
        elapsed_ms = pygame.time.get_ticks() - self.start_time
        total_ms = self.time_limit * 1000
        return min(1, elapsed_ms / total_ms)



class Target:
    def __init__(self, rect, speed, points, color, lifetime_ms):
        self.rect = rect
        self.speed = speed
        self.points = points
        self.color = color
        self.lifetime_ms = lifetime_ms

        self.created_time = pygame.time.get_ticks()
        self.entered_time = None
        self.has_entered = False
        self.entry_timeout_ms = 2500

        self.destroy_time = None
        self.destroy_start_scale = 1.0
        self.spawn_animation_ms = 150
        self.destroy_animation_ms = 180

    def move(self):
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]

    def hit(self):
        return True
    
    def get_draw_scale(self):
        current_time = pygame.time.get_ticks()

        # disappearing animation
        if self.is_destroying():
            elapsed = current_time - self.destroy_time
            progress = min(1, elapsed / self.destroy_animation_ms)
            return max(.2, self.destroy_start_scale * (1 - .8 * progress))
        
        # no animation if it does not appear on screen
        if self.entered_time is None:
            return 1.0
        
        # entering animation
        elapsed = current_time - self.entered_time
        progress = min(1, elapsed / self.spawn_animation_ms)

        # ease-out
        eased_progress = 1 - (1 - progress) ** 3

        return .85 + .15 * eased_progress

    def start_destroying(self):
        if self.destroy_time is None:
            self.destroy_start_scale = self.get_draw_scale()
            self.destroy_time = pygame.time.get_ticks()

    def is_destroying(self):
        return self.destroy_time is not None
    
    def destroy_animation_finished(self):
        if not self.is_destroying():
            return False
        elapsed = pygame.time.get_ticks() - self.destroy_time
        return elapsed >= self.destroy_animation_ms

    def is_expired(self):
        current_time = pygame.time.get_ticks()
        if self.entered_time is None: # target did not appear on the screen
            return current_time - self.created_time >= self.entry_timeout_ms
        return current_time - self.entered_time >= self.lifetime_ms
    
    def mark_as_entered(self):
        if not self.has_entered:
            self.has_entered = True
            self.entered_time = pygame.time.get_ticks()

    def draw_bullseye(self, surface, outer_color, ring_color, center_color, bullseye_color):
        center = self.rect.center
        radius = self.rect.width // 2

        pygame.draw.circle(surface, (20, 20, 25), center, radius)
        pygame.draw.circle(surface, outer_color, center, radius - 2)
        pygame.draw.circle(surface, ring_color, center, int(radius * 0.76))
        pygame.draw.circle(surface, outer_color, center, int(radius * 0.56))
        pygame.draw.circle(surface, ring_color, center, int(radius * 0.36))
        pygame.draw.circle(surface, center_color, center, int(radius * 0.20))
        pygame.draw.circle(surface, bullseye_color, center, max(3, int(radius * 0.09)))

        pygame.draw.circle(surface, (255, 255, 255), (center[0] - radius // 4, center[1] - radius // 4), max(2, radius // 12))


class NormalTarget(Target):
    SIZE = 80

    def __init__(self, rect, speed):
        super().__init__(rect, speed, 1, "green", 3000)

    def draw(self, surface):
        self.draw_bullseye(surface, (35, 150, 80), (235, 245, 238), (45, 185, 95), (225, 55, 65))


class BonusTarget(Target):
    SIZE = 60

    def __init__(self, rect, speed):
        super().__init__(rect, speed, 3, "yellow", 1000)

    def draw(self, surface):
        self.draw_bullseye(surface, (245, 185, 25), (30, 30, 35), (255, 225, 80), (255, 245, 220))


class SpecialTarget(Target):
    SIZE = 45

    def __init__(self, rect, speed):
        super().__init__(rect, speed, 5, "red", 600)

    def draw(self, surface):
        self.draw_bullseye(surface, (205, 45, 55), (245, 245, 245), (160, 25, 35), (20, 20, 25))

        center = self.rect.center
        radius = self.rect.width // 2
        line_size = int(radius * 0.62)

        # target crosshair
        pygame.draw.line(surface, (255, 255, 255), (center[0] - line_size, center[1]), (center[0] + line_size, center[1]), 1)
        pygame.draw.line(surface, (255, 255, 255), (center[0], center[1] - line_size), (center[0], center[1] + line_size), 1)


class ShieldedTarget(Target):
    SIZE = 84

    def __init__(self, rect, speed):
        super().__init__(rect, speed, 4, "turquoise", 3000)
        self.shield_active = True

    def hit(self):
        if self.shield_active == True:
            self.shield_active = False
            return False
        return True
    
    def draw_shield(self, surface):
        size = self.rect.width
        center = (size // 2, size // 2)
        radius = size // 2

        shield_surface = pygame.Surface((size, size), pygame.SRCALPHA) # transparent
        pygame.draw.circle(shield_surface, (35, 225, 215, 95), center, radius - 3)

        surface.blit(shield_surface, self.rect.topleft)

    def draw(self, surface):
        self.draw_bullseye(surface, (85, 65, 145), (235, 240, 255), (125, 100, 195), (255, 165, 45))
        if self.shield_active == True:
            self.draw_shield(surface)


class Bomb(Target):
    SIZE = 70
    
    def __init__(self, rect, speed):
        super().__init__(rect, speed, -2, (235, 85, 185), 1800)

    def draw(self, surface):
        self.draw_bullseye(surface, (105, 35, 115), (245, 220, 250), (165, 55, 170), (45, 15, 55))

        center = self.rect.center
        radius = self.rect.width // 2
        line_size = int(radius * 0.45)

        pygame.draw.line(surface, (255, 225, 250), (center[0] - line_size, center[1] - line_size), (center[0] + line_size, center[1] + line_size), 4)
        pygame.draw.line(surface, (255, 225, 250), (center[0] + line_size, center[1] - line_size), (center[0] - line_size, center[1] + line_size), 4)



class ScorePopup:
    def __init__(self, position, points, color):
        self.position = pygame.Vector2(position)
        self.text = f"+{points}" if points > 0 else str(points)
        self.color = color
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime_ms = 700

    def update(self):
        self.position.y -= 0.7

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time >= self.lifetime_ms



def create_target_from_edge(game_panel, min_speed, max_speed, target_class):
    side = random.choice(["left", "right", "top"])
    target_size = target_class.SIZE
    sideways_speed = max(1, max_speed // 2)

    if side == "left":
        rect = pygame.Rect(game_panel.left - target_size, random.randint(game_panel.top, game_panel.bottom - target_size), target_size, target_size)
        speed = [random.randint(min_speed, max_speed), random.randint(-sideways_speed, sideways_speed)]
    elif side == "right":
        rect = pygame.Rect(game_panel.right, random.randint(game_panel.top, game_panel.bottom - target_size), target_size, target_size)
        speed = [-random.randint(min_speed, max_speed), random.randint(-sideways_speed, sideways_speed)]
    else:
        rect = pygame.Rect(random.randint(game_panel.left, game_panel.right - target_size), game_panel.top - target_size, target_size, target_size)
        speed = [random.randint(-sideways_speed, sideways_speed), random.randint(min_speed, max_speed)]

    return target_class(rect, speed)

def target_is_outside(target, game_panel):
    return target.rect.right < game_panel.left or target.rect.left > game_panel.right or target.rect.bottom < game_panel.top or target.rect.top > game_panel.bottom

def choose_target_class(level):
    return random.choices([NormalTarget, BonusTarget, SpecialTarget, ShieldedTarget, Bomb], weights=level.target_weights, k=1)[0]