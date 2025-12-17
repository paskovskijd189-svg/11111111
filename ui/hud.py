import pygame
from config import UI_COLOR, TEXT_COLOR, WIDTH, HEIGHT

# Кешированный шрифт для оптимизации
_cached_font = None


def _get_font():
    global _cached_font
    if _cached_font is None:
        _cached_font = pygame.font.Font(None, 24)
    return _cached_font


def draw_ui(screen, player):
    # Панель здоровья
    pygame.draw.rect(screen, UI_COLOR, (20, 20, 204, 30))
    pygame.draw.rect(screen, (150, 50, 50), (22, 22, 200, 26))
    health_width = int((player.health / player.max_health) * 200)
    pygame.draw.rect(screen, (200, 80, 80), (22, 22, health_width, 26))

    # Текущее оружие
    font = _get_font()
    weapon_text = font.render(f"Оружие: {player.weapon_names[player.weapon]} [Q]", True, TEXT_COLOR)
    screen.blit(weapon_text, (20, 60))


def draw_background(screen, theme, camera_offset, WIDTH, HEIGHT):
    if theme == "castle":
        # Замок - тёмно-фиолетовый с каменной текстурой
        screen.fill((35, 30, 45))
        # Вертикальные "швы" между каменными блоками
        for i in range(0, WIDTH, 150):
            x = i - (camera_offset // 5) % 150
            pygame.draw.line(screen, (45, 40, 55), (x, 0), (x, HEIGHT), 2)
        # Горизонтальные швы
        for i in range(0, HEIGHT, 100):
            pygame.draw.line(screen, (45, 40, 55), (0, i), (WIDTH, i), 2)
        # Факелы на заднем плане (эффект мерцания)
        import random
        random.seed(int(camera_offset // 100))
        for i in range(5):
            x = (i * 300 + 100 - camera_offset // 4) % WIDTH
            y = 150
            flicker = random.randint(-2, 2)
            pygame.draw.circle(screen, (100, 60, 20), (x, y), 8 + flicker)
            pygame.draw.circle(screen, (180, 100, 40), (x, y), 5 + flicker)

    elif theme == "roof":
        # Терраса - ночное небо с луной и звёздами
        # Градиент неба от тёмно-синего вверху до светло-синего внизу
        for y in range(HEIGHT):
            color_intensity = int(30 + (y / HEIGHT) * 25)
            pygame.draw.line(screen, (color_intensity - 5, color_intensity, color_intensity + 20),
                           (0, y), (WIDTH, y))
        # Луна
        moon_x = WIDTH - 150
        moon_y = 80
        pygame.draw.circle(screen, (220, 220, 240), (moon_x, moon_y), 40)
        pygame.draw.circle(screen, (200, 200, 220), (moon_x + 10, moon_y - 5), 35)
        # Звёзды (больше и красивее)
        for i in range(50):
            star_x = (i * 137 + camera_offset // 3) % WIDTH
            star_y = (i * 73) % 250
            size = 1 if i % 3 == 0 else 2
            brightness = 220 if i % 4 == 0 else 180
            pygame.draw.circle(screen, (brightness, brightness, 230), (star_x, star_y), size)
        # Облака
        for i in range(3):
            cloud_x = (i * 400 + camera_offset // 6) % (WIDTH + 200) - 100
            cloud_y = 120 + i * 40
            pygame.draw.ellipse(screen, (50, 55, 70), (cloud_x, cloud_y, 120, 30))
            pygame.draw.ellipse(screen, (50, 55, 70), (cloud_x + 30, cloud_y - 10, 80, 30))

    else:  # dungeon
        # Подземелье - очень тёмное с зеленоватым оттенком
        screen.fill((15, 18, 20))
        # Трещины в стенах
        for i in range(0, WIDTH, 200):
            x = i - (camera_offset // 4) % 200
            y_start = (i * 17) % HEIGHT
            pygame.draw.line(screen, (25, 28, 25), (x, y_start), (x + 30, y_start + 80), 1)
            pygame.draw.line(screen, (25, 28, 25), (x + 30, y_start + 80), (x + 10, y_start + 150), 1)
        # Зеленоватое свечение снизу (магия/грибы)
        for y in range(HEIGHT - 100, HEIGHT):
            alpha = (y - (HEIGHT - 100)) / 100
            color_g = int(20 + alpha * 15)
            pygame.draw.line(screen, (10, color_g, 10), (0, y), (WIDTH, y), 1)
        # Паутина
        for i in range(3):
            web_x = (i * 350 + camera_offset // 8) % WIDTH
            web_y = 50 + i * 60
            pygame.draw.line(screen, (40, 40, 40), (web_x, web_y), (web_x + 60, web_y + 40), 1)
            pygame.draw.line(screen, (40, 40, 40), (web_x + 60, web_y), (web_x, web_y + 40), 1)
