import pygame
from config import OBSTACLE_COLOR, SPIKE_COLOR


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, obstacle_type="wall"):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.obstacle_type = obstacle_type

    def draw(self, screen, camera_offset):
        x = self.rect.x - camera_offset

        if self.obstacle_type == "wall":
            pygame.draw.rect(screen, OBSTACLE_COLOR, (x, self.rect.y, self.rect.width, self.rect.height))
            for i in range(0, self.rect.height, 20):
                for j in range(0, self.rect.width, 30):
                    pygame.draw.rect(screen, (70, 60, 75), (x + j + 1, self.rect.y + i + 1, 28, 18), 1)
        elif self.obstacle_type == "spikes":
            pygame.draw.rect(screen, SPIKE_COLOR, (x, self.rect.y + 10, self.rect.width, 10))
            for i in range(0, self.rect.width, 20):
                pygame.draw.polygon(screen, SPIKE_COLOR, [
                    (x + i, self.rect.y + 10),
                    (x + i + 10, self.rect.y),
                    (x + i + 20, self.rect.y + 10)
                ])
