import pygame
import sys
import math  # Needed for mouse-driven movement calculations

# Constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32
FPS = 60

# A simple level layout using characters:
# "1" represents a wall, and "." represents floor.
level_layout = [
    "111111111111111111111",
    "1...........1.......1",
    "1.11111.111.1.1111..1",
    "1.1...1...1...1..1.1",
    "1.1...11111..1...1.1",
    "1..................1",
    "11111111111111111111"
]

class DungeonMap:
    """
    DungeonMap manages the grid-based level layout.
    It creates simple surfaces for floor and wall tiles.
    """
    def __init__(self, layout):
        self.layout = layout
        self.width = len(layout[0])
        self.height = len(layout)
        # Create tile surfaces. In a full game, you might load assets here.
        self.floor_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.floor_tile.fill((50, 50, 50))  # Dark gray for floor

        self.wall_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.wall_tile.fill((100, 100, 100))  # Lighter gray for walls

    def draw(self, surface):
        for y, row in enumerate(self.layout):
            for x, tile in enumerate(row):
                if tile == '1':
                    surface.blit(self.wall_tile, (x * TILE_SIZE, y * TILE_SIZE))
                else:
                    surface.blit(self.floor_tile, (x * TILE_SIZE, y * TILE_SIZE))

class Player(pygame.sprite.Sprite):
    """
    The Player sprite handles movement and collision.
    Supports both keyboard (arrow keys) and mouse/touch movement.
    """
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((0, 255, 0))  # Green
        self.rect = self.image.get_rect(topleft=pos)
        self.speed = 3
        # Used to store a target point (set by mouse/touch input)
        self.target = None

    def update(self, keys_pressed, dungeon, dt=0):
        dx = 0
        dy = 0

        # Check keyboard input first.
        if keys_pressed[pygame.K_LEFT]:
            dx = -self.speed
        if keys_pressed[pygame.K_RIGHT]:
            dx = self.speed
        if keys_pressed[pygame.K_UP]:
            dy = -self.speed
        if keys_pressed[pygame.K_DOWN]:
            dy = self.speed

        if dx != 0 or dy != 0:
            # If keyboard movement is used, cancel any mouse/touch target.
            self.target = None
            self.move(dx, dy, dungeon)
        elif self.target is not None:
            # Move toward the target position (from a mouse/finger tap)
            target_dx = self.target[0] - self.rect.centerx
            target_dy = self.target[1] - self.rect.centery
            distance = math.hypot(target_dx, target_dy)
            if distance < self.speed:
                # If close enough, snap to target and cancel further movement.
                self.rect.center = self.target
                self.target = None
            else:
                # Normalize the vector and move the player a bit.
                dx = (target_dx / distance) * self.speed
                dy = (target_dy / distance) * self.speed
                self.move(int(round(dx)), int(round(dy)), dungeon)

    def move(self, dx, dy, dungeon):
        # Move horizontally first
        self.rect.x += dx
        if self.collide_walls(dungeon):
            self.rect.x -= dx
        # Then move vertically
        self.rect.y += dy
        if self.collide_walls(dungeon):
            self.rect.y -= dy

    def collide_walls(self, dungeon):
        """
        Checks collision by inspecting nearby tiles based on the dungeon layout.
        """
        x = self.rect.x // TILE_SIZE
        y = self.rect.y // TILE_SIZE

        for row in range(y - 1, y + 2):
            for col in range(x - 1, x + 2):
                if row < 0 or col < 0 or row >= dungeon.height or col >= dungeon.width:
                    continue
                if dungeon.layout[row][col] == '1':
                    tile_rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if self.rect.colliderect(tile_rect):
                        return True
        return False

class Enemy(pygame.sprite.Sprite):
    """
    The Enemy sprite uses multiple frames to simulate animation.
    """
    def __init__(self, pos):
        super().__init__()
        self.images = []
        # Create a list of surfaces for animation frames.
        for i in range(3):
            img = pygame.Surface((TILE_SIZE, TILE_SIZE))
            img.fill((255, 0, 0))  # Red square for enemy base
            # Draw a simple circle detail on each frame.
            pygame.draw.circle(img, (0, 0, 0), (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 4)
            self.images.append(img)
        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect(topleft=pos)
        self.animation_timer = 0
        self.animation_delay = 200  # milliseconds delay between frames

    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.images)
            self.image = self.images[self.current_frame]

class Game:
    """
    The Game class ties everything together: initializing pygame, handling the main loop,
    drawing the map, sprites, and overlaying lighting effects.
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Top-Down Dungeon Crawler")
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize the dungeon map.
        self.dungeon = DungeonMap(level_layout)

        # Create the player sprite and add it to a sprite group.
        self.player = Player(pos=(TILE_SIZE, TILE_SIZE))
        self.player_group = pygame.sprite.Group(self.player)

        # Create some enemy sprites.
        self.enemies = pygame.sprite.Group()
        enemy_positions = [(TILE_SIZE * 5, TILE_SIZE * 3), (TILE_SIZE * 10, TILE_SIZE * 2)]
        for pos in enemy_positions:
            enemy = Enemy(pos)
            self.enemies.add(enemy)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # Handle mouse or finger taps.
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Set the player's target to the clicked/tapped position.
                self.player.target = event.pos

    def update(self, dt):
        keys_pressed = pygame.key.get_pressed()
        # Pass dt if needed for future adjustments.
        self.player.update(keys_pressed, self.dungeon, dt)
        for enemy in self.enemies:
            enemy.update(dt)

    def draw(self):
        # Draw the dungeon map.
        self.dungeon.draw(self.screen)

        # Draw sprites.
        self.player_group.draw(self.screen)
        self.enemies.draw(self.screen)

        # Apply lighting effects.
        self.apply_lighting()

        pygame.display.flip()

    def apply_lighting(self):
        """
        Creates a dark translucent overlay and then "carves out" a lighted circle around the player
        to simulate a torch or dynamic light effect.
        """
        overlay = pygame.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark overlay with some transparency

        # Parameters for the light mask (e.g., torch radius)
        light_radius = 100
        light = pygame.Surface((light_radius * 2, light_radius * 2), flags=pygame.SRCALPHA)
        # Build a radial gradient to simulate diminishing light intensity.
        for i in range(light_radius * 2):
            for j in range(light_radius * 2):
                dx = i - light_radius
                dy = j - light_radius
                distance = math.hypot(dx, dy)
                if distance <= light_radius:
                    # The closer to the center, the lower the alpha value to "remove" darkness.
                    alpha = max(0, 255 - int((distance / light_radius) * 255))
                    light.set_at((i, j), (0, 0, 0, alpha))
        # Blit the "light" onto the overlay subtractively.
        overlay.blit(
            light,
            (self.player.rect.centerx - light_radius, self.player.rect.centery - light_radius),
            special_flags=pygame.BLEND_RGBA_SUB,
        )
        self.screen.blit(overlay, (0, 0))

if __name__ == "__main__":
    game = Game()
    game.run()