import pygame
import sys
import time
import random
import math
import os
from gamecore import GameCore, MAX_OFFLINE_SECONDS

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LathamVerse")

# --- COLOR PALETTE ---
# Warm dark theme - less generic, more personality
BG_DARK = (18, 18, 24)
BG_MID = (26, 27, 35)
PANEL_BG = (32, 34, 44)
PANEL_BG_ALT = (28, 30, 40)
CARD_BG = (38, 40, 52)
CARD_BG_HOVER = (48, 50, 65)
CARD_BG_AFFORDABLE = (40, 48, 55)

TEXT_WHITE = (240, 238, 230)
TEXT_LIGHT = (200, 196, 188)
TEXT_DIM = (130, 128, 122)
TEXT_DARK = (80, 78, 74)

# Accent colors - curated, not generic
TEAL = (60, 210, 180)
TEAL_DIM = (35, 120, 100)
AMBER = (245, 180, 60)
AMBER_DIM = (160, 115, 35)
VIOLET = (140, 90, 235)
VIOLET_DIM = (90, 55, 155)
CORAL = (235, 95, 85)
CORAL_DIM = (150, 55, 50)
LIME = (160, 230, 80)

# UI colors
DIVIDER = (50, 52, 64)
CARD_BORDER = (55, 57, 70)
SHADOW = (10, 10, 16)

# --- FONTS ---
font_sm = pygame.font.SysFont("Helvetica", 12)
font_body = pygame.font.SysFont("Helvetica", 14)
font_body_b = pygame.font.SysFont("Helvetica", 14, bold=True)
font_md = pygame.font.SysFont("Helvetica", 16)
font_md_b = pygame.font.SysFont("Helvetica", 16, bold=True)
font_lg = pygame.font.SysFont("Helvetica", 22, bold=True)
font_xl = pygame.font.SysFont("Helvetica", 30, bold=True)
font_title = pygame.font.SysFont("Georgia", 42, bold=True)
font_subtitle = pygame.font.SysFont("Georgia", 16, italic=True)



# Pre-generate a subtle noise texture for the background
def make_noise_texture(w, h, intensity=6):
    """Creates a subtle noise overlay to break up flat colors."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    # Sparse noise - only some pixels
    for _ in range(w * h // 8):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        v = random.randint(-intensity, intensity)
        a = random.randint(10, 30)
        c = (128 + v, 128 + v, 128 + v, a)
        surf.set_at((x, y), c)
    return surf

noise_texture = make_noise_texture(WIDTH, HEIGHT, 8)


class Particle:
    """Click explosion particle with varied shapes."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 12)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = random.randint(15, 35)
        self.max_life = self.lifetime
        self.color = random.choice([TEAL, AMBER, VIOLET, LIME, (255, 220, 140)])
        self.radius = random.uniform(2, 7)
        self.shape = random.choice(["circle", "circle", "square"])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.25
        self.vx *= 0.98
        self.lifetime -= 1
        self.radius = max(0, self.radius - 0.15)

    def draw(self, surface):
        if self.lifetime > 0 and self.radius > 0:
            progress = self.lifetime / self.max_life
            alpha = max(0, min(255, int(255 * progress)))
            r = int(self.radius)
            if r < 1:
                return
            sz = r * 2 + 2
            s = pygame.Surface((sz, sz), pygame.SRCALPHA)
            col = (*self.color[:3], alpha)
            if self.shape == "square":
                pygame.draw.rect(s, col, (1, 1, r * 2, r * 2))
            else:
                pygame.draw.circle(s, col, (r + 1, r + 1), r)
            surface.blit(s, (int(self.x - r - 1), int(self.y - r - 1)))


