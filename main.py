import pygame
import os
from elements import *
from leaderboard_system import *
from ui import UI
from audio import SoundManager

os.chdir(os.path.dirname(__file__))

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

# CONSTANTS
WIDTH, HEIGHT = 1000, 800
FPS = 60

# SETUP
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rapid Fire")
levels = [
    Level(0, 15, 8, 4, 1200, (90, 8, 2, 0, 0), 3),
    Level(1, 14, 12, 5, 1050, (82, 14, 4, 0, 0), 3),
    Level(2, 13, 17, 7, 900, (68, 18, 6, 5, 3), 4),
    Level(3, 12, 22, 9, 750, (58, 21, 8, 9, 4), 4),
    Level(4, 11, 28, 11, 650, (48, 24, 11, 12, 5), 5),
    Level(5, 10, 35, 13, 550, (39, 27, 14, 14, 6), 6),
]
pygame.mouse.set_cursor(*pygame.cursors.broken_x)
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()
score = 0

title_font = pygame.font.SysFont(None, 80)
countdown_font = pygame.font.SysFont(None, 150)
hud_font = pygame.font.SysFont(None, 30)
small_font = pygame.font.SysFont(None, 22)

dim_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # transparent background
dim_overlay.fill((0, 0, 0, 160))

menu_button_font = pygame.font.SysFont(None, 32)
menu_subtitle_font = pygame.font.SysFont(None, 24)

ui = UI(screen, WIDTH, HEIGHT, title_font, hud_font, small_font, menu_button_font, menu_subtitle_font)

sounds = SoundManager()


