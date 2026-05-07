"""
Arcade Launcher  —  selecciona un juego y a jugar.
"""

import pygame
import sys

pygame.init()

# ── Colores ─────────────────────────────────────────────────────────────────
BG          = (14, 14, 26)
PANEL_BG    = (22, 22, 40)
BORDER      = (50, 50, 80)
TITLE_COL   = (80, 220, 180)
TEXT_COL    = (220, 220, 230)
DIM_COL     = (100, 100, 140)
HOVER_BG    = (35, 35, 65)
SEL_BG      = (40, 80, 120)
SEL_BORDER  = (80, 180, 240)
BACK_COL    = (160, 100, 240)

# ── Resolución base ──────────────────────────────────────────────────────────
BASE_W, BASE_H = 780, 560
screen = pygame.display.set_mode((BASE_W, BASE_H))
pygame.display.set_caption("Arcade Python")
clock = pygame.time.Clock()

font_title  = pygame.font.SysFont("consolas", 44, bold=True)
font_sub    = pygame.font.SysFont("consolas", 18)
font_item   = pygame.font.SysFont("consolas", 24, bold=True)
font_desc   = pygame.font.SysFont("consolas", 14)
font_hint   = pygame.font.SysFont("consolas", 13)

# ── Catálogo de juegos ───────────────────────────────────────────────────────
GAMES = [
    {
        "name":   "Serpiente",
        "module": "games.snake",
        "desc":   "Come manzanas, crece y llena el mapa. Clásico sin piedad.",
        "icon":   "🐍",
        "color":  (60, 200, 100),
        "difficulties": ["Muy Fácil", "Fácil", "Medio", "Difícil", "Legendario"],
    },
    # Próximamente...
    {
        "name":   "Naves Espaciales",
        "module": None,
        "desc":   "Defiende la galaxia. ¡Próximamente!",
        "icon":   "🚀",
        "color":  (100, 140, 220),
        "difficulties": [],
    },
]

DIFF_COLORS = {
    "Muy Fácil":  (100, 220, 100),
    "Fácil":      (80,  200, 80),
    "Medio":      (220, 200, 60),
    "Difícil":    (220, 130, 50),
    "Legendario": (210, 60,  60),
}

# ── Estado ───────────────────────────────────────────────────────────────────
state     = "game_select"   # game_select | diff_select
sel_game  = 0
sel_diff  = 0
hover_game = -1
hover_diff = -1


def draw_rounded_rect(surf, color, rect, radius=10, border_color=None, border_w=2):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border_color:
        pygame.draw.rect(surf, border_color, rect, border_w, border_radius=radius)


