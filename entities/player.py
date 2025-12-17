import pygame
import math
from entities.projectile import Projectile, ProjectileDirectional
from config import (SWORD_COLOR, SPEAR_COLOR, BOW_COLOR, STAFF_COLOR, FIREBALL_COLOR,
                    PLAYER_SPEED, PLAYER_JUMP_POWER, PLAYER_MAX_HEALTH,
                    SWORD_DAMAGE, SWORD_COOLDOWN, SWORD_RANGE,
                    SPEAR_DAMAGE, SPEAR_COOLDOWN, SPEAR_RANGE,
                    BOW_DAMAGE, BOW_COOLDOWN, ARROW_COLOR,
                    MAGIC_DAMAGE, MAGIC_COOLDOWN, MAGIC_MAX_DISTANCE,
                    GRAVITY, MAX_FALL_SPEED)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 40, 60)
        self.vel_x = 0
        self.vel_y = 0
        self.speed = PLAYER_SPEED
        self.jump_power = PLAYER_JUMP_POWER
        self.on_ground = False
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH

        self.weapon = 0
        self.weapon_names = ["Меч", "Копьё", "Лук", "Магия"]
        self.attack_cooldown = 0
        self.attack_animation = 0
        self.attack_range = 60
        self.facing_right = True

    def update(self, platforms, obstacles, mouse_pos, camera_offset):
        keys = pygame.key.get_pressed()

        # Направление для дальнобойного оружия (лук, магия) определяется курсором
        # Для ближнего боя (меч, копьё) - направлением движения
        if mouse_pos and self.weapon in [2, 3]:  # Лук или магия
            world_mouse_x = mouse_pos[0] + camera_offset
            if world_mouse_x > self.rect.centerx:
                self.facing_right = True
            else:
                self.facing_right = False

        self.vel_x = 0
        if keys[pygame.K_a]:
            self.vel_x = -self.speed
            # Для меча и копья поворачиваемся при движении
            if self.weapon in [0, 1]:
                self.facing_right = False
        if keys[pygame.K_d]:
            self.vel_x = self.speed
            if self.weapon in [0, 1]:
                self.facing_right = True

        if keys[pygame.K_w] and self.on_ground:
            self.vel_y = -self.jump_power
            self.on_ground = False

        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        self.rect.x += self.vel_x
        self.check_collision_x(platforms, obstacles)
        self.rect.y += self.vel_y
        self.check_collision_y(platforms, obstacles)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.attack_animation > 0:
            self.attack_animation -= 1

    def check_collision_x(self, platforms, obstacles):
        # Оптимизация: проверяем только близкие платформы
        # Для больших платформ проверяем перекрытие по X, а не расстояние до центра
        for platform in platforms:
            if (platform.rect.left - 200 <= self.rect.centerx <= platform.rect.right + 200):
                if self.rect.colliderect(platform.rect):
                    if self.vel_x > 0:
                        self.rect.right = platform.rect.left
                    elif self.vel_x < 0:
                        self.rect.left = platform.rect.right
        for obstacle in obstacles:
            if obstacle.obstacle_type == "wall":
                if (obstacle.rect.left - 200 <= self.rect.centerx <= obstacle.rect.right + 200):
                    if self.rect.colliderect(obstacle.rect):
                        if self.vel_x > 0:
                            self.rect.right = obstacle.rect.left
                        elif self.vel_x < 0:
                            self.rect.left = obstacle.rect.right

    def check_collision_y(self, platforms, obstacles):
        self.on_ground = False
        # Оптимизация: проверяем только близкие платформы
        # Для больших платформ проверяем перекрытие по X, а не расстояние до центра
        for platform in platforms:
            if (platform.rect.left - 200 <= self.rect.centerx <= platform.rect.right + 200):
                if self.rect.colliderect(platform.rect):
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:
                        self.rect.top = platform.rect.bottom
                        self.vel_y = 0
        for obstacle in obstacles:
            if obstacle.obstacle_type == "wall":
                if (obstacle.rect.left - 200 <= self.rect.centerx <= obstacle.rect.right + 200):
                    if self.rect.colliderect(obstacle.rect):
                        if self.vel_y > 0:
                            self.rect.bottom = obstacle.rect.top
                            self.vel_y = 0
                            self.on_ground = True
                        elif self.vel_y < 0:
                            self.rect.top = obstacle.rect.bottom
                            self.vel_y = 0
            # Шипы не создают коллизию - игрок проваливается сквозь них и умирает

    def attack(self, enemies, projectiles, mouse_pos, camera_offset):
        if self.attack_cooldown > 0:
            return
        self.attack_animation = 15

        # Меч и копьё бьют перед собой (не зависят от курсора)
        if self.weapon == 0:
            self.melee_attack(enemies, SWORD_DAMAGE, SWORD_RANGE)
            self.attack_cooldown = SWORD_COOLDOWN
        elif self.weapon == 1:
            self.melee_attack(enemies, SPEAR_DAMAGE, SPEAR_RANGE)
            self.attack_cooldown = SPEAR_COOLDOWN
        # Лук и магия стреляют в направлении курсора
        elif self.weapon in [2, 3]:
            world_mouse_x = mouse_pos[0] + camera_offset
            world_mouse_y = mouse_pos[1]
            dx = world_mouse_x - self.rect.centerx
            dy = world_mouse_y - self.rect.centery
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # Защита от деления на ноль
            if distance > 0.01:
                dir_x = dx / distance
                dir_y = dy / distance
            else:
                dir_x = 1 if self.facing_right else -1
                dir_y = 0

            if self.weapon == 2:
                self.ranged_attack_directional(projectiles, BOW_DAMAGE, ARROW_COLOR, "arrow", dir_x, dir_y, max_distance=None)
                self.attack_cooldown = BOW_COOLDOWN
            elif self.weapon == 3:
                self.ranged_attack_directional(projectiles, MAGIC_DAMAGE, FIREBALL_COLOR, "fireball", dir_x, dir_y, max_distance=MAGIC_MAX_DISTANCE)
                self.attack_cooldown = MAGIC_COOLDOWN

    def melee_attack(self, enemies, damage, attack_range):
        for enemy in enemies:
            dist = abs(self.rect.centerx - enemy.rect.centerx)
            if dist < attack_range and abs(self.rect.centery - enemy.rect.centery) < 50:
                if (self.facing_right and enemy.rect.centerx > self.rect.centerx) or \
                        (not self.facing_right and enemy.rect.centerx < self.rect.centerx):
                    enemy.take_damage(damage)

    def ranged_attack_directional(self, projectiles, damage, color, proj_type, dir_x, dir_y, max_distance=None):
        projectile = ProjectileDirectional(self.rect.centerx, self.rect.centery, dir_x, dir_y, damage, color, proj_type, max_distance)
        projectiles.add(projectile)

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def switch_weapon(self):
        self.weapon = (self.weapon + 1) % 4

    def draw(self, screen, camera_offset):
        x = self.rect.x - camera_offset
        y = self.rect.y
        body_color = (100, 120, 160)
        pygame.draw.rect(screen, body_color, (x + 12, y + 15, 16, 25))
        head_color = (130, 145, 170)
        pygame.draw.circle(screen, head_color, (x + 20, y + 10), 8)
        leg_color = (80, 95, 130)
        pygame.draw.rect(screen, leg_color, (x + 14, y + 40, 6, 20))
        pygame.draw.rect(screen, leg_color, (x + 20, y + 40, 6, 20))
        self.draw_weapon(screen, x, y)

    def _get_arm_position(self, x, y, angle_offset, facing_right):
        """Вычисляет позицию конца руки с оружием"""
        base_x = x + 28 if facing_right else x + 12
        direction = 1 if facing_right else -1
        arm_end_x = base_x + direction * int(15 * math.cos(math.radians(angle_offset)))
        arm_end_y = y + 25 + int(15 * math.sin(math.radians(angle_offset)))
        return base_x, y + 25, arm_end_x, arm_end_y

    def draw_weapon(self, screen, x, y):
        arm_color = (110, 125, 150)

        if self.facing_right:
            if self.weapon == 0:  # Меч - смотрит вверх, бьёт вниз перед собой
                # В покое: -90° (вертикально вверх)
                # При атаке: от -90° до 0° (вертикально вниз перед собой)
                angle = -90 + (90 * ((15 - self.attack_animation) / 15)) if self.attack_animation > 0 else -90
                # Рука тянется к мечу
                arm_end_x = x + 28 + int(10 * math.cos(math.radians(angle - 30)))
                arm_end_y = y + 20 + int(10 * math.sin(math.radians(angle - 30)))
                pygame.draw.line(screen, arm_color, (x + 28, y + 25), (arm_end_x, arm_end_y), 4)
                # Рукоять меча (15px)
                handle_end_x = arm_end_x + int(15 * math.cos(math.radians(angle)))
                handle_end_y = arm_end_y + int(15 * math.sin(math.radians(angle)))
                pygame.draw.line(screen, (100, 80, 60), (arm_end_x, arm_end_y), (handle_end_x, handle_end_y), 4)
                # Гарда меча
                guard_offset = 5
                guard_x1 = handle_end_x + int(guard_offset * math.cos(math.radians(angle + 90)))
                guard_y1 = handle_end_y + int(guard_offset * math.sin(math.radians(angle + 90)))
                guard_x2 = handle_end_x + int(guard_offset * math.cos(math.radians(angle - 90)))
                guard_y2 = handle_end_y + int(guard_offset * math.sin(math.radians(angle - 90)))
                pygame.draw.line(screen, (120, 110, 100), (guard_x1, guard_y1), (guard_x2, guard_y2), 3)
                # Лезвие меча (40px)
                blade_end_x = handle_end_x + int(40 * math.cos(math.radians(angle)))
                blade_end_y = handle_end_y + int(40 * math.sin(math.radians(angle)))
                pygame.draw.line(screen, SWORD_COLOR, (handle_end_x, handle_end_y), (blade_end_x, blade_end_y), 6)
                # Острие меча
                pygame.draw.line(screen, (220, 220, 240), (blade_end_x - 3, blade_end_y - 3), (blade_end_x, blade_end_y), 2)
            elif self.weapon == 1:  # Копьё - тычок вперед
                # Анимация копья: выдвижение вперед
                # attack_animation: 15->0, thrust: 0->30 (выдвигается при атаке)
                thrust_offset = 30 * ((15 - self.attack_animation) / 15) if self.attack_animation > 0 else 0
                arm_end_x = x + 28 + 5
                arm_end_y = y + 25
                pygame.draw.line(screen, arm_color, (x + 28, y + 25), (arm_end_x, arm_end_y), 4)
                # Древко копья (длинное)
                spear_length = 60 + thrust_offset
                spear_end_x = arm_end_x + spear_length
                spear_end_y = arm_end_y
                pygame.draw.line(screen, SPEAR_COLOR, (arm_end_x, arm_end_y), (spear_end_x, spear_end_y), 4)
                # Наконечник копья
                tip_x = spear_end_x + 12
                tip_y = spear_end_y
                pygame.draw.line(screen, (150, 150, 170), (spear_end_x, spear_end_y), (tip_x, tip_y), 5)
                pygame.draw.line(screen, (180, 180, 200), (spear_end_x, spear_end_y - 3), (tip_x, tip_y), 2)
                pygame.draw.line(screen, (180, 180, 200), (spear_end_x, spear_end_y + 3), (tip_x, tip_y), 2)
            elif self.weapon == 2:  # Лук
                angle_offset = -30 * (self.attack_animation / 15) if self.attack_animation > 0 else 0
                arm_end_x = x + 28 + int(15 * math.cos(math.radians(angle_offset)))
                arm_end_y = y + 25 + int(15 * math.sin(math.radians(angle_offset)))
                pygame.draw.line(screen, arm_color, (x + 28, y + 25), (arm_end_x, arm_end_y), 4)
                bow_x = arm_end_x + 10
                bow_y = arm_end_y
                pygame.draw.arc(screen, BOW_COLOR, (bow_x - 10, bow_y - 20, 20, 40), 0.5, 5.78, 3)
            elif self.weapon == 3:  # Магия
                angle_offset = -30 * (self.attack_animation / 15) if self.attack_animation > 0 else 0
                arm_end_x = x + 28 + int(15 * math.cos(math.radians(angle_offset)))
                arm_end_y = y + 25 + int(15 * math.sin(math.radians(angle_offset)))
                pygame.draw.line(screen, arm_color, (x + 28, y + 25), (arm_end_x, arm_end_y), 4)
                staff_end_x = arm_end_x + 35
                staff_end_y = arm_end_y
                pygame.draw.line(screen, STAFF_COLOR, (arm_end_x, arm_end_y), (staff_end_x, staff_end_y), 4)
                orb_size = 8 + (3 if self.attack_animation > 0 else 0)
                pygame.draw.circle(screen, FIREBALL_COLOR, (staff_end_x, staff_end_y), orb_size)
                pygame.draw.circle(screen, (255, 150, 80), (staff_end_x, staff_end_y), orb_size - 3)
            pygame.draw.line(screen, arm_color, (x + 12, y + 25), (x + 8, y + 35), 4)
        else:  # Facing left
            if self.weapon == 0:  # Меч - смотрит вверх, бьёт вниз перед собой
                # В покое: -90° (вертикально вверх)
                # При атаке: от -90° до 0° (вертикально вниз перед собой)
                angle = -90 + (90 * ((15 - self.attack_animation) / 15)) if self.attack_animation > 0 else -90
                arm_end_x = x + 12 - int(10 * math.cos(math.radians(angle - 30)))
                arm_end_y = y + 20 + int(10 * math.sin(math.radians(angle - 30)))
                pygame.draw.line(screen, arm_color, (x + 12, y + 25), (arm_end_x, arm_end_y), 4)
                # Рукоять меча
                handle_end_x = arm_end_x - int(15 * math.cos(math.radians(angle)))
                handle_end_y = arm_end_y + int(15 * math.sin(math.radians(angle)))
                pygame.draw.line(screen, (100, 80, 60), (arm_end_x, arm_end_y), (handle_end_x, handle_end_y), 4)
                # Гарда меча
                guard_offset = 5
                guard_x1 = handle_end_x - int(guard_offset * math.cos(math.radians(angle + 90)))
                guard_y1 = handle_end_y + int(guard_offset * math.sin(math.radians(angle + 90)))
                guard_x2 = handle_end_x - int(guard_offset * math.cos(math.radians(angle - 90)))
                guard_y2 = handle_end_y + int(guard_offset * math.sin(math.radians(angle - 90)))
                pygame.draw.line(screen, (120, 110, 100), (guard_x1, guard_y1), (guard_x2, guard_y2), 3)
                # Лезвие меча
                blade_end_x = handle_end_x - int(40 * math.cos(math.radians(angle)))
                blade_end_y = handle_end_y + int(40 * math.sin(math.radians(angle)))
                pygame.draw.line(screen, SWORD_COLOR, (handle_end_x, handle_end_y), (blade_end_x, blade_end_y), 6)
                pygame.draw.line(screen, (220, 220, 240), (blade_end_x + 3, blade_end_y - 3), (blade_end_x, blade_end_y), 2)
            elif self.weapon == 1:  # Копьё - тычок вперед
                # Инвертируем для правильного выдвижения
                thrust_offset = 30 * ((15 - self.attack_animation) / 15) if self.attack_animation > 0 else 0
                arm_end_x = x + 12 - 5
                arm_end_y = y + 25
                pygame.draw.line(screen, arm_color, (x + 12, y + 25), (arm_end_x, arm_end_y), 4)
                # Древко копья
                spear_length = 60 + thrust_offset
                spear_end_x = arm_end_x - spear_length
                spear_end_y = arm_end_y
                pygame.draw.line(screen, SPEAR_COLOR, (arm_end_x, arm_end_y), (spear_end_x, spear_end_y), 4)
                # Наконечник копья
                tip_x = spear_end_x - 12
                tip_y = spear_end_y
                pygame.draw.line(screen, (150, 150, 170), (spear_end_x, spear_end_y), (tip_x, tip_y), 5)
                pygame.draw.line(screen, (180, 180, 200), (spear_end_x, spear_end_y - 3), (tip_x, tip_y), 2)
                pygame.draw.line(screen, (180, 180, 200), (spear_end_x, spear_end_y + 3), (tip_x, tip_y), 2)
            elif self.weapon == 2:  # Лук
                angle_offset = -30 * (self.attack_animation / 15) if self.attack_animation > 0 else 0
                arm_end_x = x + 12 - int(15 * math.cos(math.radians(angle_offset)))
                arm_end_y = y + 25 + int(15 * math.sin(math.radians(angle_offset)))
                pygame.draw.line(screen, arm_color, (x + 12, y + 25), (arm_end_x, arm_end_y), 4)
                bow_x = arm_end_x - 20
                bow_y = arm_end_y
                pygame.draw.arc(screen, BOW_COLOR, (bow_x, bow_y - 20, 20, 40), 0.5, 5.78, 3)
            elif self.weapon == 3:  # Магия
                angle_offset = -30 * (self.attack_animation / 15) if self.attack_animation > 0 else 0
                arm_end_x = x + 12 - int(15 * math.cos(math.radians(angle_offset)))
                arm_end_y = y + 25 + int(15 * math.sin(math.radians(angle_offset)))
                pygame.draw.line(screen, arm_color, (x + 12, y + 25), (arm_end_x, arm_end_y), 4)
                staff_end_x = arm_end_x - 35
                staff_end_y = arm_end_y
                pygame.draw.line(screen, STAFF_COLOR, (arm_end_x, arm_end_y), (staff_end_x, staff_end_y), 4)
                orb_size = 8 + (3 if self.attack_animation > 0 else 0)
                pygame.draw.circle(screen, FIREBALL_COLOR, (staff_end_x, staff_end_y), orb_size)
                pygame.draw.circle(screen, (255, 150, 80), (staff_end_x, staff_end_y), orb_size - 3)
            pygame.draw.line(screen, arm_color, (x + 28, y + 25), (x + 32, y + 35), 4)