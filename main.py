import pygame
import sys
import random
import os
import math

# --- 1. Initialization & Setup ---
pygame.init()

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("NATHAN PRO")
clock = pygame.time.Clock()

# COLORS
BLACK = (5, 5, 5)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
RED = (255, 50, 50)
GRAY = (40, 40, 40)

# STATES
START_SCREEN = "START"
MENU = "MENU"
PLAYING = "PLAYING"
ABOUT = "ABOUT"
GAMEOVER = "GAMEOVER"

current_state = START_SCREEN
current_score = 0

# --- HIGH SCORE SYSTEM ---
SCORE_FILE = "highscore.txt"

def load_high_score():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as f:
            try: return int(f.read())
            except: return 0
    return 0

def save_high_score(score):
    with open(SCORE_FILE, "w") as f:
        f.write(str(score))

high_score = load_high_score()

# FONT
def get_font(size):
    return pygame.font.SysFont("Arial", size, bold=True)

def draw_text(text, size, color, x, y, center=False):
    font = get_font(size)
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center: rect.center = (x, y)
    else: rect.topleft = (x, y)
    screen.blit(img, rect)

# BUTTON
def draw_button(text, y, width=500, height=100):
    x = SCREEN_WIDTH // 2 - width // 2
    rect = pygame.Rect(x, y, width, height)
    mouse = pygame.mouse.get_pos()
    hover = rect.collidepoint(mouse)
    if hover:
        pygame.draw.rect(screen, CYAN, rect.inflate(10, 10), border_radius=12)
        pygame.draw.rect(screen, BLACK, rect, border_radius=12)
    else:
        pygame.draw.rect(screen, GRAY, rect, border_radius=12)
    pygame.draw.rect(screen, CYAN, rect, 2, border_radius=12)
    draw_text(text, 45, WHITE, SCREEN_WIDTH // 2, y + height // 2, center=True)
    return rect

def draw_borders():
    pygame.draw.rect(screen, WHITE, (15, 15, SCREEN_WIDTH - 30, SCREEN_HEIGHT - 30), 3)
    pygame.draw.rect(screen, WHITE, (30, 30, SCREEN_WIDTH - 60, SCREEN_HEIGHT - 60), 1)

# --- ANALOG SETUP ---
analog_base_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 250)
analog_radius = 110
stick_pos = list(analog_base_pos)
stick_radius = 55
is_dragging = False

# --- GAME VARIABLES ---
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT // 2
player_speed_factor = 0.2
obstacles = []
powerups = []
game_speed = 12
power_timer = 0 

def reset_game():
    global player_x, player_y, current_score, obstacles, powerups, game_speed, power_timer, stick_pos
    player_x = SCREEN_WIDTH // 2
    player_y = SCREEN_HEIGHT // 2
    current_score = 0
    obstacles.clear()
    powerups.clear()
    game_speed = 12
    power_timer = 0
    stick_pos = list(analog_base_pos)

def spawn_obstacle():
    obs_x = random.randint(100, SCREEN_WIDTH - 100)
    obstacles.append([obs_x, -100, 65])

def spawn_powerup():
    p_x = random.randint(100, SCREEN_WIDTH - 100)
    powerups.append([p_x, -100, 50])

