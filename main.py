import pygame
import random
from pygame.math import Vector2

# --- CONFIG ---
class Config:
    # Screen & world
    WIDTH, HEIGHT        = 800, 600
    WORLD_WIDTH, WORLD_HEIGHT = 2000, 1500
    MIN_ZOOM, MAX_ZOOM, ZOOM_STEP = 0.5, 2.0, 0.1

    # Player
    PLAYER_RADIUS        = 10
    PLAYER_SPEED         = 5
    STAMINA_MAX          = 100.0
    STAMINA_DECAY        = 0.05
    STAMINA_WATER        = 30.0
    STAMINA_REGEN        = 0.1

    # Werm
    WERM_RADIUS          = 25
    WERM_MAX_SPEED       = 4.0
    WERM_ACCEL           = 0.3
    WERM_MIN_DIST        = 300
    WERM_INACTIVE_FRAMES = 60

    # Environment objects
    NUM_ROCKS, ROCK_RANGE       = 20, (60, 100)
    NUM_WATERS, WATER_SIZE      = 10, 25
    NUM_VILLAGES, VILLAGE_RANGE = 5,  (100, 150)

# --- COLORS ---
class Palette:
    TOP_SAND     = (220,185,150)
    BOTTOM_SAND  = (255,220,190)
    ROCK         = (100,100,100)
    WATER        = (0,150,255)
    VILLAGE      = (200,150,100)
    PLAYER       = (0,100,255)
    WERM         = (139,69,19)
    TEXT         = (0,0,0)
    SHADOW       = (50,50,50)

# --- UTILITIES ---
def clamp(v, lo, hi): return max(lo, min(v, hi))

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def world_to_screen(pos, cam, zoom):
    return ((pos.x - cam.x) * zoom + Config.WIDTH/2,
            (pos.y - cam.y) * zoom + Config.HEIGHT/2)

def cast_sensor(pos, direction, length, obstacles):
    step = 5
    max_steps = int(length/step)
    for i in range(1, max_steps+1):
        p = pos + direction * step * i
        for o in obstacles:
            center = Vector2(o.x + o.w/2, o.y + o.h/2)
            if p.distance_to(center) < max(o.w, o.h)/2:
                return i / max_steps
    return 1.0

# --- WERM ENTITY ---
class Werm:
    def __init__(self):
        self.pos     = Vector2(-9999, -9999)
        self.vel     = Vector2()
        self.active  = False
        self.visible = False
        self.timer   = 0

    def steer(self, target, obstacles):
        desired = (target - self.pos).normalize()
        self.vel += desired * Config.WERM_ACCEL

        forward = self.vel.normalize() if self.vel.length() else desired
        clears  = []
        for angle in (0, 30, -30):
            clears.append(
                cast_sensor(self.pos, forward.rotate(angle), 200, obstacles)
            )

        for clr, angle in zip(clears, (0,30,-30)):
            if clr < 1:
                perp = forward.rotate(angle + 90)
                self.vel += perp * (1-clr) * 1.5

        if self.vel.length() > Config.WERM_MAX_SPEED:
            self.vel.scale_to_length(Config.WERM_MAX_SPEED)

    def update(self, player, obstacles, moved):
        if moved:
            if not self.active:
                self.pos     = self._spawn_away(player)
                self.active  = self.visible = True
                self.timer   = 0
            else:
                self.timer = 0
        else:
            self.timer += 1
            if self.timer > Config.WERM_INACTIVE_FRAMES:
                self.active = self.visible = False

        if self.active and self.visible:
            self.steer(player, obstacles)
            self.pos += self.vel

            # keep in bounds
            r = Config.WERM_RADIUS
            self.pos.x = clamp(self.pos.x, r, Config.WORLD_WIDTH - r)
            self.pos.y = clamp(self.pos.y, r, Config.WORLD_HEIGHT - r)

            # collision with player
            if self.pos.distance_to(player) < (r + Config.PLAYER_RADIUS):
                return True
        return False

    def _spawn_away(self, player):
        for _ in range(50):
            off = Vector2(random.uniform(-600,600),
                          random.uniform(-600,600))
            p   = player + off
            r   = Config.WERM_RADIUS
            p.x = clamp(p.x, r, Config.WORLD_WIDTH  - r)
            p.y = clamp(p.y, r, Config.WORLD_HEIGHT - r)
            if p.distance_to(player) >= Config.WERM_MIN_DIST:
                return p
        return player