def game_select_screen(mx, my):
    global sel_game, hover_game

    screen.fill(BG)

    # Title
    t = font_title.render("ARCADE PYTHON", True, TITLE_COL)
    screen.blit(t, t.get_rect(centerx=BASE_W // 2, y=28))
    s = font_sub.render("Elige tu juego", True, DIM_COL)
    screen.blit(s, s.get_rect(centerx=BASE_W // 2, y=80))

    # Game cards
    card_w, card_h = 320, 160
    gap = 30
    total_w = len(GAMES) * card_w + (len(GAMES) - 1) * gap
    start_x = (BASE_W - total_w) // 2
    start_y = 130

    rects = []
    for i, game in enumerate(GAMES):
        x = start_x + i * (card_w + gap)
        rect = pygame.Rect(x, start_y, card_w, card_h)
        rects.append(rect)

        hovered = rect.collidepoint(mx, my)
        if hovered:
            hover_game = i

        if game["module"] is None:
            bg = (20, 20, 36)
            bcolor = BORDER
        elif i == sel_game:
            bg = SEL_BG
            bcolor = SEL_BORDER
        elif hovered:
            bg = HOVER_BG
            bcolor = game["color"]
        else:
            bg = PANEL_BG
            bcolor = BORDER

        draw_rounded_rect(screen, bg, rect, 12, bcolor, 2)

        # Icon placeholder circle
        pygame.draw.circle(screen, game["color"] if game["module"] else BORDER,
                           (x + 50, start_y + 50), 28)
        ico = font_item.render(["S", "N"][i], True, BG if game["module"] else DIM_COL)
        screen.blit(ico, ico.get_rect(center=(x + 50, start_y + 50)))

        name_col = TEXT_COL if game["module"] else DIM_COL
        nm = font_item.render(game["name"], True, name_col)
        screen.blit(nm, (x + 90, start_y + 30))

        desc = font_desc.render(game["desc"], True, DIM_COL)
        screen.blit(desc, (x + 12, start_y + 110))

        if game["module"] is None:
            prox = font_desc.render("PRÓXIMAMENTE", True, (80, 80, 120))
            screen.blit(prox, prox.get_rect(centerx=x + card_w // 2, y=start_y + 80))

    # Hint
    h = font_hint.render("↑↓ / Clic para elegir   ENTER para continuar   ESC para salir", True, DIM_COL)
    screen.blit(h, h.get_rect(centerx=BASE_W // 2, y=BASE_H - 28))

    pygame.display.flip()
    return rects


def diff_select_screen(mx, my):
    global sel_diff, hover_diff

    game = GAMES[sel_game]
    diffs = game["difficulties"]

    screen.fill(BG)

    # Back arrow hint
    bk = font_hint.render("← ESC  volver", True, BACK_COL)
    screen.blit(bk, (18, 18))

    t = font_title.render(game["name"].upper(), True, game["color"])
    screen.blit(t, t.get_rect(centerx=BASE_W // 2, y=30))
    s = font_sub.render("Selecciona dificultad", True, DIM_COL)
    screen.blit(s, s.get_rect(centerx=BASE_W // 2, y=84))

    btn_w, btn_h = 460, 62
    gap = 14
    total_h = len(diffs) * btn_h + (len(diffs) - 1) * gap
    start_y = (BASE_H - total_h) // 2 + 20

    rects = []
    for i, diff in enumerate(diffs):
        x = (BASE_W - btn_w) // 2
        y = start_y + i * (btn_h + gap)
        rect = pygame.Rect(x, y, btn_w, btn_h)
        rects.append(rect)

        hovered = rect.collidepoint(mx, my)
        if hovered:
            hover_diff = i

        dc = DIFF_COLORS.get(diff, TEXT_COL)

        if i == sel_diff:
            bg = SEL_BG
            bcolor = dc
        elif hovered:
            bg = HOVER_BG
            bcolor = dc
        else:
            bg = PANEL_BG
            bcolor = BORDER

        draw_rounded_rect(screen, bg, rect, 10, bcolor, 2)

        # Color dot
        pygame.draw.circle(screen, dc, (x + 30, y + btn_h // 2), 9)

        label = font_item.render(diff, True, TEXT_COL if i == sel_diff else DIM_COL)
        screen.blit(label, label.get_rect(midleft=(x + 52, y + btn_h // 2)))

    h = font_hint.render("↑↓ / Clic para elegir   ENTER para jugar", True, DIM_COL)
    screen.blit(h, h.get_rect(centerx=BASE_W // 2, y=BASE_H - 28))

    pygame.display.flip()
    return rects


def launch_game(game_idx, difficulty):
    game = GAMES[game_idx]
    if game["module"] is None:
        return
    import importlib
    mod = importlib.import_module(game["module"])
    # Restore base resolution before passing surface; game will resize itself
    surf = pygame.display.set_mode((BASE_W, BASE_H))
    mod.run(surf, clock, difficulty)
    # Restore launcher window
    pygame.display.set_mode((BASE_W, BASE_H))
    pygame.display.set_caption("Arcade Python")


def main():
    global state, sel_game, sel_diff, hover_game, hover_diff

    while True:
        mx, my = pygame.mouse.get_pos()
        hover_game = -1
        hover_diff = -1

        if state == "game_select":
            rects = game_select_screen(mx, my)
        else:
            rects = diff_select_screen(mx, my)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if state == "game_select":
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        sel_game = (sel_game - 1) % len(GAMES)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        sel_game = (sel_game + 1) % len(GAMES)
                    elif event.key == pygame.K_RETURN:
                        if GAMES[sel_game]["module"]:
                            state = "diff_select"
                            sel_diff = 0
                else:
                    if event.key == pygame.K_ESCAPE:
                        state = "game_select"
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        sel_diff = (sel_diff - 1) % len(GAMES[sel_game]["difficulties"])
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        sel_diff = (sel_diff + 1) % len(GAMES[sel_game]["difficulties"])
                    elif event.key == pygame.K_RETURN:
                        diff = GAMES[sel_game]["difficulties"][sel_diff]
                        launch_game(sel_game, diff)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "game_select":
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mx, my) and GAMES[i]["module"]:
                            sel_game = i
                            state = "diff_select"
                            sel_diff = 0
                            break
                else:
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mx, my):
                            sel_diff = i
                            diff = GAMES[sel_game]["difficulties"][sel_diff]
                            launch_game(sel_game, diff)
                            break

        clock.tick(60)


if __name__ == "__main__":
    main()
