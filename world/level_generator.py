import pygame
import random
from world.platform import Platform
from world.obstacle import Obstacle
from world.door import Door
from world.background import BackgroundElement
from entities.enemy import Enemy

HEIGHT = 700


def generate_level(level_num):
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    background_elements = []

    level_length = 3000 + (level_num * 500)
    themes = ["castle", "roof", "dungeon"]
    theme = themes[(level_num - 1) % 3]

    platforms.add(Platform(0, HEIGHT - 50, level_length, 50))

    # Генерация платформ
    current_x = 300
    platform_data = []

    while current_x < level_length - 500:
        y = random.randint(HEIGHT - 350, HEIGHT - 150)
        width = random.randint(120, 250)
        platforms.add(Platform(current_x, y, width, 20))
        platform_data.append((current_x, y, width))

        gap = random.randint(100, 200)
        current_x += width + gap

        if random.random() < 0.3 and y > HEIGHT - 400:
            upper_y = y - random.randint(130, 170)
            upper_width = random.randint(100, 200)
            upper_x = current_x - width - 100
            if upper_y > 100:
                platforms.add(Platform(upper_x, upper_y, upper_width, 20))
                platform_data.append((upper_x, upper_y, upper_width))

    # Препятствия - привязаны к платформам
    for plat_x, plat_y, plat_w in platform_data:
        if random.random() < 0.4 and plat_y < HEIGHT - 100:
            # Стена на платформе
            wall_x = plat_x + random.randint(20, max(21, plat_w - 60))
            wall_height = random.randint(60, 100)
            obstacles.add(Obstacle(wall_x, plat_y - wall_height, 40, wall_height, "wall"))

    # Шипы на полу - ТОЛЬКО в свободных местах (не под платформами)
    def is_under_platform(x, platform_data):
        """Проверяет, находится ли точка под какой-либо платформой"""
        for plat_x, plat_y, plat_w in platform_data:
            if plat_x <= x <= plat_x + plat_w and plat_y < HEIGHT - 60:
                return True
        return False

    spike_x = 500
    while spike_x < level_length - 500:
        if random.random() < 0.3:
            # Проверяем, что шипы не под платформой
            if not is_under_platform(spike_x, platform_data):
                obstacles.add(Obstacle(spike_x, HEIGHT - 70, 80, 20, "spikes"))
        spike_x += random.randint(200, 400)

    # ОГРАНИЧИВАЮЩАЯ СТЕНА В КОНЦЕ УРОВНЯ
    obstacles.add(Obstacle(level_length - 80, 0, 80, HEIGHT, "wall"))

    # Фоновые элементы - размещаются осмысленно
    # 1. Элементы на стенах около платформ
    for plat_x, plat_y, plat_w in platform_data:
        if random.random() < 0.6:  # 60% платформ получают декор
            # Размещаем над платформой
            x = plat_x + random.randint(20, max(30, plat_w - 40))
            y = plat_y - random.randint(80, 120)
            if y > 50:  # Не слишком высоко
                elem_type = random.choice(["window", "painting", "torch"])
                background_elements.append(BackgroundElement(x, y, elem_type, theme))

    # 2. Элементы на уровне пола
    floor_x = 200
    while floor_x < level_length - 200:
        if random.random() < 0.3:  # 30% шанс
            # Размещаем на "стене" на уровне пола
            y = HEIGHT - random.randint(120, 180)
            elem_type = random.choice(["window", "painting", "torch"])
            background_elements.append(BackgroundElement(floor_x, y, elem_type, theme))
        floor_x += random.randint(300, 500)

    # Враги
    num_enemies = 5 + level_num * 2
    for i in range(num_enemies):
        x = random.randint(500, level_length - 300)
        y = 100
        enemy_type = random.choice(["warrior", "warrior", "archer", "tank"])
        enemies.add(Enemy(x, y, enemy_type))

    door = Door(level_length - 150, HEIGHT - 150)

    return platforms, enemies, door, level_length, obstacles, background_elements, theme