import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grimm Adventure")

player_width, player_height = 40, 60
BASE_X, BASE_Y = 100, HEIGHT - player_height - 100
player_x, player_y = BASE_X, BASE_Y
player_vel_y = 0
player_speed = 7
jump_power = 18
gravity = 1
on_ground = False
can_double_jump = True

run_anim_frame = 0
run_anim_timer = 0
RUN_ANIM_SPEED = 6
shoot_anim_timer = 0
SHOOT_ANIM_LENGTH = 6
jump_anim = False

platforms = []
platform_width = 120
platform_height = 20
scroll_speed = 5

enemy_width, enemy_height = 40, 60
enemies = []

projectile_width, projectile_height = 10, 5
projectile_speed = 12
projectiles = []

explosions = []
EXPLOSION_PARTICLES = 30
EXPLOSION_LIFETIME = 20

high_score = 0

def generate_platforms():
    platforms.clear()
    start_platform = pygame.Rect(0, HEIGHT - platform_height - 40, 300, platform_height)
    platforms.append(start_platform)
    x = start_platform.width + 50
    while x < WIDTH * 2:
        y = random.randint(HEIGHT // 2, HEIGHT - platform_height - 50)
        platforms.append(pygame.Rect(x, y, platform_width, platform_height))
        x += random.randint(150, 300)

def generate_enemies():
    enemies.clear()
    for plat in platforms[1:]:
        if random.random() < 0.3:
            ex = plat.x + random.randint(0, plat.width - enemy_width)
            ey = plat.y - enemy_height
            enemies.append(pygame.Rect(ex, ey, enemy_width, enemy_height))

def reset_game():
    global player_x, player_y, player_vel_y, score, enemies, projectiles, explosions, can_double_jump, game_over, run_anim_frame, run_anim_timer, shoot_anim_timer, jump_anim
    player_x, player_y = BASE_X, BASE_Y
    player_vel_y = 0
    score = 0
    projectiles = []
    explosions = []
    can_double_jump = True
    game_over = False
    run_anim_frame = 0
    run_anim_timer = 0
    shoot_anim_timer = 0
    jump_anim = False
    generate_platforms()
    generate_enemies()

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 28)
score = 0
game_over = False

class Explosion:
    def __init__(self, x, y):
        self.particles = []
        for _ in range(EXPLOSION_PARTICLES):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(3, 8)
            dx = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            dy = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            self.particles.append({
                "pos": [x, y],
                "vel": [dx, dy],
                "life": EXPLOSION_LIFETIME
            })

    def update(self):
        for p in self.particles:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]
            p["life"] -= 1
        self.particles = [p for p in self.particles if p["life"] > 0]

    def draw(self, surface):
        for p in self.particles:
            pygame.draw.rect(surface, (255, 255, 0), (int(p["pos"][0]), int(p["pos"][1]), 4, 4))

