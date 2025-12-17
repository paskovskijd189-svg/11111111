import pygame


class BackgroundElement:
    def __init__(self, x, y, element_type, theme):
        self.x = x
        self.y = y
        self.element_type = element_type
        self.theme = theme

    def draw(self, screen, camera_offset):
        x = self.x - camera_offset

        if -200 < x < screen.get_width() + 200:
            if self.element_type == "window":
                pygame.draw.rect(screen, (40, 45, 60), (x, self.y, 60, 80))
                pygame.draw.rect(screen, (60, 80, 100), (x + 5, self.y + 5, 50, 70))
                pygame.draw.line(screen, (40, 45, 60), (x + 30, self.y + 5), (x + 30, self.y + 75), 3)
            elif self.element_type == "painting":
                pygame.draw.rect(screen, (80, 60, 50), (x, self.y, 70, 90))
                pygame.draw.rect(screen, (100, 80, 70), (x + 5, self.y + 5, 60, 80))
            elif self.element_type == "torch":
                pygame.draw.rect(screen, (50, 45, 40), (x, self.y, 8, 40))
                pygame.draw.circle(screen, (200, 100, 50), (x + 4, self.y - 5), 10)
