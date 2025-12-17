# entities/enemy.py - Полная версия с детальной графикой

import pygame
import random
from config import (
    ENEMY_COLOR, ENEMY_ARCHER_COLOR, ENEMY_TANK_COLOR,
    WARRIOR_SPEED, WARRIOR_HEALTH, WARRIOR_DAMAGE,
    ARCHER_SPEED, ARCHER_HEALTH, ARCHER_DAMAGE, ARCHER_SHOOT_COOLDOWN,
    TANK_SPEED, TANK_HEALTH, TANK_DAMAGE,
    ARROW_COLOR, GRAVITY, MAX_FALL_SPEED
)
from entities.projectile import Projectile


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="warrior"):
        super().__init__()
        self.enemy_type = enemy_type

        if enemy_type == "warrior":
            self.rect = pygame.Rect(x, y, 35, 50)
            self.color = ENEMY_COLOR
            self.vel_x = random.choice([-WARRIOR_SPEED, WARRIOR_SPEED])
            self.health = WARRIOR_HEALTH
            self.damage = WARRIOR_DAMAGE
        elif enemy_type == "archer":
            self.rect = pygame.Rect(x, y, 30, 45)
            self.color = ENEMY_ARCHER_COLOR
            self.vel_x = random.choice([-ARCHER_SPEED, ARCHER_SPEED])
            self.health = ARCHER_HEALTH
            self.damage = ARCHER_DAMAGE
            self.shoot_cooldown = 0
        elif enemy_type == "tank":
            self.rect = pygame.Rect(x, y, 45, 60)
            self.color = ENEMY_TANK_COLOR
            self.vel_x = random.choice([-TANK_SPEED, TANK_SPEED])
            self.health = TANK_HEALTH
            self.damage = TANK_DAMAGE

        self.vel_y = 0
        self.max_health = self.health
        self.attack_cooldown = 0
        self.facing_right = self.vel_x > 0

    def update(self, platforms, player, projectiles, obstacles):
        if self.enemy_type == "archer":
            if abs(self.rect.centerx - player.rect.centerx) < 200:
                if self.rect.centerx < player.rect.centerx:
                    self.vel_x = -2
                    self.facing_right = False
                else:
                    self.vel_x = 2
                    self.facing_right = True
            elif abs(self.rect.centerx - player.rect.centerx) < 400:
                self.vel_x = 0
                self.facing_right = player.rect.centerx > self.rect.centerx
                if self.shoot_cooldown == 0:
                    direction = 1 if player.rect.centerx > self.rect.centerx else -1
                    projectile = Projectile(self.rect.centerx, self.rect.centery, direction, self.damage, ARROW_COLOR,
                                            "arrow")
                    projectiles.add(projectile)
                    self.shoot_cooldown = ARCHER_SHOOT_COOLDOWN

            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1
        else:
            if abs(self.rect.centerx - player.rect.centerx) < 400:
                if self.rect.centerx < player.rect.centerx:
                    self.vel_x = abs(self.vel_x)
                    self.facing_right = True
                else:
                    self.vel_x = -abs(self.vel_x)
                    self.facing_right = False
            else:
                self.vel_x = random.choice([-1, 1]) if random.random() < 0.02 else self.vel_x
                self.facing_right = self.vel_x > 0

        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        self.rect.x += self.vel_x

        for obstacle in obstacles:
            if obstacle.obstacle_type == "wall" and self.rect.colliderect(obstacle.rect):
                if self.vel_x > 0:
                    self.rect.right = obstacle.rect.left
                    self.vel_x = -self.vel_x
                elif self.vel_x < 0:
                    self.rect.left = obstacle.rect.right
                    self.vel_x = -self.vel_x

        self.rect.y += self.vel_y

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0

        for obstacle in obstacles:
            if obstacle.obstacle_type == "wall" and self.rect.colliderect(obstacle.rect):
                if self.vel_y > 0:
                    self.rect.bottom = obstacle.rect.top
                    self.vel_y = 0

        if self.enemy_type != "archer":
            if self.rect.colliderect(player.rect) and self.attack_cooldown == 0:
                player.take_damage(self.damage)
                self.attack_cooldown = 60

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def draw(self, screen, camera_offset):
        x = self.rect.x - camera_offset
        y = self.rect.y

        if self.enemy_type == "warrior":
            # Рыцарь
            # Шлем
            pygame.draw.rect(screen, (100, 100, 110), (x + 10, y + 5, 15, 12))
            pygame.draw.rect(screen, (80, 80, 90), (x + 12, y + 8, 11, 8))

            # Тело в броне
            pygame.draw.rect(screen, (120, 120, 130), (x + 8, y + 17, 19, 20))
            pygame.draw.circle(screen, (100, 100, 110), (x + 12, y + 22), 4)
            pygame.draw.circle(screen, (100, 100, 110), (x + 23, y + 22), 4)

            # Щит
            if not self.facing_right:
                pygame.draw.ellipse(screen, (150, 80, 80), (x + 25, y + 18, 8, 16))
                pygame.draw.line(screen, (130, 60, 60), (x + 29, y + 20), (x + 29, y + 32), 2)

            # Руки
            pygame.draw.rect(screen, (110, 110, 120), (x + 5, y + 20, 5, 15))
            pygame.draw.rect(screen, (110, 110, 120), (x + 25, y + 20, 5, 15))

            # Меч в руке
            if self.facing_right:
                pygame.draw.line(screen, (180, 180, 200), (x + 30, y + 25), (x + 38, y + 15), 3)
                pygame.draw.rect(screen, (100, 80, 60), (x + 29, y + 26, 3, 5))
            else:
                pygame.draw.line(screen, (180, 180, 200), (x + 5, y + 25), (x - 3, y + 15), 3)
                pygame.draw.rect(screen, (100, 80, 60), (x + 3, y + 26, 3, 5))

            # Ноги
            pygame.draw.rect(screen, (100, 100, 110), (x + 10, y + 37, 6, 13))
            pygame.draw.rect(screen, (100, 100, 110), (x + 19, y + 37, 6, 13))

        elif self.enemy_type == "archer":
            # Волшебник-лучник
            # Капюшон
            pygame.draw.circle(screen, (80, 100, 70), (x + 15, y + 8), 8)
            pygame.draw.polygon(screen, (80, 100, 70), [
                (x + 7, y + 8),
                (x + 15, y + 2),
                (x + 23, y + 8)
            ])

            # Лицо
            pygame.draw.circle(screen, (120, 110, 100), (x + 15, y + 12), 5)

            # Мантия
            pygame.draw.polygon(screen, (90, 110, 80), [
                (x + 8, y + 18),
                (x + 15, y + 16),
                (x + 22, y + 18),
                (x + 20, y + 40),
                (x + 10, y + 40)
            ])

            # Руки
            pygame.draw.rect(screen, (100, 120, 90), (x + 5, y + 20, 4, 12))
            pygame.draw.rect(screen, (100, 120, 90), (x + 21, y + 20, 4, 12))

            # Лук
            if self.facing_right:
                pygame.draw.arc(screen, (100, 80, 60), (x + 22, y + 18, 12, 20), 0.5, 5.78, 2)
            else:
                pygame.draw.arc(screen, (100, 80, 60), (x - 4, y + 18, 12, 20), 3.64, 8.92, 2)

        elif self.enemy_type == "tank":
            # Тяжелый рыцарь
            # Большой шлем
            pygame.draw.rect(screen, (110, 110, 120), (x + 12, y + 3, 21, 15))
            pygame.draw.rect(screen, (70, 70, 80), (x + 15, y + 8, 15, 6))

            # Массивное тело
            pygame.draw.rect(screen, (130, 130, 140), (x + 8, y + 18, 29, 28))

            # Детали брони
            for i in range(3):
                pygame.draw.circle(screen, (100, 100, 110), (x + 15 + i * 7, y + 25), 3)

            # Плечи
            pygame.draw.circle(screen, (120, 120, 130), (x + 8, y + 20), 6)
            pygame.draw.circle(screen, (120, 120, 130), (x + 37, y + 20), 6)

            # Руки
            pygame.draw.rect(screen, (110, 110, 120), (x + 3, y + 24, 7, 18))
            pygame.draw.rect(screen, (110, 110, 120), (x + 35, y + 24, 7, 18))

            # Большой меч
            if self.facing_right:
                pygame.draw.line(screen, (160, 160, 180), (x + 42, y + 30), (x + 52, y + 10), 5)
                pygame.draw.rect(screen, (100, 80, 60), (x + 40, y + 32, 4, 8))
            else:
                pygame.draw.line(screen, (160, 160, 180), (x + 3, y + 30), (x - 7, y + 10), 5)
                pygame.draw.rect(screen, (100, 80, 60), (x + 1, y + 32, 4, 8))

            # Ноги
            pygame.draw.rect(screen, (110, 110, 120), (x + 12, y + 46, 9, 14))
            pygame.draw.rect(screen, (110, 110, 120), (x + 24, y + 46, 9, 14))

        # Полоска здоровья
        health_bar_width = self.rect.width
        health_percentage = self.health / self.max_health
        pygame.draw.rect(screen, (100, 50, 50), (x, y - 10, health_bar_width, 5))
        pygame.draw.rect(screen, (200, 80, 80), (x, y - 10, health_bar_width * health_percentage, 5))