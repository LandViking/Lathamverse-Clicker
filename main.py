import pygame
import sys
import time
from gamecore import GameCore

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LathamVerse")

font = pygame.font.SysFont("Arial", 18)
large_font = pygame.font.SysFont("Arial", 36)

def draw_text(text, font, color, x, y):
    text_obj = font.render(text, True, color)
    screen.blit(text_obj, (x, y))

def main_menu(core):
    menu_running = True
    continue_rect = pygame.Rect(300, 200, 200, 60)
    restart_rect = pygame.Rect(300, 300, 200, 60)

    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if continue_rect.collidepoint(event.pos):
                    core.load_game()
                    menu_running = False
                elif restart_rect.collidepoint(event.pos):
                    # Proceed without loading (starts fresh)
                    menu_running = False

        screen.fill((245, 245, 245))
        
        # Draw Continue Button
        pygame.draw.rect(screen, (150, 220, 150), continue_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), continue_rect, width=2, border_radius=10)
        draw_text("Continue", large_font, (0, 0, 0), 340, 210)
        
        # Draw Restart Button
        pygame.draw.rect(screen, (220, 150, 150), restart_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), restart_rect, width=2, border_radius=10)
        draw_text("Restart", large_font, (0, 0, 0), 350, 310)

        pygame.display.flip()

def main():
    core = GameCore()
    
    # Trigger the main menu before the core game loop starts
    main_menu(core)
    
    clock = pygame.time.Clock()
    last_time = time.time()

    # Pre-load and scale assets (added basic fallback if file is missing)
    try:
        clicker_image = pygame.image.load("assets/Dillon1.png").convert_alpha()
        clicker_image = pygame.transform.scale(clicker_image, (250, 250))
    except FileNotFoundError:
        clicker_image = pygame.Surface((250, 250))
        clicker_image.fill((100, 100, 200))
    
    clicker_rect = pygame.Rect(50, 150, 250, 250)
    ascend_rect = pygame.Rect(50, 450, 280, 60)
    
    running = True
    while running: 
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        core.idle(dt)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Save the game automatically when closing
                core.save_game()
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # Main Clicker Object
                if clicker_rect.collidepoint(mouse_pos):
                    core.click()
                elif ascend_rect.collidepoint(mouse_pos):
                    core.attempt_ascension()
                else:
                    y_offset = 100
                    for name in core.upgrades:
                        upgrade_rect = pygame.Rect(350, y_offset, 400, 60)
                        if upgrade_rect.collidepoint(mouse_pos):
                            core.attempt_purchase(name)
                        y_offset += 75
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    core.attempt_ascension()
                        
        screen.fill((245, 245, 245))
        
        # Draw Stats Text
        draw_text(f"Little Lathams: {core.player.little_lathams:.1f}", font, (20, 20, 20), 20, 20)
        draw_text(f"Click Lathams: {core.current_click_power:.1f}", font, (20, 20, 20), 20, 60)
        draw_text(f"Idle Lathams: {core.current_idle_power:.1f}/s", font, (20, 20, 20), 20, 85)
        draw_text(f"Ascensions: {core.player.ascensions} (Multiplier: x{core.player.ascensions_multiplier})", font, (20, 20, 20), 20, 110)                    
        
        # Draw Main Clicker
        screen.blit(clicker_image, (50, 150))
        
        # Draw Ascend Button
        can_ascend = core.player.little_lathams >= core.ascension_threshold
        ascend_color = (100, 255, 100) if can_ascend else (180, 180, 180)
        pygame.draw.rect(screen, ascend_color, ascend_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), ascend_rect, border_radius=10, width=2)
        draw_text(f"Ascend (A) Cost: {int(core.ascension_threshold)}", font, (0, 0, 0) if can_ascend else (100, 100, 100), 60, 465)
        
        # Draw Upgrades
        draw_text("Upgrades:", large_font, (20, 20, 20), 350, 50)
        y_offset = 100
        for name, upgrade in core.upgrades.items():
            upgrade_rect = pygame.Rect(350, y_offset, 400, 60)
            affordable = core.player.little_lathams >= upgrade.current_cost
            color = (150, 220, 150) if affordable else (220, 220, 220)
            
            pygame.draw.rect(screen, color, upgrade_rect, border_radius=8)
            pygame.draw.rect(screen, (0, 0, 0), upgrade_rect, width=1, border_radius=8)

            draw_text(f"{name} (Lvl {upgrade.level})", font, (0, 0, 0), 360, y_offset + 10)
            draw_text(f"Cost: {int(upgrade.current_cost)}", font, (50, 50, 50), 360, y_offset + 35)
            draw_text(f"+{upgrade.base_power} {upgrade.effect_type}", font, (50, 50, 50), 650, y_offset + 25)
            
            y_offset += 75

        # Refresh screen
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()