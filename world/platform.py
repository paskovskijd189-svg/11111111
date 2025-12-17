import pygame
from config import PLATFORM_COLOR, WIDTH


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen, camera_offset):
        x = self.rect.x - camera_offset
        pygame.draw.rect(screen, PLATFORM_COLOR, (x, self.rect.y, self.rect.width, self.rect.height))