def lore_menu():
    lore_lines = [
        "LORE:",
        "",
        "You are GRIMM, a lone force of vengeance and fury.",
        "Forged in the fires of hell, you are the last hope against the endless horde.",
        "Your fists shatter steel, your rage ignites the night.",
        "",
        "ENEMIES: The Forsaken Wardens",
        "Once protectors of this world, now twisted by demonic power.",
        "They stand motionless, waiting for a hero to end their suffering.",
        "",
        "Press M to return to Main Menu"
    ]
    while True:
        screen.fill((30, 30, 30))
        box = pygame.Surface((WIDTH - 120, HEIGHT - 120))
        box.set_alpha(230)
        box.fill((20, 20, 20))
        screen.blit(box, (60, 60))
        for i, line in enumerate(lore_lines):
            color = (255, 255, 0) if i == 0 else (200, 200, 200)
            lore_msg = small_font.render(line, True, color)
            screen.blit(lore_msg, (WIDTH // 2 - lore_msg.get_width() // 2, 100 + i * 32))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                return

def main_menu():
    global high_score
    while True:
        screen.fill((20, 20, 20))
        title = font.render("GRIMM ADVENTURE", True, (255, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))
        play_msg = small_font.render("Press ENTER to Start", True, (255, 255, 255))
        screen.blit(play_msg, (WIDTH // 2 - play_msg.get_width() // 2, 130))
        lore_msg = small_font.render("Press L for Lore", True, (255, 255, 0))
        screen.blit(lore_msg, (WIDTH // 2 - lore_msg.get_width() // 2, 170))
        esc_msg = small_font.render("Press ESC to Quit", True, (255, 255, 255))
        screen.blit(esc_msg, (WIDTH // 2 - esc_msg.get_width() // 2, 210))
        hs_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
        screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, 260))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_l:
                    lore_menu()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

main_menu()
reset_game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not game_over:
            if on_ground:
                player_vel_y = -jump_power
                can_double_jump = True
                jump_anim = True
            elif can_double_jump:
                player_vel_y = -jump_power
                can_double_jump = False
                jump_anim = True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
            gun_x = player_x + 30
            gun_y = player_y + 38
            proj_rect = pygame.Rect(gun_x + 12, gun_y + 3 - projectile_height // 2,
                                   projectile_width, projectile_height)
            projectiles.append(proj_rect)
            shoot_anim_timer = SHOOT_ANIM_LENGTH
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
            reset_game()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m and game_over:
            main_menu()
            reset_game()

    if not game_over:
        keys = pygame.key.get_pressed()
        moving = False
        if keys[pygame.K_a]:
            player_x -= player_speed
            moving = True
        if keys[pygame.K_d]:
            player_x += player_speed
            moving = True

        player_vel_y += gravity
        player_y += player_vel_y

        if (moving or on_ground) and not jump_anim:
            run_anim_timer += 1
            if run_anim_timer >= RUN_ANIM_SPEED:
                run_anim_frame = (run_anim_frame + 1) % 2
                run_anim_timer = 0
        else:
            run_anim_frame = 0
            run_anim_timer = 0

        if shoot_anim_timer > 0:
            shoot_anim_timer -= 1

        if not on_ground:
            jump_anim = True
        else:
            jump_anim = False

        for plat in platforms:
            plat.x -= scroll_speed

        for enemy in enemies:
            enemy.x -= scroll_speed

        for explosion in explosions:
            for p in explosion.particles:
                p["pos"][0] -= scroll_speed

        if platforms and platforms[-1].x < WIDTH:
            y = random.randint(HEIGHT // 2, HEIGHT - platform_height - 50)
            new_plat = pygame.Rect(WIDTH + random.randint(50, 200), y, platform_width, platform_height)
            platforms.append(new_plat)
            if random.random() < 0.3:
                ex = new_plat.x + random.randint(0, new_plat.width - enemy_width)
                ey = new_plat.y - enemy_height
                enemies.append(pygame.Rect(ex, ey, enemy_width, enemy_height))

        platforms = [p for p in platforms if p.x + p.width > 0]
        enemies = [e for e in enemies if e.x + enemy_width > 0]

        on_ground = False
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        for plat in platforms:
            if player_rect.colliderect(plat) and player_vel_y > 0:
                player_y = plat.y - player_height
                player_vel_y = 0
                on_ground = True
                can_double_jump = True
                score += 1

        if player_y > HEIGHT:
            game_over = True
            if score > high_score:
                high_score = score

        for proj in projectiles:
            proj.x += projectile_speed

        projectiles = [p for p in projectiles if p.x < WIDTH]

        for proj in projectiles[:]:
            for enemy in enemies[:]:
                if proj.colliderect(enemy):
                    explosions.append(Explosion(enemy.x + enemy_width // 2, enemy.y + enemy_height // 2))
                    enemies.remove(enemy)
                    projectiles.remove(proj)
                    score += 5
                    break

        for enemy in enemies:
            if player_rect.colliderect(enemy):
                game_over = True
                if score > high_score:
                    high_score = score

        for explosion in explosions[:]:
            explosion.update()
            if not explosion.particles:
                explosions.remove(explosion)

    screen.fill((30, 30, 30))

    if not game_over:
        pygame.draw.rect(screen, (200, 0, 0), (player_x + 15, player_y + 20, 10, 30))
        pygame.draw.circle(screen, (255, 200, 200), (player_x + 20, player_y + 10), 10)
        if jump_anim:
            pygame.draw.line(screen, (200, 0, 0), (player_x + 15, player_y + 30), (player_x + 10, player_y + 15), 5)
            pygame.draw.line(screen, (200, 0, 0), (player_x + 25, player_y + 30), (player_x + 30, player_y + 38), 5)
            gun_x, gun_y = player_x + 30, player_y + 38
            pygame.draw.rect(screen, (80, 80, 80), (gun_x, gun_y, 12, 6))
            if shoot_anim_timer > 0:
                pygame.draw.rect(screen, (255, 255, 0), (gun_x + 12, gun_y + 2, 8, 2))
        elif run_anim_frame == 0:
            pygame.draw.line(screen, (200, 0, 0), (player_x + 15, player_y + 30), (player_x + 5, player_y + 50), 5)
            pygame.draw.line(screen, (200, 0, 0), (player_x + 25, player_y + 30), (player_x + 35, player_y + 50), 5)
            gun_x, gun_y = player_x + 30, player_y + 38
            pygame.draw.rect(screen, (80, 80, 80), (gun_x, gun_y, 12, 6))
            if shoot_anim_timer > 0:
                pygame.draw.rect(screen, (255, 255, 0), (gun_x + 12, gun_y + 2, 8, 2))
        else:
            pygame.draw.line(screen, (200, 0, 0), (player_x + 15, player_y + 30), (player_x + 10, player_y + 55), 5)
            pygame.draw.line(screen, (200, 0, 0), (player_x + 25, player_y + 30), (player_x + 40, player_y + 40), 5)
            gun_x, gun_y = player_x + 30, player_y + 38
            pygame.draw.rect(screen, (80, 80, 80), (gun_x, gun_y, 12, 6))
            if shoot_anim_timer > 0:
                pygame.draw.rect(screen, (255, 255, 0), (gun_x + 12, gun_y + 2, 8, 2))
        if jump_anim:
            pygame.draw.line(screen, (200, 0, 0), (player_x + 17, player_y + 50), (player_x + 17, player_y + 65), 5)
            pygame.draw.line(screen, (200, 0, 0), (player_x + 23, player_y + 50), (player_x + 23, player_y + 65), 5)
        elif run_anim_frame == 0:
            pygame.draw.line(screen, (200, 0, 0), (player_x + 17, player_y + 50), (player_x + 12, player_y + 60), 5)
            pygame.draw.line(screen, (200, 0, 0), (player_x + 23, player_y + 50), (player_x + 28, player_y + 60), 5)
        else:
            pygame.draw.line(screen, (200, 0, 0), (player_x + 17, player_y + 50), (player_x + 10, player_y + 65), 5)
            pygame.draw.line(screen, (200, 0, 0), (player_x + 23, player_y + 50), (player_x + 30, player_y + 65), 5)
    else:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((20, 20, 20))
        screen.blit(overlay, (0, 0))
        msg = font.render("Game Over! Press R to Restart", True, (255, 255, 0))
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 60))
        menu_msg = small_font.render("Press M to return to Main Menu", True, (255, 255, 255))
        screen.blit(menu_msg, (WIDTH // 2 - menu_msg.get_width() // 2, HEIGHT // 2 - 10))
        hs_msg = small_font.render(f"High Score: {high_score}", True, (255, 255, 255))
        screen.blit(hs_msg, (WIDTH // 2 - hs_msg.get_width() // 2, HEIGHT // 2 + 30))

    for plat in platforms:
        pygame.draw.rect(screen, (0, 200, 255), plat)

    for enemy in enemies:
        pygame.draw.rect(screen, (0, 255, 0), (enemy.x + 15, enemy.y + 20, 10, 30))
        pygame.draw.circle(screen, (200, 255, 200), (enemy.x + 20, enemy.y + 10), 10)
        pygame.draw.line(screen, (0, 255, 0), (enemy.x + 15, enemy.y + 30), (enemy.x + 5, enemy.y + 50), 5)
        pygame.draw.line(screen, (0, 255, 0), (enemy.x + 25, enemy.y + 30), (enemy.x + 35, enemy.y + 50), 5)
        pygame.draw.line(screen, (0, 255, 0), (enemy.x + 17, enemy.y + 50), (enemy.x + 12, enemy.y + 60), 5)
        pygame.draw.line(screen, (0, 255, 0), (enemy.x + 23, enemy.y + 50), (enemy.x + 28, enemy.y + 60), 5)

    for proj in projectiles:
        pygame.draw.rect(screen, (255, 255, 0), proj)

    for explosion in explosions:
        explosion.draw(screen)

    score_text = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(score_text, (20, 20))
    pygame.display.flip()
    clock.tick(60)