# --- 3. Main Loop ---
def main():
    global current_state, current_score, high_score, game_speed, player_x, player_y, power_timer, stick_pos, is_dragging

    while True:
        screen.fill(BLACK)
        mx, my = pygame.mouse.get_pos()
        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                dist = math.hypot(mx - analog_base_pos[0], my - analog_base_pos[1])
                if dist < analog_radius:
                    is_dragging = True
            if event.type == pygame.MOUSEBUTTONUP:
                is_dragging = False
                stick_pos = list(analog_base_pos)

        # --- START SCREEN ---
        if current_state == START_SCREEN:
            draw_text("NATHAN PRO", 110, CYAN, SCREEN_WIDTH // 2, 350, center=True)
            draw_text(f"BEST SCORE: {high_score}", 60, WHITE, SCREEN_WIDTH // 2, 500, center=True)
            btn = draw_button("START", 650)
            if click and btn.collidepoint(mx, my): current_state = MENU

        # --- MENU ---
        elif current_state == MENU:
            draw_text("MAIN MENU", 90, CYAN, SCREEN_WIDTH // 2, 300, center=True)
            b1 = draw_button("PLAY GAME", 450); b2 = draw_button("ABOUT", 580); b3 = draw_button("EXIT", 710)
            if click:
                if b1.collidepoint(mx, my): reset_game(); current_state = PLAYING
                elif b2.collidepoint(mx, my): current_state = ABOUT
                elif b3.collidepoint(mx, my): pygame.quit(); sys.exit()

        # --- PLAYING ---
        elif current_state == PLAYING:
            effective_speed = game_speed * 2 if power_timer > 0 else game_speed
            if power_timer > 0: power_timer -= 1
            game_speed += 0.005
            
            # ANALOG CONTROL
            if is_dragging:
                dx = mx - analog_base_pos[0]
                dy = my - analog_base_pos[1]
                distance = math.hypot(dx, dy)
                if distance > analog_radius:
                    ratio = analog_radius / distance
                    dx *= ratio; dy *= ratio
                stick_pos = [analog_base_pos[0] + dx, analog_base_pos[1] + dy]
                player_x += dx * player_speed_factor
                player_y += dy * player_speed_factor

            player_x = max(80, min(SCREEN_WIDTH - 80, player_x))
            player_y = max(80, min(SCREEN_HEIGHT - 450, player_y))

            # DRAW ANALOG
            pygame.draw.circle(screen, GRAY, analog_base_pos, analog_radius, 3) 
            pygame.draw.circle(screen, CYAN, (int(stick_pos[0]), int(stick_pos[1])), stick_radius)

            if random.randint(1, 15) == 1: spawn_obstacle()
            if random.randint(1, 400) == 1: spawn_powerup()

            player_rect = pygame.Rect(player_x - 30, player_y, 60, 80)

            # POWERUPS
            for p in powerups[:]:
                p[1] += effective_speed
                p_rect = pygame.Rect(p[0]-25, p[1], 50, 50)
                pygame.draw.rect(screen, CYAN, p_rect, 3) 
                if player_rect.colliderect(p_rect):
                    power_timer = 300; powerups.remove(p)
                elif p[1] > SCREEN_HEIGHT: powerups.remove(p)

            # OBSTACLES
            for obs in obstacles[:]:
                obs[1] += effective_speed
                rect = pygame.Rect(obs[0] - 30, obs[1], 60, 60)
                pygame.draw.rect(screen, RED, rect, 3)
                if player_rect.colliderect(rect):
                    if current_score > high_score: high_score = current_score; save_high_score(high_score)
                    current_state = GAMEOVER
                elif obs[1] > SCREEN_HEIGHT: obstacles.remove(obs)

            # PLAYER
            pts = [(player_x, player_y), (player_x - 40, player_y + 80), (player_x, player_y + 60), (player_x + 40, player_y + 80)]
            pygame.draw.polygon(screen, CYAN, pts, 3)
            
            current_score += 2 if power_timer > 0 else 1 
            draw_text(f"SCORE: {current_score}", 45, CYAN, 80, 80)
            draw_text(f"BEST: {high_score}", 40, WHITE, SCREEN_WIDTH - 250, 80)

        # --- ABOUT (ኢሜይል የተጨመረበት) ---
        elif current_state == ABOUT:
            draw_text("DEVELOPER INFO", 80, CYAN, SCREEN_WIDTH // 2, 300, center=True)
            draw_text("Developer: Natnael Mesafnt", 45, WHITE, SCREEN_WIDTH // 2, 450, center=True)
            draw_text("Email: natnaelmesafnt82@gmail.com", 35, WHITE, SCREEN_WIDTH // 2, 520, center=True)
            draw_text("Phone: +25145512655", 40, WHITE, SCREEN_WIDTH // 2, 590, center=True)
            btn = draw_button("BACK", 750)
            if click and btn.collidepoint(mx, my): current_state = MENU

        # --- GAMEOVER ---
        elif current_state == GAMEOVER:
            draw_text("CRASHED!", 100, RED, SCREEN_WIDTH // 2, 350, center=True)
            draw_text(f"SCORE: {current_score}", 50, WHITE, SCREEN_WIDTH // 2, 460, center=True)
            draw_text(f"BEST SCORE: {high_score}", 50, CYAN, SCREEN_WIDTH // 2, 530, center=True)
            b1 = draw_button("RETRY", 650); b2 = draw_button("MENU", 780)
            if click:
                if b1.collidepoint(mx, my): reset_game(); current_state = PLAYING
                elif b2.collidepoint(mx, my): current_state = MENU

        draw_borders()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