# --- MAIN GAME ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption("Lune Werm Survivor")
        self.clock  = pygame.time.Clock()
        self.font   = pygame.font.SysFont(None, 20)

        self.player  = Vector2(Config.WORLD_WIDTH/2, Config.WORLD_HEIGHT/2)
        self.stamina = Config.STAMINA_MAX
        self.zoom    = 1.0
        self.start   = pygame.time.get_ticks()
        self.game_over = False

        # pre-render gradient
        self.bg = pygame.Surface((Config.WIDTH, Config.HEIGHT))
        for y in range(Config.HEIGHT):
            color = lerp(Palette.TOP_SAND, Palette.BOTTOM_SAND, y/Config.HEIGHT)
            pygame.draw.line(self.bg, color, (0,y), (Config.WIDTH,y))

        # spawn world
        self.obstacles = []
        self.rocks     = self._spawn(Config.NUM_ROCKS, Config.ROCK_RANGE)
        self.waters    = self._spawn(Config.NUM_WATERS, (Config.WATER_SIZE,)*2)
        self.villages  = self._spawn(Config.NUM_VILLAGES, Config.VILLAGE_RANGE)

        self.werms = [Werm() for _ in range(3)]

    def _spawn(self, count, size_range):
        items = []
        for _ in range(count):
            for _ in range(100):
                w = random.randint(*size_range)
                x = random.uniform(0, Config.WORLD_WIDTH - w)
                y = random.uniform(0, Config.WORLD_HEIGHT - w)
                rect = pygame.Rect(x, y, w, w)
                if not any(rect.colliderect(o) for o in self.obstacles):
                    self.obstacles.append(rect)
                    items.append(rect)
                    break
        return items

    def run(self):
        # Intro screen
        showing_intro = True
        while showing_intro:
            for e in pygame.event.get():
                if e.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    showing_intro = False
            self.screen.fill((0,0,0))
            lines = [
                "LUNE WERM: SURVIVOR",
                "",
                "Controls:",
                "  Arrow keys to move",
                "  Mouse wheel to zoom",
                "",
                "Collect water (blue), visit villages (regen),",
                "avoid the werms!",
                "",
                "Press any key to start"
            ]
            for i, text in enumerate(lines):
                surf = self.font.render(text, True, (255,255,255))
                self.screen.blit(surf, (50, 50 + i*28))
            pygame.display.flip()
            self.clock.tick(30)

        # Main loop
        while True:
            dt = self.clock.tick(60)
            moved = False
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.MOUSEBUTTONDOWN and e.button in (4,5):
                    self.zoom += Config.ZOOM_STEP if e.button==4 else -Config.ZOOM_STEP
                    self.zoom = clamp(self.zoom, Config.MIN_ZOOM, Config.MAX_ZOOM)

            # player movement
            keys = pygame.key.get_pressed()
            dx, dy = keys[pygame.K_RIGHT]-keys[pygame.K_LEFT], keys[pygame.K_DOWN]-keys[pygame.K_UP]
            if dx or dy:
                moved = True
                dir_vec = Vector2(dx, dy)
                dir_vec.scale_to_length(Config.PLAYER_SPEED)
                self.player += dir_vec
                r = Config.PLAYER_RADIUS
                self.player.x = clamp(self.player.x, r, Config.WORLD_WIDTH - r)
                self.player.y = clamp(self.player.y, r, Config.WORLD_HEIGHT - r)
                self.stamina -= Config.STAMINA_DECAY
                self.game_over |= (self.stamina <= 0)

            # update werms
            for w in self.werms:
                if w.update(self.player, self.rocks + self.villages, moved):
                    self.game_over = True

            # water pickups
            for wat in self.waters[:]:
                if wat.collidepoint(self.player.x, self.player.y):
                    self.stamina = min(self.stamina + Config.STAMINA_WATER, Config.STAMINA_MAX)
                    self.waters.remove(wat)

            # village regen
            if any(v.collidepoint(self.player.x, self.player.y) for v in self.villages):
                self.stamina = min(self.stamina + Config.STAMINA_REGEN, Config.STAMINA_MAX)

            # draw
            self.screen.blit(self.bg, (0,0))
            for color, group in ((Palette.ROCK, self.rocks),(Palette.WATER, self.waters),(Palette.VILLAGE, self.villages)):
                for r in group:
                    pos = world_to_screen(Vector2(r.x, r.y), self.player, self.zoom)
                    pygame.draw.rect(self.screen, color, (*pos, r.w*self.zoom, r.h*self.zoom))

            # draw werms
            for w in self.werms:
                if w.visible:
                    p = world_to_screen(w.pos, self.player, self.zoom)
                    pygame.draw.circle(self.screen, Palette.WERM, (int(p[0]), int(p[1])), int(Config.WERM_RADIUS*self.zoom))

            # draw player shadow & player
            p_scr = world_to_screen(self.player, self.player, self.zoom)
            shadow = (p_scr[0]+4, p_scr[1]+4)
            pygame.draw.circle(self.screen, Palette.SHADOW, (int(shadow[0]), int(shadow[1])), int(Config.PLAYER_RADIUS*self.zoom))
            pygame.draw.circle(self.screen, Palette.PLAYER,  (int(p_scr[0]), int(p_scr[1])), int(Config.PLAYER_RADIUS*self.zoom))

            # UI: stamina
            pygame.draw.rect(self.screen, (255,0,0), (10,40,100,10))
            pygame.draw.rect(self.screen, (0,255,0), (10,40,100*(self.stamina/Config.STAMINA_MAX),10))
            # UI: timer
            elapsed = (pygame.time.get_ticks()-self.start)//1000
            self.screen.blit(self.font.render(f"Time: {elapsed}s",True,Palette.TEXT),(10,10))

            # game over
            if self.game_over:
                over = self.font.render("Game Over! Press R to restart",True, Palette.TEXT)
                self.screen.blit(over,(Config.WIDTH//2-100,Config.HEIGHT//2))
                if pygame.key.get_pressed()[pygame.K_r]: self.__init__()

            pygame.display.flip()

if __name__ == "__main__":
    Game().run()

