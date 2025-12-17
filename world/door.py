import pygame
from config import DOOR_COLOR, TEXT_COLOR

# Кешированный шрифт для оптимизации
_cached_font = None


def _get_font():
    global _cached_font
    if _cached_font is None:
        _cached_font = pygame.font.Font(None, 24)
    return _cached_font


class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 60, 100)
        self.active = False

    def draw(self, screen, camera_offset):
        x = self.rect.x - camera_offset
        color = (120, 150, 100) if self.active else DOOR_COLOR
        pygame.draw.rect(screen, color, (x, self.rect.y, self.rect.width, self.rect.height))
        pygame.draw.rect(screen, (80, 100, 70), (x + 5, self.rect.y + 5, self.rect.width - 10, self.rect.height - 10),
                         3)

        if self.active:
            font = _get_font()
            text = font.render("E", True, TEXT_COLOR)
            screen.blit(text, (x + 20, self.rect.y - 30))