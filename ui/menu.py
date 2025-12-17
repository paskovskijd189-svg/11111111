import pygame

def main_menu(screen, clock, font, small_font, volume):
    menu_running = True
    selected = 0
    menu_items = ["Начать игру", "Настройки", "Выход"]

    while menu_running:
        screen.fill((25, 20, 30))
        mouse_pos = pygame.mouse.get_pos()

        # Заголовок
        title = font.render("CASTLE ROGUELIKE", True, (200, 195, 210))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 150))

        # Кнопки
        button_rects = []
        for i, item in enumerate(menu_items):
            text = font.render(item, True, (200, 195, 210))
            text_rect = text.get_rect(center=(screen.get_width() // 2, 300 + i * 70))
            button_rect = pygame.Rect(text_rect.x - 20, text_rect.y - 10, text_rect.width + 40, text_rect.height + 20)
            button_rects.append(button_rect)

            if button_rect.collidepoint(mouse_pos):
                color = (220, 215, 230)
            else:
                color = (200, 195, 210)

            pygame.draw.rect(screen, (80, 75, 90), button_rect, 2, border_radius=5)
            screen.blit(font.render(item, True, color), text_rect)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, volume
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        if i == 0:
                            return True, volume
                        elif i == 1:
                            volume = settings_menu(screen, clock, font, volume)
                        elif i == 2:
                            return False, volume
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_w, pygame.K_UP]:
                    selected = (selected - 1) % len(menu_items)
                elif event.key in [pygame.K_s, pygame.K_DOWN]:
                    selected = (selected + 1) % len(menu_items)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if selected == 0:
                        return True, volume
                    elif selected == 1:
                        volume = settings_menu(screen, clock, font, volume)
                    elif selected == 2:
                        return False, volume

        pygame.display.flip()
        clock.tick(60)
    return False, volume


def settings_menu(screen, clock, font, volume):
    settings_running = True

    while settings_running:
        screen.fill((25, 20, 30))

        # Заголовок
        title = font.render("НАСТРОЙКИ", True, (200, 195, 210))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 150))

        vol_text = font.render(f"Громкость: {int(volume * 100)}%", True, (200, 195, 210))
        screen.blit(vol_text, (screen.get_width() // 2 - vol_text.get_width() // 2, 300))

        hint = pygame.font.Font(None, 24).render("Используй A/D для изменения, ESC для выхода", True, (200, 195, 210))
        screen.blit(hint, (screen.get_width() // 2 - hint.get_width() // 2, 400))

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return volume
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    settings_running = False
                elif event.key == pygame.K_a:
                    volume = max(0, volume - 0.1)
                elif event.key == pygame.K_d:
                    volume = min(1, volume + 0.1)

        pygame.display.flip()
        clock.tick(60)

    return volume
