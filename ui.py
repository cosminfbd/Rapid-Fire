import pygame
import math

class UI:
    def __init__(self, screen, width, height, title_font, hud_font, small_font, menu_button_font, menu_subtitle_font):
        self.screen             = screen
        self.width              = width
        self.height             = height
        
        self.title_font         = title_font
        self.hud_font           = hud_font
        self.small_font         = small_font
        self.menu_button_font   = menu_button_font
        self.menu_subtitle_font = menu_subtitle_font    
        
        self.menu_background    = (10, 14, 20)
        self.menu_panel         = (31, 35, 52)
        self.menu_border        = (163, 163, 194)
        self.menu_text          = (240, 245, 255)
        self.menu_muted         = (170, 180, 205) # subtitles & secondary text

    def draw_menu_background(self):
        self.screen.fill(self.menu_background)

        panel = pygame.Rect(self.width // 2 - 310, 35, 620, 750)

        pygame.draw.rect(self.screen, self.menu_panel, panel, border_radius=18)
        pygame.draw.rect(self.screen, self.menu_border, panel, width=2, border_radius=18)
        pygame.draw.line(self.screen, self.menu_border, (panel.left + 35, panel.top + 105), (panel.right - 35, panel.top + 105), 1)

    def draw_menu_heading(self, title, subtitle="", color=None):
        if color is None:
            color = self.menu_text

        title_text = self.title_font.render(title, True, color)
        self.screen.blit(title_text, title_text.get_rect(center=(self.width // 2, 85)))

        if subtitle:
            subtitle_text = self.menu_subtitle_font.render(subtitle, True, self.menu_muted)
            self.screen.blit(subtitle_text, subtitle_text.get_rect(center=(self.width // 2, 130)))

    def draw_menu_button(self, rect, label, mouse_position, style="primary"):
        styles = { # normal color, hover color, border color, text color
            "primary": ((71, 71, 107), (92, 92, 140), self.menu_border, self.menu_text),
            "danger": ((105, 48, 65), (140, 58, 80), (190, 105, 125), self.menu_text),
            "gold": ((185, 145, 50), (220, 180, 75), (255, 215, 105), (25, 25, 30))
        }

        normal_color, hover_color, border_color, text_color = styles[style]
        color = hover_color if rect.collidepoint(mouse_position) else normal_color
        shadow_rect = rect.move(0, 4)

        pygame.draw.rect(self.screen, (8, 10, 16), shadow_rect, border_radius=10)
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=10)

        button_text = self.menu_button_font.render(label, True, text_color)
        self.screen.blit(button_text, button_text.get_rect(center=rect.center))

    def draw_tutorial_card(self, rect, title, description, title_color):
        pygame.draw.rect(self.screen, (24, 28, 42), rect, border_radius=10)
        pygame.draw.rect(self.screen, self.menu_border, rect, width=1, border_radius=10)

        title_text = self.small_font.render(title, True, title_color)
        description_text = self.small_font.render(description, True, self.menu_text)
        self.screen.blit(title_text, (rect.x + 95, rect.y + 14))
        self.screen.blit(description_text, (rect.x + 95, rect.y + 43))

    def draw_arena_dots(self, game_panel, camera_x, camera_y):
        spacing = 56
        dot_color = (93, 97, 142)

        for x in range(game_panel.left - spacing, game_panel.right + spacing, spacing):
            for y in range(game_panel.top - spacing, game_panel.bottom + spacing, spacing):
                # adjust for camera movement
                dot_x = x + camera_x
                dot_y = y + camera_y

                if game_panel.collidepoint(dot_x, dot_y): # draw dot if inside game panel
                    pygame.draw.circle(self.screen, dot_color, (dot_x, dot_y), 2)

    def draw_timer_ring(self, center, radius, progress, time_left):
        progress = max(0, min(1, progress))

        ring_rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        ring_rect.center = center

        pygame.draw.circle(self.screen,(35, 40, 55), center, radius, 9) # empty ring

        if time_left <= 3:
            ring_color = (255, 100, 100)
        else:
            ring_color = (255, 210, 100)

        start_angle = -math.pi / 2

        if progress >= 0.999: # fill the ring
            pygame.draw.circle(self.screen, ring_color, center, radius, 9)
        elif progress > 0:
            # 2 * pi => complete circle
            end_angle = start_angle + 2 * math.pi * progress
            pygame.draw.arc(self.screen, ring_color, ring_rect, start_angle, end_angle, 9)

        time_text = self.hud_font.render(f"{time_left}s", True, (235, 245, 255))

        self.screen.blit(time_text, time_text.get_rect(center=center))
    
    def draw_game_interface(self, game_panel, info_panel, username, score, level_score, combo, combo_multiplier, time_left, time_progress, level_number, total_levels, required_score):
        self.screen.fill((10, 14, 20))

        # game panel
        pygame.draw.rect(self.screen, (71, 71, 107), game_panel)

        # info panel
        pygame.draw.rect(self.screen, (51, 51, 77), info_panel)
        pygame.draw.line(self.screen, (163, 163, 194), (0, info_panel.top), (self.width, info_panel.top), 2)

        level_text = self.small_font.render(f"LEVEL {level_number}/{total_levels}", True, (150, 190, 225))
        self.screen.blit(level_text, (20, 16))

        if combo >= 2:
            if combo_multiplier == 3:
                combo_color = (255, 105, 135)
            elif combo_multiplier == 2:
                combo_color = (255, 210, 100)
            else:
                combo_color = (150, 190, 225)
            combo_label = f"COMBO {combo}"
            if combo_multiplier > 1:
                combo_label += f"  x{combo_multiplier}"
            combo_text = self.small_font.render(combo_label, True, combo_color)
            self.screen.blit(combo_text, combo_text.get_rect(topright=(self.width - 20, 16)))

        score_text = self.hud_font.render(f"SCORE: {score}", True, (235, 245, 255))

        if level_score >= required_score:
            goal_color = (115, 235, 150)
        else:
            goal_color = (255, 210, 100)

        display_level_score = min(level_score, required_score)
        goal_text = self.hud_font.render(f"GOAL: {display_level_score} / {required_score}", True, goal_color)

        player_text = self.hud_font.render(f"PLAYER: {username}", True, (235, 245, 255))

        self.screen.blit(score_text, (30, info_panel.y + 28))
        self.screen.blit(goal_text, (30, info_panel.y + 72))
        self.draw_timer_ring((self.width // 2, info_panel.centery + 5), 48, time_progress, time_left)
        self.screen.blit(player_text, player_text.get_rect(right=self.width - 30, centery=info_panel.y + 45))

    def draw_modal_panel(self, rect): # level complete
        shadow_rect = rect.move(0, 7)
        pygame.draw.rect(self.screen,(8, 10, 16), shadow_rect, border_radius=18)

        panel_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (31, 35, 52, 235), panel_surface.get_rect(), border_radius=18)
        self.screen.blit(panel_surface, rect.topleft)

        pygame.draw.rect(self.screen, self.menu_border, rect, width=2, border_radius=18)
        pygame.draw.line(self.screen, self.menu_border, (rect.left + 40, rect.top + 135), (rect.right - 40, rect.top + 135), 1)