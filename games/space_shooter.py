"""
Space Shooter — juego para el Arcade Python Launcher.
Uso: mod.run(surface, clock, difficulty)
"""

import pygame
import random
import sys
import math

# ---------------------------------------------------------------------------
# Configuración por dificultad
# ---------------------------------------------------------------------------
DIFFICULTIES = {
    "Muy Fácil": {
        "enemy_speed": 1.5,
        "enemy_rate": 1.8,
        "bullet_speed": 8,
        "lives": 5,
        "fps": 60,
        "color": (100, 220, 100),
    },
    "Fácil": {
        "enemy_speed": 2.2,
        "enemy_rate": 1.4,
        "bullet_speed": 9,
        "lives": 4,
        "fps": 60,
        "color": (80, 200, 80),
    },
    "Medio": {
        "enemy_speed": 3.0,
        "enemy_rate": 1.0,
        "bullet_speed": 10,
        "lives": 3,
        "fps": 60,
        "color": (220, 200, 60),
    },
    "Difícil": {
        "enemy_speed": 4.0,
        "enemy_rate": 0.7,
        "bullet_speed": 11,
        "lives": 2,
        "fps": 60,
        "color": (220, 130, 50),
    },
    "Legendario": {
        "enemy_speed": 5.5,
        "enemy_rate": 0.45,
        "bullet_speed": 12,
        "lives": 1,
        "fps": 60,
        "color": (210, 60, 60),
    },
}

# Colores
BG_TOP = (5, 5, 20)
BG_BOT = (10, 10, 35)
PLAYER_COL = (80, 200, 255)
BULLET_COL = (255, 240, 80)
ENEMY_COLS = [(220, 60, 60), (200, 80, 200), (60, 200, 180), (220, 140, 40)]
TEXT_COL = (230, 230, 230)
DIM_COL = (100, 100, 140)
WIN_COL = (80, 230, 180)
LOSE_COL = (220, 80, 80)
STAR_COL = (200, 200, 240)
HUD_BG = (10, 10, 25)
SHIELD_COL = (80, 160, 255)
EXPL_COLS = [(255, 200, 60), (255, 140, 40), (220, 60, 30), (180, 30, 10)]

WIN_W, WIN_H = 700, 560
PANEL_H = 50
PLAY_H = WIN_H - PANEL_H

PLAYER_SPEED = 5
PLAYER_W, PLAYER_H = 36, 42


# ---------------------------------------------------------------------------
# Helpers de dibujo
# ---------------------------------------------------------------------------


