import pygame
import random
import math
from config import WIDTH, HEIGHT, BG_COLOR, FPS
from ui.menu import main_menu, settings_menu
from ui.hud import draw_ui, draw_background
from entities.player import Player
from entities.enemy import Enemy
from entities.projectile import Projectile, ProjectileDirectional
from world.platform import Platform
from world.obstacle import Obstacle
from world.door import Door
from world.background import BackgroundElement
from world.level_generator import generate_level

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Castle Roguelike")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)


# Камера
class Camera:
    def __init__(self):
        self.offset_x = 0

    def update(self, target):
        self.offset_x = target.rect.centerx - WIDTH // 3
        if self.offset_x < 0:
            self.offset_x = 0


# Игровой цикл
def game_loop():
    player = Player(100, HEIGHT - 150)
    level = 1
    platforms, enemies, door, level_length, obstacles, background_elements, theme = generate_level(level)
    projectiles = pygame.sprite.Group()
    camera = Camera()
    damage_cooldown = 0
    running = True
    volume = 0.5

    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    player.switch_weapon()
                elif event.key == pygame.K_e:
                    if door.active and player.rect.colliderect(door.rect):
                        level += 1
                        player.health = min(player.health + 20, player.max_health)
                        platforms, enemies, door, level_length, obstacles, background_elements, theme = generate_level(
                            level)
                        player.rect.topleft = (100, HEIGHT - 150)
                        camera.offset_x = 0
                        projectiles.empty()
                elif event.key == pygame.K_ESCAPE:
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.attack(enemies, projectiles, mouse_pos, camera.offset_x)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            player.attack(enemies, projectiles, mouse_pos, camera.offset_x)

        # Обновление объектов
        player.update(platforms, obstacles, mouse_pos, camera.offset_x)
        enemies.update(platforms, player, projectiles, obstacles)
        projectiles.update(enemies, obstacles)
        camera.update(player)
        door.active = len(enemies) == 0

        if damage_cooldown > 0:
            damage_cooldown -= 1

        # Оптимизация: проверяем только близкие шипы
        for obstacle in obstacles:
            if obstacle.obstacle_type == "spikes":
                if (obstacle.rect.left - 100 <= player.rect.centerx <= obstacle.rect.right + 100):
                    if player.rect.colliderect(obstacle.rect):
                        # Шипы убивают мгновенно
                        player.health = 0
                        break

        # Проверка смерти
        if player.health <= 0:
            screen.fill(BG_COLOR)
            game_over_text = font.render("ИГРА ОКОНЧЕНА", True, (200, 195, 210))
            restart_text = small_font.render("Нажми ESC для выхода в меню", True, (200, 195, 210))
            level_text = small_font.render(f"Достигнутый уровень: {level}", True, (200, 195, 210))
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))
            screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 - 10))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 30))
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return True
                clock.tick(FPS)

        # Рисование с culling (не рисуем объекты вне экрана)
        draw_background(screen, theme, camera.offset_x, WIDTH, HEIGHT)

        # Определяем границы видимой области с небольшим запасом
        visible_left = camera.offset_x - 100
        visible_right = camera.offset_x + WIDTH + 100

        for bg_element in background_elements:
            if visible_left <= bg_element.x <= visible_right:
                bg_element.draw(screen, camera.offset_x)

        for platform in platforms:
            if visible_left <= platform.rect.right and platform.rect.left <= visible_right:
                platform.draw(screen, camera.offset_x)

        for obstacle in obstacles:
            if visible_left <= obstacle.rect.right and obstacle.rect.left <= visible_right:
                obstacle.draw(screen, camera.offset_x)

        if visible_left <= door.rect.right and door.rect.left <= visible_right:
            door.draw(screen, camera.offset_x)

        player.draw(screen, camera.offset_x)

        for enemy in enemies:
            if visible_left <= enemy.rect.right and enemy.rect.left <= visible_right:
                enemy.draw(screen, camera.offset_x)

        for projectile in projectiles:
            if visible_left <= projectile.rect.right and projectile.rect.left <= visible_right:
                projectile.draw(screen, camera.offset_x)

        draw_ui(screen, player)

        # Уровень
        level_text = small_font.render(f"Уровень: {level}", True, (200, 195, 210))
        screen.blit(level_text, (WIDTH - 150, 20))

        # Курсор-прицел
        cursor_color = (200, 200, 220)
        pygame.draw.circle(screen, cursor_color, mouse_pos, 8, 2)
        pygame.draw.line(screen, cursor_color, (mouse_pos[0] - 12, mouse_pos[1]), (mouse_pos[0] - 4, mouse_pos[1]), 2)
        pygame.draw.line(screen, cursor_color, (mouse_pos[0] + 4, mouse_pos[1]), (mouse_pos[0] + 12, mouse_pos[1]), 2)
        pygame.draw.line(screen, cursor_color, (mouse_pos[0], mouse_pos[1] - 12), (mouse_pos[0], mouse_pos[1] - 4), 2)
        pygame.draw.line(screen, cursor_color, (mouse_pos[0], mouse_pos[1] + 4), (mouse_pos[0], mouse_pos[1] + 12), 2)

        pygame.display.flip()
        clock.tick(FPS)

    return True


def main():
    try:
        running = True
        volume = 0.5
        while running:
            start_game, volume = main_menu(screen, clock, font, small_font, volume)
            if not start_game:
                break
            running = game_loop()
    except pygame.error as e:
        print(f"Ошибка Pygame: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    finally:
        pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nИгра прервана пользователем")
        pygame.quit()