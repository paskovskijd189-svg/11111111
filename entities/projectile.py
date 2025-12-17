import pygame
import math


class ProjectileDirectional(pygame.sprite.Sprite):
    def __init__(self, x, y, dir_x, dir_y, damage, color, proj_type, max_distance=None):
        super().__init__()
        self.proj_type = proj_type
        self.rect = pygame.Rect(x, y, 15, 15)
        speed = 12
        self.vel_x = speed * dir_x
        self.vel_y = speed * dir_y
        self.damage = damage
        self.color = color
        self.lifetime = 150
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.start_x = x
        self.start_y = y
        self.max_distance = max_distance
        # Для стрел добавляем гравитацию
        self.has_gravity = (proj_type == "arrow")

    def update(self, enemies, obstacles):
        # Гравитация для стрел (баллистика) - УВЕЛИЧЕНА
        if self.has_gravity:
            self.vel_y += 0.7  # Увеличенная гравитация для более выраженной дуги

        # Сохраняем старую позицию для проверки коллизий
        old_x = self.rect.x
        old_y = self.rect.y

        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.lifetime -= 1

        # Проверка максимальной дальности (для магии)
        if self.max_distance is not None:
            distance_traveled = math.sqrt((self.rect.x - self.start_x) ** 2 + (self.rect.y - self.start_y) ** 2)
            if distance_traveled > self.max_distance:
                self.kill()
                return

        if self.lifetime <= 0:
            self.kill()
            return

        # УЛУЧШЕННАЯ проверка столкновения с препятствиями (не проходят сквозь стены)
        for obstacle in obstacles:
            if obstacle.obstacle_type == "wall":
                # Проверяем как текущую позицию, так и траекторию
                if self.rect.colliderect(obstacle.rect):
                    self.kill()
                    return
                # Дополнительная проверка: если снаряд пересек стену между кадрами
                if self._line_intersects_rect(old_x, old_y, self.rect.x, self.rect.y, obstacle.rect):
                    self.kill()
                    return

        # Проверка столкновения с врагами
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage(self.damage)
                self.kill()
                break

    def _line_intersects_rect(self, x1, y1, x2, y2, rect):
        """Проверяет, пересекает ли линия от (x1,y1) до (x2,y2) прямоугольник"""
        # Простая проверка: если снаряд прошел через стену между кадрами
        # Проверяем, пересекла ли траектория границы rect
        if x1 < rect.left and x2 > rect.right:
            return True
        if x1 > rect.right and x2 < rect.left:
            return True
        if y1 < rect.top and y2 > rect.bottom:
            return True
        if y1 > rect.bottom and y2 < rect.top:
            return True
        return False

    def draw(self, screen, camera_offset):
        x = self.rect.x - camera_offset
        y = self.rect.y

        if self.proj_type == "fireball":
            pygame.draw.circle(screen, self.color, (x + 7, y + 7), 8)
            pygame.draw.circle(screen, (255, 150, 80), (x + 7, y + 7), 5)
        else:  # Стрела - вращается по направлению полета
            # Вычисляем угол на основе текущей скорости (с учетом гравитации)
            angle = math.atan2(self.vel_y, self.vel_x)
            end_x = x + int(15 * math.cos(angle))
            end_y = y + 7 + int(15 * math.sin(angle))
            # Древко стрелы
            pygame.draw.line(screen, self.color, (x, y + 7), (end_x, end_y), 3)
            # Наконечник стрелы
            tip_x = end_x + int(5 * math.cos(angle))
            tip_y = end_y + int(5 * math.sin(angle))
            pygame.draw.line(screen, (180, 180, 200), (end_x, end_y), (tip_x, tip_y), 4)


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, damage, color, proj_type):
        super().__init__()
        self.proj_type = proj_type
        self.rect = pygame.Rect(x, y, 15, 8)
        self.vel_x = 10 * direction
        self.damage = damage
        self.color = color
        self.lifetime = 150
        self.direction = direction

    def update(self, enemies, obstacles):
        self.rect.x += self.vel_x
        self.lifetime -= 1

        if self.lifetime <= 0:
            self.kill()
            return

        for obstacle in obstacles:
            if obstacle.obstacle_type == "wall" and self.rect.colliderect(obstacle.rect):
                self.kill()
                return

        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage(self.damage)
                self.kill()
                break

    def draw(self, screen, camera_offset):
        x = self.rect.x - camera_offset
        y = self.rect.y

        end_x = x + (15 if self.direction > 0 else 0)
        pygame.draw.line(screen, self.color, (x, y + 4), (end_x, y + 4), 3)