def draw_ship(surf, x, y, color, scale=1.0):
    """Dibuja una nave triangular estilizada centrada en (x,y)."""
    w = int(PLAYER_W * scale)
    h = int(PLAYER_H * scale)
    pts = [
        (x, y - h // 2),  # punta superior
        (x - w // 2, y + h // 2),  # esquina izq inferior
        (x - w // 4, y + h // 4),  # entrante izq
        (x, y + h // 6),  # centro inferior
        (x + w // 4, y + h // 4),  # entrante der
        (x + w // 2, y + h // 2),  # esquina der inferior
    ]
    pygame.draw.polygon(surf, color, pts)
    # detalle: línea central
    pygame.draw.line(
        surf,
        (min(color[0] + 60, 255), min(color[1] + 60, 255), min(color[2] + 60, 255)),
        (x, y - h // 2 + 4),
        (x, y + h // 6),
        2,
    )


def draw_enemy(surf, x, y, color, kind=0, r=18):
    """Dibuja distintos tipos de enemigos."""
    if kind == 0:
        # Nave enemiga clásica (triángulo invertido)
        pts = [
            (x, y + r),
            (x - r, y - r // 2),
            (x - r // 3, y - r // 4),
            (x, y - r // 2),
            (x + r // 3, y - r // 4),
            (x + r, y - r // 2),
        ]
        pygame.draw.polygon(surf, color, pts)
    elif kind == 1:
        # Diamante
        pts = [(x, y - r), (x + r, y), (x, y + r), (x - r, y)]
        pygame.draw.polygon(surf, color, pts)
    elif kind == 2:
        # Hexágono
        pts = [
            (
                x + int(r * math.cos(math.radians(60 * i - 30))),
                y + int(r * math.sin(math.radians(60 * i - 30))),
            )
            for i in range(6)
        ]
        pygame.draw.polygon(surf, color, pts)
    else:
        # Cruz / X
        pygame.draw.rect(surf, color, (x - r, y - r // 3, r * 2, r // 1.5))
        pygame.draw.rect(surf, color, (x - r // 3, y - r, r // 1.5, r * 2))


def draw_gradient_bg(surf, stars):
    surf.fill(BG_TOP)
    # gradient suave
    for y in range(0, PLAY_H, 4):
        alpha = int(y / PLAY_H * 30)
        pygame.draw.line(surf, (10, 10, 35 + alpha), (0, y), (WIN_W, y))
    # estrellas
    for s in stars:
        pygame.draw.circle(surf, s[2], (s[0], s[1]), s[3])


# ---------------------------------------------------------------------------
# Clases
# ---------------------------------------------------------------------------


class Player:
    def __init__(self):
        self.x = WIN_W // 2
        self.y = PLAY_H - 50
        self.rect = pygame.Rect(
            self.x - PLAYER_W // 2, self.y - PLAYER_H // 2, PLAYER_W, PLAYER_H
        )
        self.shoot_cooldown = 0.0
        self.shoot_delay = 0.22  # segundos entre disparos
        self.shield_timer = 0.0  # invulnerabilidad tras golpe

    def update(self, dt, keys, bullet_speed):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += PLAYER_SPEED

        self.x = max(PLAYER_W // 2, min(WIN_W - PLAYER_W // 2, self.x))
        self.y = max(PLAYER_H // 2, min(PLAY_H - PLAYER_H // 2, self.y))

        self.rect.center = (self.x, self.y)
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        self.shield_timer = max(0, self.shield_timer - dt)

    def try_shoot(self, keys, bullets, bullet_speed):
        if (
            keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        ) and self.shoot_cooldown == 0:
            bullets.append(Bullet(self.x, self.y - PLAYER_H // 2, bullet_speed))
            self.shoot_cooldown = self.shoot_delay

    def draw(self, surf):
        if self.shield_timer > 0 and int(self.shield_timer * 10) % 2 == 0:
            return  # parpadeo de invulnerabilidad
        draw_ship(surf, self.x, self.y, PLAYER_COL)
        # motor (llama azul)
        pygame.draw.ellipse(
            surf, (60, 120, 255), (self.x - 6, self.y + PLAYER_H // 2 - 4, 12, 10)
        )


class Bullet:
    R = 5

    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.alive = True

    def update(self, dt):
        self.y -= self.speed
        if self.y < -10:
            self.alive = False

    def draw(self, surf):
        pygame.draw.ellipse(surf, BULLET_COL, (self.x - 3, self.y - 7, 6, 14))
        pygame.draw.ellipse(surf, (255, 255, 200), (self.x - 1, self.y - 5, 2, 8))


class Enemy:
    def __init__(self, x, y, speed, kind, wave):
        self.x = x
        self.y = y
        self.speed = speed + wave * 0.15
        self.kind = kind % 4
        self.color = ENEMY_COLS[self.kind]
        self.r = 18
        self.alive = True
        self.points = (self.kind + 1) * 10 + wave * 5
        # patrón de movimiento: algunos se mueven en zigzag
        self.zigzag = kind % 3 == 2
        self.ztime = random.uniform(0, math.pi * 2)

    @property
    def rect(self):
        return pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)

    def update(self, dt):
        self.y += self.speed
        if self.zigzag:
            self.ztime += dt * 2.5
            self.x += math.sin(self.ztime) * 1.5
            self.x = max(self.r, min(WIN_W - self.r, self.x))
        if self.y > PLAY_H + self.r:
            self.alive = False

    def draw(self, surf):
        draw_enemy(surf, int(self.x), int(self.y), self.color, self.kind, self.r)


class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = [
            {
                "vx": random.uniform(-3, 3),
                "vy": random.uniform(-4, 1),
                "r": random.randint(2, 6),
                "col": random.choice(EXPL_COLS),
                "life": random.uniform(0.3, 0.7),
            }
            for _ in range(18)
        ]
        self.alive = True

    def update(self, dt):
        for p in self.particles:
            p["life"] -= dt
            p["vx"] *= 0.92
            p["vy"] *= 0.92
        self.particles = [p for p in self.particles if p["life"] > 0]
        if not self.particles:
            self.alive = False

    def draw(self, surf):
        for p in self.particles:
            x = self.x + p["vx"] * 8
            y = self.y + p["vy"] * 8
            pygame.draw.circle(surf, p["col"], (int(x), int(y)), p["r"])


class Star:
    def __init__(self, speed_mult=1.0):
        self.x = random.randint(0, WIN_W)
        self.y = random.randint(0, PLAY_H)
        self.speed = random.uniform(0.3, 1.2) * speed_mult
        self.r = random.choice([1, 1, 1, 2])
        bright = random.randint(140, 255)
        self.col = (bright, bright, min(bright + 20, 255))

    def update(self):
        self.y += self.speed
        if self.y > PLAY_H:
            self.y = 0
            self.x = random.randint(0, WIN_W)

    def as_tuple(self):
        return (int(self.x), int(self.y), self.col, self.r)


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------


def run(surface: pygame.Surface, clock: pygame.time.Clock, difficulty: str):
    cfg = DIFFICULTIES[difficulty]
    enemy_speed = cfg["enemy_speed"]
    enemy_rate = cfg["enemy_rate"]  # segundos entre oleadas de enemigos
    bullet_speed = cfg["bullet_speed"]
    lives = cfg["lives"]
    diff_color = cfg["color"]

    surface = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption(f"Naves Espaciales — {difficulty}")

    font_big = pygame.font.SysFont("consolas", 34, bold=True)
    font_med = pygame.font.SysFont("consolas", 22)
    font_small = pygame.font.SysFont("consolas", 16)

    # --- Estrellas de fondo ---
    stars = [Star() for _ in range(90)]

    def new_game():
        return (
            Player(),
            [],  # bullets
            [],  # enemies
            [],  # explosions
            0,  # score
            lives,  # lives_left
            0,  # wave
            0.0,  # enemy_timer
            0.0,  # total_time
            "playing",
        )

    (
        player,
        bullets,
        enemies,
        explosions,
        score,
        lives_left,
        wave,
        enemy_timer,
        total_time,
        state,
    ) = new_game()

    def spawn_wave(wave):
        count = 4 + wave * 2
        count = min(count, 14)
        margin = 40
        xs = (
            [margin + (WIN_W - 2 * margin) / (count - 1) * i for i in range(count)]
            if count > 1
            else [WIN_W // 2]
        )
        new_enemies = []
        for i, x in enumerate(xs):
            kind = (wave + i) % 4
            new_enemies.append(Enemy(x, -30 - i * 15, enemy_speed, kind, wave))
        return new_enemies

    def draw_hud():
        hud_y = PLAY_H
        pygame.draw.rect(surface, HUD_BG, (0, hud_y, WIN_W, PANEL_H))
        pygame.draw.line(surface, (40, 40, 70), (0, hud_y), (WIN_W, hud_y), 1)

        # Vidas (iconos de nave)
        for i in range(lives_left):
            draw_ship(surface, 18 + i * 26, hud_y + 25, PLAYER_COL, scale=0.55)

        # Puntuación
        sc = font_med.render(f"Score: {score}", True, TEXT_COL)
        surface.blit(sc, sc.get_rect(centerx=WIN_W // 2, y=hud_y + 6))

        # Oleada + dificultad
        wv = font_small.render(f"Oleada {wave}  —  {difficulty}", True, diff_color)
        surface.blit(wv, wv.get_rect(right=WIN_W - 10, y=hud_y + 8))

        # Tiempo
        tm = font_small.render(f"{int(total_time)}s", True, DIM_COL)
        surface.blit(tm, tm.get_rect(right=WIN_W - 10, y=hud_y + 28))

    def overlay(title, color, subtitle=""):
        ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        surface.blit(ov, (0, 0))
        t1 = font_big.render(title, True, color)
        surface.blit(t1, t1.get_rect(center=(WIN_W // 2, WIN_H // 2 - 40)))
        if subtitle:
            t2 = font_med.render(subtitle, True, TEXT_COL)
            surface.blit(t2, t2.get_rect(center=(WIN_W // 2, WIN_H // 2 + 4)))
        t3 = font_small.render("R = reiniciar   ESC = menú", True, DIM_COL)
        surface.blit(t3, t3.get_rect(center=(WIN_W // 2, WIN_H // 2 + 38)))
        pygame.display.flip()

    # ---------- bucle principal ----------
    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if state != "playing" and event.key == pygame.K_r:
                    (
                        player,
                        bullets,
                        enemies,
                        explosions,
                        score,
                        lives_left,
                        wave,
                        enemy_timer,
                        total_time,
                        state,
                    ) = new_game()

        # --- Update ---
        if state == "playing":
            total_time += dt
            keys = pygame.key.get_pressed()
            player.update(dt, keys, bullet_speed)
            player.try_shoot(keys, bullets, bullet_speed)

            # Spawn oleada
            enemy_timer += dt
            if not enemies and enemy_timer >= enemy_rate:
                wave += 1
                enemies = spawn_wave(wave)
                enemy_timer = 0.0
            elif enemies:
                enemy_timer = 0.0

            # Mover balas
            for b in bullets:
                b.update(dt)
            bullets = [b for b in bullets if b.alive]

            # Mover enemigos
            for e in enemies:
                e.update(dt)
            # enemigo llega al fondo → pierde vida
            for e in enemies:
                if not e.alive and e.y > PLAY_H:
                    lives_left -= 1
                    explosions.append(Explosion(e.x, PLAY_H - 10))
            enemies = [e for e in enemies if e.alive and e.y <= PLAY_H + 20]

            # Colisiones bala–enemigo
            for b in bullets:
                for e in enemies:
                    if b.alive and e.alive and e.rect.collidepoint(b.x, b.y):
                        b.alive = False
                        e.alive = False
                        score += e.points
                        explosions.append(Explosion(e.x, e.y))
            bullets = [b for b in bullets if b.alive]
            enemies = [e for e in enemies if e.alive]

            # Colisión jugador–enemigo
            if player.shield_timer == 0:
                for e in enemies:
                    if e.alive and e.rect.colliderect(player.rect):
                        e.alive = False
                        lives_left -= 1
                        player.shield_timer = 2.0
                        explosions.append(Explosion(e.x, e.y))
                        break

            # Explosiones
            for ex in explosions:
                ex.update(dt)
            explosions = [ex for ex in explosions if ex.alive]

            # Estrellas
            for s in stars:
                s.update()

            # Comprobar fin
            if lives_left <= 0:
                lives_left = 0
                state = "lost"
            if score >= 9999:
                state = "won"

        # --- Draw ---
        star_tuples = [s.as_tuple() for s in stars]
        draw_gradient_bg(surface, star_tuples)

        for e in enemies:
            e.draw(surface)
        for b in bullets:
            b.draw(surface)
        for ex in explosions:
            ex.draw(surface)
        player.draw(surface)

        draw_hud()
        pygame.display.flip()

        if state == "won":
            overlay("¡VICTORIA!", WIN_COL, f"Score: {score}  —  Oleadas: {wave}")
        elif state == "lost":
            overlay("GAME OVER", LOSE_COL, f"Score: {score}  —  Oleadas: {wave}")
