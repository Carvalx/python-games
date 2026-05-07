import pygame
import random
import sys

# ---------------------------------------------------------------------------
# Difficulty settings: (cell_size, grid_cols, grid_rows, fps, label)
# ---------------------------------------------------------------------------
DIFFICULTIES = {
    "Muy Fácil":  {"cols": 15, "rows": 12, "fps": 6,  "color": (100, 220, 100)},
    "Fácil":      {"cols": 20, "rows": 15, "fps": 9,  "color": (80,  200, 80)},
    "Medio":      {"cols": 25, "rows": 20, "fps": 13, "color": (220, 200, 60)},
    "Difícil":    {"cols": 32, "rows": 24, "fps": 18, "color": (220, 130, 50)},
    "Legendario": {"cols": 40, "rows": 30, "fps": 25, "color": (210, 60,  60)},
}

CELL = 24          # pixel size of each grid cell
PANEL = 48         # bottom HUD height

BG         = (18,  18,  30)
GRID_LINE  = (30,  30,  50)
SNAKE_HEAD = (80,  230, 120)
SNAKE_BODY = (50,  180, 90)
APPLE_COL  = (220, 60,  60)
TEXT_COL   = (230, 230, 230)
DIM_COL    = (100, 100, 130)
WIN_COL    = (80,  230, 180)
LOSE_COL   = (220, 80,  80)

UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)


def run(surface: pygame.Surface, clock: pygame.time.Clock, difficulty: str):
    cfg   = DIFFICULTIES[difficulty]
    cols  = cfg["cols"]
    rows  = cfg["rows"]
    fps   = cfg["fps"]
    diff_color = cfg["color"]

    win_w = cols * CELL
    win_h = rows * CELL + PANEL

    # Resize the surface to fit this difficulty
    surface = pygame.display.set_mode((win_w, win_h))
    pygame.display.set_caption(f"Serpiente — {difficulty}")

    font_big  = pygame.font.SysFont("consolas", 32, bold=True)
    font_med  = pygame.font.SysFont("consolas", 22)
    font_small= pygame.font.SysFont("consolas", 16)

    def new_game():
        snake = [(cols // 2, rows // 2)]
        direction = RIGHT
        apple = spawn_apple(snake, cols, rows)
        return snake, direction, apple, 0

    def spawn_apple(snake, cols, rows):
        free = [(c, r) for c in range(cols) for r in range(rows) if (c, r) not in snake]
        return random.choice(free) if free else None

    def draw_grid():
        for c in range(0, win_w, CELL):
            pygame.draw.line(surface, GRID_LINE, (c, 0), (c, rows * CELL))
        for r in range(0, rows * CELL, CELL):
            pygame.draw.line(surface, GRID_LINE, (0, r), (win_w, r))

    def draw_cell(col, row, color, shrink=2):
        pygame.draw.rect(
            surface, color,
            (col * CELL + shrink, row * CELL + shrink,
             CELL - shrink * 2, CELL - shrink * 2),
            border_radius=4,
        )

    def draw_hud(score, total_cells):
        hud_y = rows * CELL
        pygame.draw.rect(surface, (12, 12, 22), (0, hud_y, win_w, PANEL))
        pygame.draw.line(surface, GRID_LINE, (0, hud_y), (win_w, hud_y))

        pct   = score / total_cells * 100
        bar_w = int((win_w - 20) * pct / 100)
        pygame.draw.rect(surface, (40, 40, 60), (10, hud_y + 28, win_w - 20, 10), border_radius=5)
        if bar_w > 0:
            pygame.draw.rect(surface, diff_color, (10, hud_y + 28, bar_w, 10), border_radius=5)

        sc_txt = font_med.render(f"Puntos: {score}", True, TEXT_COL)
        df_txt = font_small.render(f"{difficulty}  —  {pct:.1f}% del mapa", True, DIM_COL)
        surface.blit(sc_txt, (10, hud_y + 4))
        surface.blit(df_txt, (10, hud_y + 30))

    def overlay(title, color, subtitle=""):
        overlay_surf = pygame.Surface((win_w, win_h), pygame.SRCALPHA)
        overlay_surf.fill((0, 0, 0, 160))
        surface.blit(overlay_surf, (0, 0))

        t1 = font_big.render(title, True, color)
        surface.blit(t1, t1.get_rect(center=(win_w // 2, win_h // 2 - 30)))
        if subtitle:
            t2 = font_med.render(subtitle, True, TEXT_COL)
            surface.blit(t2, t2.get_rect(center=(win_w // 2, win_h // 2 + 10)))
        t3 = font_small.render("R = reiniciar   ESC = menú", True, DIM_COL)
        surface.blit(t3, t3.get_rect(center=(win_w // 2, win_h // 2 + 45)))
        pygame.display.flip()

    snake, direction, apple, score = new_game()
    total_cells = cols * rows
    pending_dir = direction
    state = "playing"   # playing | won | lost

    move_timer = 0.0

    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return   # back to launcher

                if state != "playing":
                    if event.key == pygame.K_r:
                        snake, direction, apple, score = new_game()
                        pending_dir = direction
                        state = "playing"
                    continue

                if event.key in (pygame.K_UP,    pygame.K_w) and direction != DOWN:
                    pending_dir = UP
                if event.key in (pygame.K_DOWN,  pygame.K_s) and direction != UP:
                    pending_dir = DOWN
                if event.key in (pygame.K_LEFT,  pygame.K_a) and direction != RIGHT:
                    pending_dir = LEFT
                if event.key in (pygame.K_RIGHT, pygame.K_d) and direction != LEFT:
                    pending_dir = RIGHT

        if state == "playing":
            move_timer += dt
            if move_timer >= 1.0 / fps:
                move_timer = 0.0
                direction = pending_dir

                head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

                # Wall collision
                if not (0 <= head[0] < cols and 0 <= head[1] < rows):
                    state = "lost"
                    continue

                # Self collision
                if head in snake:
                    state = "lost"
                    continue

                snake.insert(0, head)

                if head == apple:
                    score += 1
                    apple = spawn_apple(snake, cols, rows)
                    if apple is None:
                        state = "won"
                        continue
                else:
                    snake.pop()

        # --- Draw ---
        surface.fill(BG)
        draw_grid()

        for i, seg in enumerate(snake):
            draw_cell(*seg, SNAKE_HEAD if i == 0 else SNAKE_BODY)

        if apple:
            draw_cell(*apple, APPLE_COL)

        draw_hud(score, total_cells)
        pygame.display.flip()

        if state == "won":
            overlay("¡GANASTE!", WIN_COL, f"Puntuación: {score}")
        elif state == "lost":
            overlay("GAME OVER", LOSE_COL, f"Puntuación: {score}")