class FloatingText:
    """Floating damage/income numbers with scale-in effect."""
    def __init__(self, x, y, text, color=AMBER):
        self.x = x + random.randint(-15, 15)
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = 45
        self.max_life = 45
        self.vy = -1.8
        self.scale = 1.5  # Start big, shrink to normal

    def update(self):
        self.y += self.vy
        self.vy *= 0.96
        self.lifetime -= 1
        self.scale = max(1.0, self.scale - 0.04)

    def draw(self, surface):
        if self.lifetime > 0:
            progress = self.lifetime / self.max_life
            alpha = max(0, min(255, int(255 * progress)))
            sz = max(12, int(14 * self.scale))
            f = pygame.font.SysFont("Helvetica", sz, bold=True)
            text_surf = f.render(self.text, True, self.color)
            text_surf.set_alpha(alpha)
            surface.blit(text_surf, (int(self.x - text_surf.get_width() // 2), int(self.y)))


def draw_text(text, f, color, x, y):
    """Draw text at position."""
    obj = f.render(text, True, color)
    screen.blit(obj, (x, y))


def draw_text_centered(text, f, color, cx, cy):
    """Draw text centered on a point."""
    obj = f.render(text, True, color)
    screen.blit(obj, (cx - obj.get_width() // 2, cy - obj.get_height() // 2))


def draw_text_right(text, f, color, rx, y):
    """Draw text right-aligned."""
    obj = f.render(text, True, color)
    screen.blit(obj, (rx - obj.get_width(), y))


def format_number(n):
    """Format large numbers with suffixes."""
    if n < 1000:
        return f"{n:.1f}"
    elif n < 1_000_000:
        return f"{n/1000:.1f}K"
    elif n < 1_000_000_000:
        return f"{n/1_000_000:.2f}M"
    else:
        return f"{n/1_000_000_000:.2f}B"


def format_time(seconds):
    """Formats raw seconds into a readable HH:MM:SS format."""
    hrs, rem = divmod(seconds, 3600)
    mins, secs = divmod(rem, 60)
    return f"{int(hrs)}h {int(mins)}m {int(secs)}s"


def draw_panel(surface, rect, color=PANEL_BG, radius=6):
    """Draw a panel with a subtle top-highlight edge."""
    # Shadow
    shadow_rect = rect.inflate(0, 0).move(2, 2)
    shadow_s = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_s, (0, 0, 0, 40), shadow_s.get_rect(), border_radius=radius)
    surface.blit(shadow_s, shadow_rect.topleft)
    # Main panel
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    # Top highlight line
    if rect.width > 20:
        hl_rect = pygame.Rect(rect.x + 8, rect.y, rect.width - 16, 1)
        hl_s = pygame.Surface((hl_rect.width, 1), pygame.SRCALPHA)
        hl_s.fill((255, 255, 255, 15))
        surface.blit(hl_s, hl_rect.topleft)


def draw_card(surface, rect, accent_color=None, hover=False, bounce=False, radius=5):
    """Draw an upgrade card with a left accent strip."""
    actual = rect.inflate(-4, -4) if bounce else rect
    bg = CARD_BG_HOVER if hover else CARD_BG
    pygame.draw.rect(surface, bg, actual, border_radius=radius)
    # Left accent strip
    if accent_color:
        strip_rect = pygame.Rect(actual.x, actual.y + 3, 3, actual.height - 6)
        pygame.draw.rect(surface, accent_color, strip_rect, border_radius=2)
    return actual


def draw_progress_bar(surface, x, y, w, h, progress, fill_color, bg_color=(22, 23, 30)):
    """Draw a minimal progress bar with rounded ends."""
    bar = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, bg_color, bar, border_radius=h // 2)
    if progress > 0:
        fw = max(h, int(w * min(1.0, progress)))
        fill = pygame.Rect(x, y, fw, h)
        pygame.draw.rect(surface, fill_color, fill, border_radius=h // 2)
        # Shine on top half
        shine = pygame.Surface((fw, h // 2), pygame.SRCALPHA)
        shine.fill((255, 255, 255, 20))
        surface.blit(shine, (x, y))


def draw_bg_grid(surface, time_val):
    """Draw a subtle animated dot grid in the background."""
    spacing = 40
    for gx in range(0, WIDTH + spacing, spacing):
        for gy in range(0, HEIGHT + spacing, spacing):
            # Subtle wave offset
            offset = math.sin(time_val * 0.3 + gx * 0.02 + gy * 0.015) * 2
            brightness = int(28 + offset)
            brightness = max(20, min(36, brightness))
            pygame.draw.circle(surface, (brightness, brightness, brightness + 4), (gx, gy), 1)


def main_menu(core) -> bool:
    """Main menu screen. Returns True if game was loaded, False if new game."""
    continue_rect = pygame.Rect(WIDTH // 2 - 130, 310, 260, 52)
    restart_rect = pygame.Rect(WIDTH // 2 - 130, 380, 260, 52)

    clock = pygame.time.Clock()
    t = 0.0

    # Background floating dots
    bg_dots = []
    for _ in range(40):
        bg_dots.append({
            "x": random.uniform(0, WIDTH),
            "y": random.uniform(0, HEIGHT),
            "vx": random.uniform(-0.3, 0.3),
            "vy": random.uniform(-0.2, -0.05),
            "r": random.uniform(1.5, 4),
            "color": random.choice([TEAL, AMBER, VIOLET]),
            "alpha": random.randint(15, 50),
        })

    while True:
        dt = clock.tick(60) / 1000.0
        t += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if continue_rect.collidepoint(event.pos):
                    return core.load_game()
                elif restart_rect.collidepoint(event.pos):
                    return False

        screen.fill(BG_DARK)

        # Animated background dots
        for d in bg_dots:
            d["x"] += d["vx"]
            d["y"] += d["vy"]
            if d["y"] < -10:
                d["y"] = HEIGHT + 10
                d["x"] = random.uniform(0, WIDTH)
            if d["x"] < -10 or d["x"] > WIDTH + 10:
                d["x"] = random.uniform(0, WIDTH)
            s = pygame.Surface((int(d["r"] * 2 + 2), int(d["r"] * 2 + 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*d["color"][:3], d["alpha"]), (int(d["r"] + 1), int(d["r"] + 1)), int(d["r"]))
            screen.blit(s, (int(d["x"] - d["r"]), int(d["y"] - d["r"])))

        # Title
        title_surf = font_title.render("LathamVerse", True, TEXT_WHITE)
        # Subtle shadow
        shadow_surf = font_title.render("LathamVerse", True, (0, 0, 0))
        shadow_surf.set_alpha(60)
        screen.blit(shadow_surf, (WIDTH // 2 - title_surf.get_width() // 2 + 2, 162))
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 160))

        # Underline accent
        uw = title_surf.get_width()
        accent_alpha = int(140 + 60 * math.sin(t * 2))
        line_s = pygame.Surface((uw, 2), pygame.SRCALPHA)
        # Gradient-ish line: teal to violet
        for lx in range(uw):
            frac = lx / uw
            r = int(TEAL[0] * (1 - frac) + VIOLET[0] * frac)
            g = int(TEAL[1] * (1 - frac) + VIOLET[1] * frac)
            b = int(TEAL[2] * (1 - frac) + VIOLET[2] * frac)
            line_s.set_at((lx, 0), (r, g, b, accent_alpha))
            line_s.set_at((lx, 1), (r, g, b, accent_alpha // 2))
        screen.blit(line_s, (WIDTH // 2 - uw // 2, 210))

        # Subtitle
        sub_surf = font_subtitle.render("become the ultimate looksmaxer", True, TEXT_DIM)
        screen.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, 228))

        mouse_pos = pygame.mouse.get_pos()

        # Continue button
        cont_hover = continue_rect.collidepoint(mouse_pos)
        cont_bg = TEAL if cont_hover else (45, 50, 62)
        cont_border = TEAL if cont_hover else (65, 70, 85)
        pygame.draw.rect(screen, cont_bg, continue_rect, border_radius=8)
        pygame.draw.rect(screen, cont_border, continue_rect, width=1, border_radius=8)
        cont_text_color = BG_DARK if cont_hover else TEXT_LIGHT
        draw_text_centered("Continue", font_lg, cont_text_color, continue_rect.centerx, continue_rect.centery)

        # New game button
        rst_hover = restart_rect.collidepoint(mouse_pos)
        rst_bg = CORAL_DIM if rst_hover else (38, 35, 42)
        rst_border = CORAL if rst_hover else (58, 55, 65)
        pygame.draw.rect(screen, rst_bg, restart_rect, border_radius=8)
        pygame.draw.rect(screen, rst_border, restart_rect, width=1, border_radius=8)
        rst_text_color = TEXT_WHITE if rst_hover else TEXT_DIM
        draw_text_centered("New Game", font_lg, rst_text_color, restart_rect.centerx, restart_rect.centery)

        # Version / credit
        draw_text_centered("v1.0", font_sm, TEXT_DARK, WIDTH // 2, HEIGHT - 25)

        pygame.display.flip()


def main():
    core = GameCore()

    was_loaded = main_menu(core)

    show_offline_popup = was_loaded and core.offline_time_seconds > 0
    close_popup_btn = pygame.Rect(WIDTH // 2 - 100, 395, 200, 48)

    clock = pygame.time.Clock()
    last_time = time.time()

    AUTOSAVE_INTERVAL = 60.0
    autosave_timer = 0.0

    # Load all ascension tier images (least aura → most aura)
    # Dillon1 = bald (asc 0), Dillon2 = tiny spiky (asc 1), Dillon3 = tall spiky (asc 2),
    # Dillon4 = massive hair (asc 3-4), Dillon5 = hair surfer (asc 5+)
    ascension_images = []
    for i in range(1, 6):
        try:
            img = pygame.image.load(resource_path(f"assets/Dillon{i}.png")).convert_alpha()
            img = pygame.transform.scale(img, (180, 180))
            ascension_images.append(img)
        except FileNotFoundError:
            fallback = pygame.Surface((180, 180))
            fallback.fill((100, 100, 200))
            ascension_images.append(fallback)

    # Ascension thresholds for each image tier
    # Index 0 = asc 0, 1 = asc 1, 2 = asc 2, 3 = asc 3-4, 4 = asc 5+
    def get_clicker_image(ascensions):
        if ascensions >= 5:
            return ascension_images[4]
        elif ascensions >= 3:
            return ascension_images[3]
        elif ascensions >= 2:
            return ascension_images[2]
        elif ascensions >= 1:
            return ascension_images[1]
        else:
            return ascension_images[0]

    clicker_image = get_clicker_image(core.player.ascensions)

    try:
        foxy_image = pygame.image.load(resource_path("assets/foxy.gif")).convert_alpha()
        foxy_image = pygame.transform.scale(foxy_image, (WIDTH, HEIGHT))
    except FileNotFoundError:
        foxy_image = None
    try:
        jumpscare_sound = pygame.mixer.Sound(resource_path("assets/foxy.mp3"))
    except FileNotFoundError:
        jumpscare_sound = None

    # Load game sound effects
    def load_sfx(name):
        try:
            return pygame.mixer.Sound(resource_path(f"assets/{name}"))
        except FileNotFoundError:
            return None

    sfx_click = load_sfx("click.wav")
    sfx_purchase = load_sfx("purchase.wav")
    sfx_ascend = load_sfx("ascend.wav")
    sfx_deny = load_sfx("deny.wav")
    sfx_tab = load_sfx("tab.wav")
    sfx_milestone = load_sfx("milestone.wav")

    all_sfx = [s for s in (sfx_click, sfx_purchase, sfx_ascend, sfx_deny, sfx_tab, sfx_milestone) if s]
    muted = False

    def set_muted(m):
        for s in all_sfx:
            s.set_volume(0.0 if m else 1.0)

    # Layout constants
    LEFT_W = 260
    LEFT_PAD = 8
    RIGHT_X = LEFT_W + LEFT_PAD * 2 + 4
    RIGHT_W = WIDTH - RIGHT_X - LEFT_PAD

    clicker_cx = LEFT_PAD + LEFT_W // 2
    clicker_cy = 280
    clicker_rect = pygame.Rect(clicker_cx - 90, clicker_cy - 90, 180, 180)

    ascend_rect = pygame.Rect(LEFT_PAD + 15, 430, LEFT_W - 30, 46)
    mute_rect = pygame.Rect(LEFT_PAD + LEFT_W - 46, 14, 38, 20)

    # Tab state
    active_tab = "upgrades"
    tab_y = LEFT_PAD
    tab_h = 32
    tab_gap = 6
    tab_w = (RIGHT_W - tab_gap) // 2
    tab_upgrades_rect = pygame.Rect(RIGHT_X, tab_y, tab_w, tab_h)
    tab_prestige_rect = pygame.Rect(RIGHT_X + tab_w + tab_gap, tab_y, tab_w, tab_h)

    scroll_offset = 0
    max_scroll = 0

    particles = []
    floating_texts = []
    bounces = {}
    bounce_frames = 4
    jumpscare_timer = 0.0  # Time-based (seconds), matches sound duration
    t = 0.0

    new_unlocks_flash = 0

    ascend_confirm_pending = False
    ascend_confirm_yes_rect = pygame.Rect(WIDTH // 2 - 150, 400, 130, 46)
    ascend_confirm_no_rect = pygame.Rect(WIDTH // 2 + 20, 400, 130, 46)

    def do_ascend():
        nonlocal active_tab, scroll_offset, clicker_image, new_unlocks_flash
        old_milestone = core.get_next_milestone()
        if core.attempt_ascension():
            bounces["ascend"] = bounce_frames
            new_unlocks_flash = 3.0
            active_tab = "upgrades"
            scroll_offset = 0
            clicker_image = get_clicker_image(core.player.ascensions)
            new_milestone = core.get_next_milestone()
            if old_milestone != new_milestone and sfx_milestone:
                sfx_milestone.play()
            elif sfx_ascend:
                sfx_ascend.play()

    # Hover tracking for smooth highlights
    hover_card = None

    running = True
    while running:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        t += dt

        if not show_offline_popup and not ascend_confirm_pending:
            core.idle(dt)
            autosave_timer += dt
            if autosave_timer >= AUTOSAVE_INTERVAL:
                core.save_game()
                autosave_timer = 0.0

        if new_unlocks_flash > 0:
            new_unlocks_flash -= dt

        mouse_pos = pygame.mouse.get_pos()
        hover_card = None  # Reset each frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                core.save_game()
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = event.pos

                if show_offline_popup:
                    if close_popup_btn.collidepoint(click_pos):
                        show_offline_popup = False
                        last_time = time.time()
                    continue

                if ascend_confirm_pending:
                    if ascend_confirm_yes_rect.collidepoint(click_pos):
                        do_ascend()
                    ascend_confirm_pending = False
                    continue

                if mute_rect.collidepoint(click_pos):
                    muted = not muted
                    set_muted(muted)
                    continue

                # Jumpscare (1 in 50000)
                if random.randint(1, 50000) == 1:
                    jumpscare_timer = 5.0
                    if jumpscare_sound:
                        jumpscare_sound.play()

                # Particles on every click
                for _ in range(30):
                    particles.append(Particle(click_pos[0], click_pos[1]))

                # Tab switching
                if tab_upgrades_rect.collidepoint(click_pos):
                    if active_tab != "upgrades" and sfx_tab:
                        sfx_tab.play()
                    active_tab = "upgrades"
                    scroll_offset = 0
                elif tab_prestige_rect.collidepoint(click_pos):
                    if core.player.ascensions >= 1:
                        if active_tab != "prestige" and sfx_tab:
                            sfx_tab.play()
                        active_tab = "prestige"
                        scroll_offset = 0
                    elif sfx_deny:
                        sfx_deny.play()

                # Clicker
                elif clicker_rect.collidepoint(click_pos):
                    result = core.click()
                    if result:
                        power, is_crit = result
                        bounces["clicker"] = bounce_frames
                        if sfx_click:
                            sfx_click.play()
                        text = f"CRIT +{format_number(power)}!" if is_crit else f"+{format_number(power)}"
                        floating_texts.append(FloatingText(
                            click_pos[0], click_pos[1],
                            text, CORAL if is_crit else AMBER
                        ))

                # Ascend (opens confirmation)
                elif ascend_rect.collidepoint(click_pos):
                    if core.player.little_lathams >= core.ascension_threshold:
                        ascend_confirm_pending = True
                    elif sfx_deny:
                        sfx_deny.play()
                else:
                    # Panel clicks
                    panel_content_y = tab_y + tab_h + 8
                    panel_h = HEIGHT - panel_content_y - LEFT_PAD

                    if active_tab == "upgrades":
                        visible = core.get_visible_upgrades()
                        y = panel_content_y + 6 - scroll_offset
                        for name, upgrade in visible.items():
                            card_rect = pygame.Rect(RIGHT_X + 6, y, RIGHT_W - 12, 58)
                            if card_rect.collidepoint(click_pos) and panel_content_y <= click_pos[1] <= panel_content_y + panel_h:
                                if core.attempt_purchase(name):
                                    bounces[f"upg_{name}"] = bounce_frames
                                    if sfx_purchase:
                                        sfx_purchase.play()
                                elif sfx_deny:
                                    sfx_deny.play()
                            y += 64

                    elif active_tab == "prestige":
                        visible = core.get_visible_prestige()
                        y = panel_content_y + 44 - scroll_offset
                        for name, upgrade in visible.items():
                            card_rect = pygame.Rect(RIGHT_X + 6, y, RIGHT_W - 12, 62)
                            if card_rect.collidepoint(click_pos) and panel_content_y <= click_pos[1] <= panel_content_y + panel_h:
                                if core.attempt_prestige_purchase(name):
                                    bounces[f"pres_{name}"] = bounce_frames
                                    if sfx_purchase:
                                        sfx_purchase.play()
                                elif sfx_deny:
                                    sfx_deny.play()
                            y += 68

            if event.type == pygame.MOUSEWHEEL and not show_offline_popup and not ascend_confirm_pending:
                # Jumpscare chance on scroll too
                if random.randint(1, 50000) == 1:
                    jumpscare_timer = 5.0
                    if jumpscare_sound:
                        jumpscare_sound.play()
                if mouse_pos[0] >= RIGHT_X:
                    scroll_offset = max(0, min(max_scroll, scroll_offset - event.y * 25))

            if event.type == pygame.KEYDOWN and not show_offline_popup:
                if ascend_confirm_pending:
                    if event.key == pygame.K_RETURN:
                        do_ascend()
                        ascend_confirm_pending = False
                    elif event.key == pygame.K_ESCAPE:
                        ascend_confirm_pending = False
                elif event.key == pygame.K_a:
                    if core.player.little_lathams >= core.ascension_threshold:
                        ascend_confirm_pending = True
                    elif sfx_deny:
                        sfx_deny.play()

        # --- UPDATE ---
        if not show_offline_popup and not ascend_confirm_pending:
            for p in particles[:]:
                p.update()
                if p.lifetime <= 0:
                    particles.remove(p)

            for ft in floating_texts[:]:
                ft.update()
                if ft.lifetime <= 0:
                    floating_texts.remove(ft)

            for key in list(bounces.keys()):
                if bounces[key] > 0:
                    bounces[key] -= 1

            if jumpscare_timer > 0:
                jumpscare_timer -= dt

        # ==================== DRAWING ====================
        screen.fill(BG_DARK)
        draw_bg_grid(screen, t)
        screen.blit(noise_texture, (0, 0))

        # === LEFT PANEL ===
        left_rect = pygame.Rect(LEFT_PAD, LEFT_PAD, LEFT_W, HEIGHT - LEFT_PAD * 2)
        draw_panel(screen, left_rect, PANEL_BG)

        # --- Header: title + currency ---
        draw_text("LathamVerse", font_lg, TEXT_WHITE, LEFT_PAD + 14, 16)

        # Mute toggle
        mute_hover = mute_rect.collidepoint(mouse_pos)
        mute_bg = (45, 47, 60) if mute_hover else (35, 37, 48)
        pygame.draw.rect(screen, mute_bg, mute_rect, border_radius=4)
        pygame.draw.rect(screen, DIVIDER, mute_rect, width=1, border_radius=4)
        mute_col = CORAL if muted else TEAL
        draw_text_centered("MUTE" if muted else "SFX", font_sm, mute_col, mute_rect.centerx, mute_rect.centery)

        # Divider
        pygame.draw.line(screen, DIVIDER, (LEFT_PAD + 14, 46), (LEFT_PAD + LEFT_W - 14, 46), 1)

        # Currency display - big and prominent
        lathams_str = format_number(core.player.little_lathams)
        draw_text(lathams_str, font_xl, AMBER, LEFT_PAD + 14, 54)
        draw_text("little lathams", font_sm, TEXT_DIM, LEFT_PAD + 14, 88)

        # Stats row
        stats_y = 110
        # Click power
        draw_text("click", font_sm, TEXT_DIM, LEFT_PAD + 14, stats_y)
        draw_text(format_number(core.current_click_power), font_md_b, TEAL, LEFT_PAD + 14, stats_y + 14)
        # Idle power
        draw_text("per sec", font_sm, TEXT_DIM, LEFT_PAD + 100, stats_y)
        draw_text(f"{format_number(core.current_idle_power)}", font_md_b, LIME, LEFT_PAD + 100, stats_y + 14)
        # Multiplier
        draw_text("mult", font_sm, TEXT_DIM, LEFT_PAD + 190, stats_y)
        draw_text(f"x{core.player.ascensions_multiplier:.1f}", font_md_b, VIOLET, LEFT_PAD + 190, stats_y + 14)

        # Divider
        pygame.draw.line(screen, DIVIDER, (LEFT_PAD + 14, 148), (LEFT_PAD + LEFT_W - 14, 148), 1)

        # Ascension info compact row
        asc_y = 155
        draw_text(f"Ascension {core.player.ascensions}", font_body_b, VIOLET, LEFT_PAD + 14, asc_y)
        if core.player.ascensions >= 1:
            draw_text_right(f"{core.player.ascension_points} AP", font_body_b, AMBER, LEFT_PAD + LEFT_W - 14, asc_y)

        # --- Clicker Image ---
        frame_cx = clicker_cx
        frame_cy = clicker_cy + 2

        # Auto-clicker animated ring (only when prestige unlocked)
        if core.has_prestige("auto_click"):
            frame_r = 94
            arc_angle = (t * 3) % (math.pi * 2)
            ring_s = pygame.Surface((frame_r * 2 + 8, frame_r * 2 + 8), pygame.SRCALPHA)
            for i in range(20):
                a = arc_angle + i * 0.15
                px = int(frame_r + 4 + math.cos(a) * (frame_r + 1))
                py = int(frame_r + 4 + math.sin(a) * (frame_r + 1))
                alpha = max(0, 180 - i * 9)
                pygame.draw.circle(ring_s, (*TEAL[:3], alpha), (px, py), 2)
            screen.blit(ring_s, (frame_cx - frame_r - 4, frame_cy - frame_r - 4))

        # The image itself
        if bounces.get("clicker", 0) > 0:
            scale_sz = 168
            scaled = pygame.transform.scale(clicker_image, (scale_sz, scale_sz))
            screen.blit(scaled, (frame_cx - scale_sz // 2, frame_cy - scale_sz // 2))
        else:
            screen.blit(clicker_image, (frame_cx - 90, frame_cy - 90))

        # Click hint
        draw_text_centered("tap to earn", font_sm, TEXT_DARK, frame_cx, frame_cy + 100)

        # --- Ascend Button ---
        can_ascend = core.player.little_lathams >= core.ascension_threshold

        current_ascend_rect = ascend_rect.copy()
        if bounces.get("ascend", 0) > 0:
            current_ascend_rect = current_ascend_rect.inflate(-4, -4)

        if can_ascend:
            # Glow behind
            glow_a = int(40 + 25 * math.sin(t * 2.5))
            glow_s = pygame.Surface((current_ascend_rect.width + 12, current_ascend_rect.height + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow_s, (*VIOLET[:3], glow_a), glow_s.get_rect(), border_radius=10)
            screen.blit(glow_s, (current_ascend_rect.x - 6, current_ascend_rect.y - 6))

            pygame.draw.rect(screen, VIOLET, current_ascend_rect, border_radius=7)
            pygame.draw.rect(screen, (180, 140, 255), current_ascend_rect, width=1, border_radius=7)
            # Shine
            shine_s = pygame.Surface((current_ascend_rect.width, current_ascend_rect.height // 2), pygame.SRCALPHA)
            shine_s.fill((255, 255, 255, 18))
            screen.blit(shine_s, current_ascend_rect.topleft)
        else:
            pygame.draw.rect(screen, (35, 37, 48), current_ascend_rect, border_radius=7)
            pygame.draw.rect(screen, DIVIDER, current_ascend_rect, width=1, border_radius=7)

        asc_text_col = TEXT_WHITE if can_ascend else TEXT_DARK
        draw_text_centered("ASCEND", font_md_b, asc_text_col, current_ascend_rect.centerx, current_ascend_rect.centery - 6)
        cost_text = f"{format_number(core.ascension_threshold)} needed"
        draw_text_centered(cost_text, font_sm, asc_text_col if not can_ascend else (220, 210, 255), current_ascend_rect.centerx, current_ascend_rect.centery + 10)

        # AP reward preview
        if can_ascend:
            ap_preview = core.calculate_ap_reward()
            draw_text(f"+{ap_preview} AP", font_sm, AMBER, current_ascend_rect.right + 6, current_ascend_rect.centery - 6)

        # Progress bar
        progress = min(1.0, core.player.little_lathams / core.ascension_threshold)
        bar_y = current_ascend_rect.bottom + 8
        draw_progress_bar(screen, LEFT_PAD + 15, bar_y, LEFT_W - 30, 5, progress, VIOLET)
        pct_text = f"{progress * 100:.0f}%"
        draw_text_centered(pct_text, font_sm, TEXT_DIM, LEFT_PAD + LEFT_W // 2, bar_y + 14)

        # --- Milestones ---
        ms_y = bar_y + 28
        pygame.draw.line(screen, DIVIDER, (LEFT_PAD + 14, ms_y), (LEFT_PAD + LEFT_W - 14, ms_y), 1)
        ms_y += 6
        draw_text("Milestones", font_body_b, TEXT_LIGHT, LEFT_PAD + 14, ms_y)
        ms_y += 22

        unlocked = core.get_unlocked_milestones()
        next_ms = core.get_next_milestone()

        for _, ms_name, _ in unlocked[-3:]:
            draw_text(f"• {ms_name}", font_sm, TEAL, LEFT_PAD + 18, ms_y)
            ms_y += 17

        if next_ms and ms_y < HEIGHT - LEFT_PAD - 10:
            draw_text(f"› {next_ms[1]} (Asc {next_ms[0]})", font_sm, TEXT_DARK, LEFT_PAD + 18, ms_y)

        # === RIGHT PANEL (Upgrades / Prestige) ===
        panel_content_y = tab_y + tab_h + 8
        panel_h_val = HEIGHT - panel_content_y - LEFT_PAD

        right_bg_rect = pygame.Rect(RIGHT_X, panel_content_y, RIGHT_W, panel_h_val)
        draw_panel(screen, right_bg_rect, PANEL_BG_ALT)

        # --- Tabs ---
        for tab_name, tab_rect, tab_color, tab_dim in [
            ("Upgrades", tab_upgrades_rect, TEAL, TEAL_DIM),
            ("Prestige", tab_prestige_rect, VIOLET, VIOLET_DIM),
        ]:
            if tab_name == "Prestige" and core.player.ascensions < 1:
                # Draw locked tab
                pygame.draw.rect(screen, (30, 32, 40), tab_rect, border_radius=5)
                draw_text_centered("🔒 Prestige", font_body, TEXT_DARK, tab_rect.centerx, tab_rect.centery)
                continue

            is_active = (active_tab == tab_name.lower())
            if is_active:
                pygame.draw.rect(screen, tab_color, tab_rect, border_radius=5)
                draw_text_centered(tab_name, font_body_b, BG_DARK, tab_rect.centerx, tab_rect.centery)
            else:
                pygame.draw.rect(screen, (35, 37, 48), tab_rect, border_radius=5)
                pygame.draw.rect(screen, DIVIDER, tab_rect, width=1, border_radius=5)
                draw_text_centered(tab_name, font_body, TEXT_DIM, tab_rect.centerx, tab_rect.centery)

        # --- Content area (clipped) ---
        clip_rect = pygame.Rect(RIGHT_X + 1, panel_content_y + 1, RIGHT_W - 2, panel_h_val - 2)
        screen.set_clip(clip_rect)

        if active_tab == "upgrades":
            visible = core.get_visible_upgrades()
            y = panel_content_y + 6 - scroll_offset

            for name, upgrade in visible.items():
                card_rect = pygame.Rect(RIGHT_X + 6, y, RIGHT_W - 12, 58)

                if y + 58 > panel_content_y and y < panel_content_y + panel_h_val:
                    affordable = core.player.little_lathams >= upgrade.current_cost
                    is_bouncing = bounces.get(f"upg_{name}", 0) > 0
                    is_hovered = card_rect.collidepoint(mouse_pos)

                    # New unlock flash
                    is_new = (upgrade.required_ascensions == core.player.ascensions
                              and upgrade.required_ascensions > 0
                              and new_unlocks_flash > 0)

                    accent = TEAL if affordable else DIVIDER
                    actual = draw_card(screen, card_rect, accent_color=accent, hover=is_hovered and affordable, bounce=is_bouncing)

                    if is_new:
                        flash_a = int(25 + 20 * math.sin(t * 6))
                        flash_s = pygame.Surface((actual.width, actual.height), pygame.SRCALPHA)
                        flash_s.fill((*AMBER[:3], flash_a))
                        screen.blit(flash_s, actual.topleft)

                    # Name
                    name_col = TEXT_WHITE if affordable else TEXT_DIM
                    draw_text(name, font_body_b, name_col, actual.x + 12, actual.y + 8)

                    # Level badge
                    lvl_text = f"Lv.{upgrade.level}"
                    lvl_col = TEAL if affordable else TEXT_DARK
                    draw_text(lvl_text, font_sm, lvl_col, actual.x + 12, actual.y + 30)

                    # Effect
                    eff_type = "click" if upgrade.effect_type == "click" else "/s"
                    eff_str = f"+{format_number(upgrade.base_power)} {eff_type}"
                    draw_text(eff_str, font_sm, TEXT_DIM, actual.x + 70, actual.y + 30)

                    # Cost (right aligned)
                    cost_str = format_number(upgrade.current_cost)
                    cost_col = TEAL if affordable else CORAL
                    draw_text_right(cost_str, font_md_b, cost_col, actual.right - 10, actual.y + 10)
                    draw_text_right("lathams", font_sm, TEXT_DARK, actual.right - 10, actual.y + 30)

                y += 64

            max_scroll = max(0, y + scroll_offset - panel_content_y - panel_h_val + 6)

        elif active_tab == "prestige":
            visible = core.get_visible_prestige()
            y = panel_content_y + 6 - scroll_offset

            # AP header
            ap_hdr = pygame.Rect(RIGHT_X + 6, y, RIGHT_W - 12, 32)
            pygame.draw.rect(screen, (35, 32, 22), ap_hdr, border_radius=5)
            draw_text_centered(f"✦ {core.player.ascension_points} Ascension Points", font_body_b, AMBER, ap_hdr.centerx, ap_hdr.centery)
            y += 38

            for name, upgrade in visible.items():
                card_rect = pygame.Rect(RIGHT_X + 6, y, RIGHT_W - 12, 62)

                if y + 62 > panel_content_y and y < panel_content_y + panel_h_val:
                    is_bouncing = bounces.get(f"pres_{name}", 0) > 0
                    is_hovered = card_rect.collidepoint(mouse_pos)

                    if upgrade.purchased:
                        actual = draw_card(screen, card_rect, accent_color=TEAL, hover=False, bounce=is_bouncing)
                        draw_text(f"✓ {name}", font_body_b, TEAL, actual.x + 12, actual.y + 8)
                        draw_text(upgrade.description, font_sm, TEXT_DIM, actual.x + 12, actual.y + 30)
                        draw_text_right("OWNED", font_sm, TEAL, actual.right - 10, actual.y + 20)
                    else:
                        can_buy = upgrade.can_purchase(core.player.ascension_points, core.player.ascensions)
                        accent = VIOLET if can_buy else DIVIDER
                        actual = draw_card(screen, card_rect, accent_color=accent, hover=is_hovered and can_buy, bounce=is_bouncing)

                        name_col = TEXT_WHITE if can_buy else TEXT_DIM
                        draw_text(name, font_body_b, name_col, actual.x + 12, actual.y + 8)
                        desc_col = TEXT_DIM if can_buy else TEXT_DARK
                        draw_text(upgrade.description, font_sm, desc_col, actual.x + 12, actual.y + 30)

                        cost_col = AMBER if can_buy else CORAL
                        draw_text_right(f"{upgrade.cost} AP", font_md_b, cost_col, actual.right - 10, actual.y + 10)

                        if upgrade.required_ascensions > core.player.ascensions:
                            draw_text_right(f"Asc {upgrade.required_ascensions}", font_sm, TEXT_DARK, actual.right - 10, actual.y + 34)

                y += 68

            max_scroll = max(0, y + scroll_offset - panel_content_y - panel_h_val + 6)

        screen.set_clip(None)

        # Scroll indicator if there's scrollable content
        if max_scroll > 0:
            scroll_frac = scroll_offset / max_scroll if max_scroll > 0 else 0
            indicator_h = max(20, int(panel_h_val * (panel_h_val / (panel_h_val + max_scroll))))
            indicator_y = panel_content_y + int((panel_h_val - indicator_h) * scroll_frac)
            indicator_rect = pygame.Rect(RIGHT_X + RIGHT_W - 4, indicator_y, 3, indicator_h)
            scroll_s = pygame.Surface((3, indicator_h), pygame.SRCALPHA)
            scroll_s.fill((255, 255, 255, 35))
            screen.blit(scroll_s, indicator_rect.topleft)

        # --- Floating texts ---
        for ft in floating_texts:
            ft.draw(screen)

        # --- Particles ---
        for p in particles:
            p.draw(screen)

        # --- Jumpscare ---
        if jumpscare_timer > 0 and foxy_image:
            screen.blit(foxy_image, (0, 0))

        # --- Offline popup ---
        if show_offline_popup:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            popup_rect = pygame.Rect(WIDTH // 2 - 200, 160, 400, 300)
            draw_panel(screen, popup_rect, PANEL_BG)
            pygame.draw.rect(screen, AMBER_DIM, popup_rect, width=1, border_radius=6)

            draw_text_centered("Welcome Back", font_xl, TEXT_WHITE, WIDTH // 2, 200)

            # Divider
            div_y = 225
            pygame.draw.line(screen, DIVIDER, (popup_rect.x + 30, div_y), (popup_rect.right - 30, div_y), 1)

            time_str = format_time(core.offline_time_seconds)
            draw_text_centered(f"You were gone for {time_str}", font_body, TEXT_DIM, WIDTH // 2, 250)

            earned_str = format_number(core.offline_lathams_gained)
            draw_text_centered(f"+{earned_str}", font_xl, TEAL, WIDTH // 2, 290)
            draw_text_centered("little lathams earned", font_sm, TEXT_DIM, WIDTH // 2, 322)

            if core.has_prestige("offline_mult"):
                draw_text_centered("2x Offline Boost active", font_sm, VIOLET, WIDTH // 2, 345)

            # Show cap notice if they were away longer than 30 minutes
            if core.offline_time_seconds >= MAX_OFFLINE_SECONDS:
                draw_text_centered("(capped at 30 min)", font_sm, TEXT_DARK, WIDTH // 2, 365)

            # Button
            btn_hover = close_popup_btn.collidepoint(mouse_pos)
            btn_bg = TEAL if btn_hover else TEAL_DIM
            pygame.draw.rect(screen, btn_bg, close_popup_btn, border_radius=7)
            btn_text_col = BG_DARK if btn_hover else TEXT_WHITE
            draw_text_centered("Nice", font_md_b, btn_text_col, close_popup_btn.centerx, close_popup_btn.centery)

        # --- Ascend confirmation popup ---
        if ascend_confirm_pending:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            popup_rect = pygame.Rect(WIDTH // 2 - 200, 160, 400, 300)
            draw_panel(screen, popup_rect, PANEL_BG)
            pygame.draw.rect(screen, VIOLET_DIM, popup_rect, width=1, border_radius=6)

            draw_text_centered("Ascend?", font_xl, TEXT_WHITE, WIDTH // 2, 200)

            div_y = 225
            pygame.draw.line(screen, DIVIDER, (popup_rect.x + 30, div_y), (popup_rect.right - 30, div_y), 1)

            draw_text_centered("All lathams and upgrade levels will reset.", font_body, TEXT_DIM, WIDTH // 2, 250)
            next_mult = 1.5 ** (core.player.ascensions + 1)
            draw_text_centered(
                f"Multiplier x{core.player.ascensions_multiplier:.1f} → x{next_mult:.1f}",
                font_body, TEAL, WIDTH // 2, 275
            )

            ap_preview = core.calculate_ap_reward()
            draw_text_centered(f"+{ap_preview} Ascension Points", font_lg, AMBER, WIDTH // 2, 320)

            yes_hover = ascend_confirm_yes_rect.collidepoint(mouse_pos)
            yes_bg = VIOLET if yes_hover else VIOLET_DIM
            pygame.draw.rect(screen, yes_bg, ascend_confirm_yes_rect, border_radius=7)
            draw_text_centered("Confirm", font_md_b, TEXT_WHITE, ascend_confirm_yes_rect.centerx, ascend_confirm_yes_rect.centery)

            no_hover = ascend_confirm_no_rect.collidepoint(mouse_pos)
            no_bg = (48, 50, 62) if no_hover else (38, 35, 42)
            pygame.draw.rect(screen, no_bg, ascend_confirm_no_rect, border_radius=7)
            pygame.draw.rect(screen, DIVIDER, ascend_confirm_no_rect, width=1, border_radius=7)
            draw_text_centered("Cancel", font_md_b, TEXT_LIGHT, ascend_confirm_no_rect.centerx, ascend_confirm_no_rect.centery)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()