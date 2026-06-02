import pygame
import sys
import time
import random
from gamecore import GameCore

pygame.init()
pygame.mixer.init() 

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LathamVerse")

font = pygame.font.SysFont("Arial", 18)
large_font = pygame.font.SysFont("Arial", 36)

class Particle:
    """Handles individual particles for the click explosion effect."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # MASSIVELY increased velocity spread for an intense explosion
        self.vx = random.uniform(-30, 30)
        self.vy = random.uniform(-30, 30)
        self.lifetime = random.randint(30, 60)
        self.color = random.choice([(255, 165, 0), (255, 69, 0), (255, 215, 0), (220, 50, 50), (255, 255, 200)])
        # Much larger particles
        self.radius = random.randint(6, 18)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.radius = max(0, self.radius - 0.25) 

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

def draw_text(text, font, color, x, y):
    text_obj = font.render(text, True, color)
    screen.blit(text_obj, (x, y))

def format_time(seconds):
    """Formats raw seconds into a readable HH:MM:SS format."""
    hrs, rem = divmod(seconds, 3600)
    mins, secs = divmod(rem, 60)
    return f"{int(hrs)}h {int(mins)}m {int(secs)}s"

def main_menu(core) -> bool:
    """Returns True if the game was loaded, False if starting fresh/restarted."""
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
                    loaded = core.load_game()
                    return loaded
                elif restart_rect.collidepoint(event.pos):
                    return False

        screen.fill((245, 245, 245))
        
        pygame.draw.rect(screen, (150, 220, 150), continue_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), continue_rect, width=2, border_radius=10)
        draw_text("Continue", large_font, (0, 0, 0), 340, 210)
        
        pygame.draw.rect(screen, (220, 150, 150), restart_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), restart_rect, width=2, border_radius=10)
        draw_text("Restart", large_font, (0, 0, 0), 350, 310)

        pygame.display.flip()

def main():
    core = GameCore()
    
    # Track if we successfully loaded a game
    was_loaded = main_menu(core)
    
    # If loaded and time has passed, trigger the popup
    show_offline_popup = was_loaded and core.offline_time_seconds > 0
    close_popup_btn = pygame.Rect(300, 350, 200, 50)
    
    clock = pygame.time.Clock()
    last_time = time.time()

    try:
        clicker_image = pygame.image.load("assets/Dillon1.png").convert_alpha()
        clicker_image = pygame.transform.scale(clicker_image, (250, 250))
    except FileNotFoundError:
        clicker_image = pygame.Surface((250, 250))
        clicker_image.fill((100, 100, 200))

    try:
        foxy_image = pygame.image.load("assets/foxy.gif").convert_alpha()
        foxy_image = pygame.transform.scale(foxy_image, (WIDTH, HEIGHT))
        jumpscare_sound = pygame.mixer.Sound("assets/jumpscare.wav")
    except FileNotFoundError:
        foxy_image = None
        jumpscare_sound = None
    
    clicker_rect = pygame.Rect(50, 150, 250, 250)
    ascend_rect = pygame.Rect(50, 450, 280, 60)
    
    particles = []
    bounces = {}
    bounce_frames = 4  
    jumpscare_timer = 0 
    
    running = True
    while running: 
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Only process idle time if the popup is NOT showing
        if not show_offline_popup:
            core.idle(dt)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                core.save_game()
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                # --- OFFLINE POPUP LOGIC ---
                if show_offline_popup:
                    if close_popup_btn.collidepoint(mouse_pos):
                        show_offline_popup = False
                        # Reset last_time to prevent a sudden burst of idle generation after closing the menu
                        last_time = time.time() 
                    continue # Ignore all other clicks while popup is active

                # --- JUMPSCARE LOGIC (1 in 1000 chance) ---
                if random.randint(1, 1000) == 1:
                    jumpscare_timer = 60  
                    if jumpscare_sound:
                        jumpscare_sound.play()
                
                # --- INTENSE EXPLOSION (1 in 25 chance) ---
                if random.randint(1, 1) == 1:
                    # Spawn 300 particles for a massive burst
                    for _ in range(300):
                        particles.append(Particle(mouse_pos[0], mouse_pos[1]))
                
                # Main Clicker Object
                if clicker_rect.collidepoint(mouse_pos):
                    if core.click(): 
                        bounces["clicker"] = bounce_frames
                elif ascend_rect.collidepoint(mouse_pos):
                    core.attempt_ascension()
                    bounces["ascend"] = bounce_frames
                else:
                    y_offset = 100
                    for name in core.upgrades:
                        upgrade_rect = pygame.Rect(350, y_offset, 400, 60)
                        if upgrade_rect.collidepoint(mouse_pos):
                            core.attempt_purchase(name)
                            bounces[f"upg_{name}"] = bounce_frames
                        y_offset += 75
                        
            if event.type == pygame.KEYDOWN and not show_offline_popup:
                if event.key == pygame.K_a:
                    core.attempt_ascension()
                    bounces["ascend"] = bounce_frames
                        
        # --- UPDATE ANIMATIONS ---
        if not show_offline_popup:
            for p in particles[:]:
                p.update()
                if p.lifetime <= 0:
                    particles.remove(p)
                    
            for key in list(bounces.keys()):
                if bounces[key] > 0:
                    bounces[key] -= 1

            if jumpscare_timer > 0:
                jumpscare_timer -= 1

        # --- DRAWING ---
        screen.fill((245, 245, 245))
        
        draw_text(f"Little Lathams: {core.player.little_lathams:.1f}", font, (20, 20, 20), 20, 20)
        draw_text(f"Click Lathams: {core.current_click_power:.1f}", font, (20, 20, 20), 20, 60)
        draw_text(f"Idle Lathams: {core.current_idle_power:.1f}/s", font, (20, 20, 20), 20, 85)
        draw_text(f"Ascensions: {core.player.ascensions} (Multiplier: x{core.player.ascensions_multiplier})", font, (20, 20, 20), 20, 110)                    
        
        if bounces.get("clicker", 0) > 0:
            scaled_clicker = pygame.transform.scale(clicker_image, (230, 230))
            screen.blit(scaled_clicker, (60, 160)) 
        else:
            screen.blit(clicker_image, (50, 150))
        
        current_ascend_rect = ascend_rect.copy()
        text_offset = 0
        if bounces.get("ascend", 0) > 0:
            current_ascend_rect = current_ascend_rect.inflate(-8, -8)
            text_offset = 4 
            
        can_ascend = core.player.little_lathams >= core.ascension_threshold
        ascend_color = (100, 255, 100) if can_ascend else (180, 180, 180)
        pygame.draw.rect(screen, ascend_color, current_ascend_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), current_ascend_rect, border_radius=10, width=2)
        draw_text(f"Ascend (A) Cost: {int(core.ascension_threshold)}", font, (0, 0, 0) if can_ascend else (100, 100, 100), 60 + text_offset, 465 + text_offset)
        
        draw_text("Upgrades:", large_font, (20, 20, 20), 350, 50)
        y_offset = 100
        for name, upgrade in core.upgrades.items():
            upgrade_rect = pygame.Rect(350, y_offset, 400, 60)
            current_upg_rect = upgrade_rect.copy()
            text_offset = 0
            
            if bounces.get(f"upg_{name}", 0) > 0:
                current_upg_rect = current_upg_rect.inflate(-8, -8)
                text_offset = 4

            affordable = core.player.little_lathams >= upgrade.current_cost
            color = (150, 220, 150) if affordable else (220, 220, 220)
            
            pygame.draw.rect(screen, color, current_upg_rect, border_radius=8)
            pygame.draw.rect(screen, (0, 0, 0), current_upg_rect, width=1, border_radius=8)

            draw_text(f"{name} (Lvl {upgrade.level})", font, (0, 0, 0), 360 + text_offset, y_offset + 10 + text_offset)
            draw_text(f"Cost: {int(upgrade.current_cost)}", font, (50, 50, 50), 360 + text_offset, y_offset + 35 + text_offset)
            draw_text(f"+{upgrade.base_power} {upgrade.effect_type}", font, (50, 50, 50), 650 + text_offset, y_offset + 25 + text_offset)
            
            y_offset += 75

        for p in particles:
            p.draw(screen)

        if jumpscare_timer > 0 and foxy_image:
            screen.blit(foxy_image, (0, 0))

        # --- DRAW OFFLINE PROGRESS POPUP ---
        if show_offline_popup:
            # Dim the background
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Draw popup box
            popup_rect = pygame.Rect(200, 150, 400, 300)
            pygame.draw.rect(screen, (245, 245, 245), popup_rect, border_radius=15)
            pygame.draw.rect(screen, (50, 50, 50), popup_rect, width=4, border_radius=15)
            
            # Draw popup text
            draw_text("Welcome Back!", large_font, (0, 0, 0), 280, 170)
            
            time_str = format_time(core.offline_time_seconds)
            draw_text(f"Time Away: {time_str}", font, (50, 50, 50), 230, 240)
            draw_text(f"Lathams Gained: {core.offline_lathams_gained:.1f}", font, (50, 50, 50), 230, 280)
            
            # Draw "Awesome" dismiss button
            pygame.draw.rect(screen, (150, 220, 150), close_popup_btn, border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), close_popup_btn, width=2, border_radius=10)
            draw_text("Awesome!", font, (0, 0, 0), 365, 365)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()