def leaderboard(username, score):
    highscore = update_highscore(username, score)
    scores = load_scores()

    sorted_scores = sorted(scores.items(), key=lambda player: player[1], reverse=True)

    while True:
        mouse_position = pygame.mouse.get_pos()

        menu_button = pygame.Rect(WIDTH // 2 - 100, 650, 200, 60)
        quit_button = pygame.Rect(WIDTH // 2 - 100, 720, 200, 60)

        ui.draw_menu_background()
        ui.draw_menu_heading("LEADERBOARD", f"{username}  |  Score: {score}  |  Highscore: {highscore}", (255, 205, 70))

        # top 10 scores
        for index, (player_name, player_score) in enumerate(sorted_scores[:10]):
            row = pygame.Rect(WIDTH // 2 - 220, 170 + index * 40, 440, 32)

            # highlight current user
            if player_name == username:
                row_color = (71, 71, 107)
            else:
                row_color = (24, 28, 42)

            pygame.draw.rect(screen, row_color, row, border_radius=6)

            rank_text = font.render(f"{index + 1}. {player_name}", True, ui.menu_text)
            score_text = font.render(str(player_score), True, (255, 205, 70))

            screen.blit(rank_text, (row.x + 14, row.y + 4))
            screen.blit(score_text, score_text.get_rect(right=row.right - 14, centery=row.centery))

        ui.draw_menu_button(menu_button, "MAIN MENU", mouse_position, "primary")
        ui.draw_menu_button(quit_button, "QUIT", mouse_position, "danger")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if menu_button.collidepoint(event.pos): # return to main menu
                    return "menu"
                if quit_button.collidepoint(event.pos): # quit game
                    return "quit"

        pygame.display.flip()
        clock.tick(FPS)

def next_level_countdown(background):
    countdown_start = pygame.time.get_ticks()
    COUNTDOWN_MS = 3000
    sounds.play_countdown()

    while True:
        elapsed = pygame.time.get_ticks() - countdown_start
        remaining_ms = COUNTDOWN_MS - elapsed

        if remaining_ms <= 0: # end countdown & start level
            return "next_level"

        seconds_left = (remaining_ms + 999) // 1000

        screen.blit(background, (0, 0))
        screen.blit(dim_overlay, (0, 0))

        text = font.render("NEXT LEVEL STARTS IN", True, "white")
        number = countdown_font.render(str(seconds_left), True, "yellow")

        screen.blit(text, text.get_rect(center=(WIDTH // 2, 250)))
        screen.blit(number, number.get_rect(center=(WIDTH // 2, 390)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        pygame.display.flip()
        clock.tick(FPS)

def level_complete(level_id, username, score):
    background = screen.copy() # frozen frame of the gameplay
    modal_rect = pygame.Rect(WIDTH // 2 - 260, 145, 520, 385)

    while True:
        mouse_position = pygame.mouse.get_pos()

        continue_button = pygame.Rect(WIDTH // 2 - 100, 330, 200, 60)
        quit_button = pygame.Rect(WIDTH // 2 - 100, 410, 200, 60)

        screen.blit(background, (0, 0))
        screen.blit(dim_overlay, (0, 0))
        ui.draw_modal_panel(modal_rect)

        message = title_font.render("Level Complete!", True, "green")
        subtitle = font.render(f"Level {level_id + 1} cleared | Score: {score}", True, ui.menu_muted)
        screen.blit(message, message.get_rect(center=(WIDTH // 2, modal_rect.top + 70)))
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, modal_rect.top + 112)))

        if level_id + 1 >= len(levels): # all levels completed
            continue_label = "LEADERBOARD"
            secondary_label = "MAIN MENU"
        else:
            continue_label = "CONTINUE"
            secondary_label = "QUIT"

        continue_style = "gold" if level_id + 1 >= len(levels) else "primary"
        secondary_style = "primary" if level_id + 1 >= len(levels) else "danger"

        ui.draw_menu_button(continue_button, continue_label, mouse_position, continue_style)
        ui.draw_menu_button(quit_button, secondary_label, mouse_position, secondary_style)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if continue_button.collidepoint(event.pos):
                    if level_id + 1 >= len(levels):
                        return leaderboard(username, score)
                    return next_level_countdown(background)
                elif quit_button.collidepoint(event.pos):
                    if level_id + 1 >= len(levels): # save & quit
                        update_highscore(username, score)
                        return "menu"
                    return "quit"

        pygame.display.flip()
        clock.tick(FPS)

def game_over(username, score, highscore):
    highscore = update_highscore(username, score)
    sounds.play_game_over()

    while True:
        mouse_position = pygame.mouse.get_pos()

        restart_button = pygame.Rect(WIDTH // 2 - 125, 340, 250, 55)
        leaderboard_button = pygame.Rect(WIDTH // 2 - 125, 410, 250, 55)
        menu_button = pygame.Rect(WIDTH // 2 - 125, 480, 250, 55)
        quit_button = pygame.Rect(WIDTH // 2 - 125, 550, 250, 55)

        ui.draw_menu_background()
        ui.draw_menu_heading("GAME OVER", f"Score: {score}  |  Highscore: {highscore}", (235, 95, 105))

        ui.draw_menu_button(restart_button, "RESTART", mouse_position, "primary")
        ui.draw_menu_button(leaderboard_button, "LEADERBOARD", mouse_position, "gold")
        ui.draw_menu_button(menu_button, "MAIN MENU", mouse_position, "primary")
        ui.draw_menu_button(quit_button, "QUIT", mouse_position, "danger")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_button.collidepoint(event.pos):
                    return "restart"
                elif leaderboard_button.collidepoint(event.pos):
                    return leaderboard(username, score)
                elif menu_button.collidepoint(event.pos):
                    return "menu"
                elif quit_button.collidepoint(event.pos):
                    return "quit"

        pygame.display.flip()
        clock.tick(FPS)

def get_combo_multiplier(combo):
    if combo >= 10:
        return 3
    if combo >= 5:
        return 2
    return 1

def draw_animated_target(target):
    original_rect = target.rect.copy()
    scale = target.get_draw_scale()

    # smaller during spawn animation
    # normal size otherwise
    scaled_width = max(1, round(original_rect.width * scale))
    scaled_height = max(1, round(original_rect.height * scale))

    target.rect = pygame.Rect(0, 0, scaled_width, scaled_height)
    target.rect.center = original_rect.center
    target.draw(screen)

    # after drawing, go back to original scale parameter for further calculations
    target.rect = original_rect

def game(level_id, username, highscore):
    # panels
    game_panel = pygame.Rect(0, 0, WIDTH, int(.8 * HEIGHT))
    info_panel = pygame.Rect(0, game_panel.bottom, WIDTH, HEIGHT - game_panel.height)

    targets = []
    score_popups = []
    last_spawn_time = pygame.time.get_ticks() - levels[level_id].spawn_interval # last time a target was spawned

    global score
    if level_id == 0:
        score = 0
    levels[level_id].start()
    level_score = 0

    combo = 0

    camera_offset = pygame.Vector2(0, 0)

    # camera movement boundaries
    CAMERA_MAX_X = 32
    CAMERA_MAX_Y = 22
    # camera movement smoothness
    CAMERA_SMOOTHNESS = 0.10
    
    while True:
        mouse_position = pygame.mouse.get_pos()
        
        if game_panel.collidepoint(mouse_position): # mouse is in the game panel => camera movement
            # values in [-1, 1]
            # calculates how far the mouse is from the center of the arena
            normalized_x = (mouse_position[0] - game_panel.centerx) / (game_panel.width / 2)
            normalized_y = (mouse_position[1] - game_panel.centery) / (game_panel.height / 2)
            # transform normalized coordinates in real displacement
            camera_target = pygame.Vector2(-normalized_x * CAMERA_MAX_X, -normalized_y * CAMERA_MAX_Y)
        else: # mouse is in the info panel => camera resets
            camera_target = pygame.Vector2(0, 0)

        # move the camera smoothly, don't jump instantly to the position
        camera_offset += (camera_target - camera_offset) * CAMERA_SMOOTHNESS
        camera_x = round(camera_offset.x)
        camera_y = round(camera_offset.y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                hit_target = False
                
                # go through a copy of the target list
                for target in targets[:]:
                    if target.is_destroying():
                        continue

                    # move targets with the camera
                    target_x = target.rect.centerx + camera_x
                    target_y = target.rect.centery + camera_y
                    target_radius = target.rect.width * target.get_draw_scale() / 2  # smaller hitbox for spawn animation

                    # target hit
                    if (mouse_x - target_x) ** 2 + (mouse_y - target_y) ** 2 <= target_radius ** 2:
                        hit_target = True
                        
                        if target.hit(): # for non-shielded, returns True
                            if target.points < 0: # bomb
                                combo = 0
                                points = target.points
                            else:
                                combo += 1
                                multiplier = get_combo_multiplier(combo)
                                points = target.points * multiplier
                            
                            score = max(0, score + points)
                            level_score = max(0, level_score + points)
                            sounds.play_hit(target.points)
                            score_popups.append(ScorePopup(target.rect.center, points, target.color))
                            target.start_destroying()
                        else: # shielded target
                            sounds.play_shield_hit()
                        
                        break

                if not hit_target:
                    combo = 0

        current_time = pygame.time.get_ticks()
        # check if a new target can be added
        if len(targets) < levels[level_id].max_targets and current_time - last_spawn_time >= levels[level_id].spawn_interval:
            target_class = choose_target_class(levels[level_id]) # randomly choose a type of target
            new_target = create_target_from_edge(game_panel, 2, levels[level_id].max_speed, target_class)
            targets.append(new_target)
            last_spawn_time = current_time
        
        # movement
        for target in targets[:]:
            if target.is_destroying():
                if target.destroy_animation_finished():
                    targets.remove(target)
                continue

            target.move()
            if target.rect.colliderect(game_panel): # target has entered the game panel
                target.mark_as_entered()
            if target.is_expired(): # target survived for too long on the game panel
                target.start_destroying()
            elif target.has_entered and target_is_outside(target, game_panel): # target has left the game panel
                target.start_destroying()

        # score pop-up
        for popup in score_popups[:]:
            popup.update() # popup animation
            if popup.is_expired():
                score_popups.remove(popup)

        combo_multiplier = get_combo_multiplier(combo)

        time_left = levels[level_id].time_left()
        time_progress = levels[level_id].progress()

        # drawings
        ui.draw_game_interface(game_panel, info_panel, username, score, level_score, combo, combo_multiplier, time_left, time_progress, level_id + 1, len(levels), levels[level_id].required_score)
        ui.draw_arena_dots(game_panel, camera_x, camera_y)

        old_clip = screen.get_clip() # save the current screen drawing boundary
        screen.set_clip(game_panel) # draw only in the game panel
        for target in targets:
            target.rect.move_ip(camera_x, camera_y) # move the target in place (w/ camera offset)
            draw_animated_target(target)
            # camera should only affect how the target is seen,
            # not its actual position used in logic
            target.rect.move_ip(-camera_x, -camera_y) # move the target back to its original place
        for popup in score_popups:
            popup_text = font.render(popup.text, True, popup.color)
            popup_position = (popup.position.x + camera_x, popup.position.y + camera_y) # move with camera
            screen.blit(popup_text, popup_text.get_rect(center=popup_position))
        screen.set_clip(old_clip) # put back the old drawing limit

        pygame.display.flip()

        if time_left == 0: # level ended
            if level_score >= levels[level_id].required_score:
                exit_message = level_complete(level_id, username, score)
                if exit_message == "quit" or exit_message == "menu": # quit or return to main menu
                    return exit_message
                if exit_message == "next_level": # go to next level
                    return game(level_id + 1, username, highscore)
            else:
                exit_message = game_over(username, score, highscore)
                if exit_message == "quit" or exit_message == "menu": # quit or return to main menu
                    return exit_message
                if exit_message == "restart": # restart the game
                    return game(0, username, highscore)

        clock.tick(FPS)

def enter_username():
    username = ""
    input_box = pygame.Rect(WIDTH // 2 - 200, 350, 400, 55)

    while True:
        ui.draw_menu_background()
        ui.draw_menu_heading("PLAYER NAME", "Choose a name before starting.", (235, 245, 255))

        pygame.draw.rect(screen, (17, 24, 34), input_box, border_radius=10)
        pygame.draw.rect(screen, ui.menu_border, input_box, width=2, border_radius=10)

        shown_name = username if username else "Type your name..."
        name_color = ui.menu_text if username else ui.menu_muted

        name_text = font.render(shown_name, True, name_color)
        screen.blit(name_text, (input_box.x + 15, input_box.y + 12))

        hint = small_font.render("Press ENTER to start", True, ui.menu_muted)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 440)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN: # user started typing
                if event.key == pygame.K_RETURN: # user pressed enter
                    if username.strip() != "": # save valid username
                        return username.strip()
                elif event.key == pygame.K_BACKSPACE: # delete last character
                    username = username[:-1]
                # text character
                elif len(username) < 15: # username size should be smaller than 15 characters
                    username += event.unicode # add the actual character written (not the key code)

        pygame.display.flip()
        clock.tick(FPS)

def tutorial():
    card_x = WIDTH // 2 - 285
    card_width = 570
    card_height = 70

    # info about targets
    examples = [
        (
            NormalTarget(pygame.Rect(card_x + 18, 180, 58, 58), [0, 0]),
            "NORMAL TARGET",
            "+1 point",
            (90, 220, 130)
        ),
        (
            BonusTarget(pygame.Rect(card_x + 18, 260, 58, 58), [0, 0]),
            "BONUS TARGET",
            "+3 points",
            (255, 210, 90)
        ),
        (
            SpecialTarget(pygame.Rect(card_x + 18, 340, 58, 58), [0, 0]),
            "SPECIAL TARGET",
            "+5 points  |  Very fast",
            (255, 95, 105)
        ),
        (
            ShieldedTarget(pygame.Rect(card_x + 18, 420, 58, 58), [0, 0]),
            "SHIELDED TARGET",
            "+4 points | Break shield, then hit again",
            (110, 245, 230)
        ),
        (
            Bomb(pygame.Rect(card_x + 18, 500, 58, 58),[0, 0]),
            "BOMB",
            "-2 points  |  Combo resets",
            (245, 110, 200)
        )
    ]

    back_button = pygame.Rect(WIDTH // 2 - 100, 710, 200, 55)
    combo_box = pygame.Rect(card_x, 585, card_width, 95) # box for info about combo

    while True:
        mouse_position = pygame.mouse.get_pos()

        ui.draw_menu_background()
        ui.draw_menu_heading("HOW TO PLAY", "Reach the level goal before the timer expires.")

        # draw info about all targets
        for index, (target, title, description, color) in enumerate(examples):
            card = pygame.Rect(card_x, 170 + index * 80, card_width, card_height)
            ui.draw_tutorial_card(card, title, description, color)
            target.draw(screen)
        
        pygame.draw.rect(screen, (24, 28, 42), combo_box, border_radius=10)
        pygame.draw.rect(screen, ui.menu_border, combo_box, width=1, border_radius=10)

        # info about combo
        combo_title = font.render("COMBO", True, (255, 210, 100))
        combo_line_1 = small_font.render("5 hits in a row: x2 points", True, ui.menu_text)
        combo_line_2 = small_font.render("10 hits in a row: x3 points", True, ui.menu_text)
        combo_line_3 = small_font.render("Missed click or bomb: combo resets", True, ui.menu_muted)
        screen.blit(combo_title, (combo_box.x + 22, combo_box.y + 12))
        screen.blit(combo_line_1, (combo_box.x + 155, combo_box.y + 14))
        screen.blit(combo_line_2, (combo_box.x + 155, combo_box.y + 40))
        screen.blit(combo_line_3, (combo_box.x + 155, combo_box.y + 66))

        ui.draw_menu_button(back_button, "BACK", mouse_position, "primary")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.collidepoint(event.pos): # return to main menu
                    return "menu"
                
        pygame.display.flip()
        clock.tick(FPS)

def start_menu():
    global score

    while True:
        mouse_position = pygame.mouse.get_pos()

        play_button = pygame.Rect(WIDTH // 2 - 120, 290, 240, 60)
        tutorial_button = pygame.Rect(WIDTH // 2 - 120, 370, 240, 60)
        quit_button = pygame.Rect(WIDTH // 2 - 120, 450, 240, 60)

        ui.draw_menu_background()
        ui.draw_menu_heading("RAPID FIRE", "Hit targets. Beat your highscore.", (235, 245, 255))
        ui.draw_menu_button(play_button, "PLAY", mouse_position, "primary")
        ui.draw_menu_button(tutorial_button, "HOW TO PLAY", mouse_position, "gold")
        ui.draw_menu_button(quit_button, "QUIT", mouse_position, "danger")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button.collidepoint(event.pos): # play the game
                    score = 0
                    username = enter_username()
                    if username is None:
                        return
                    highscore = get_highscore(username)
                    if game(0, username, highscore) == "quit":
                        return
                elif tutorial_button.collidepoint(event.pos): # go to tutorial
                    if tutorial() == "quit":
                        return
                elif quit_button.collidepoint(event.pos): # quit the game
                    return
                
        pygame.display.flip()
        clock.tick(FPS)
                
if __name__ == "__main__":
    start_menu()
    pygame.quit()