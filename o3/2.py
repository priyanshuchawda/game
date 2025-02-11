import pygame
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# --------------------------------------------------
# Player Class
# --------------------------------------------------
class Player:
    def __init__(self, x, y):
        self.image = pygame.Surface((50, 75))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 200      # Horizontal speed (pixels per second)
        self.gravity = 500    # Gravity acceleration (pixels per second squared)
        self.jump_strength = -300  # Upward velocity when jumping

    def update(self, dt, platforms):
        keys = pygame.key.get_pressed()
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
        else:
            self.vel_x = 0

        self.rect.x += self.vel_x * dt

        # Jumping (only if on the ground)
        if keys[pygame.K_SPACE]:
            for plat in platforms:
                if self.rect.bottom == plat.top:
                    self.vel_y = self.jump_strength
                    break

        # Apply gravity
        self.vel_y += self.gravity * dt
        self.rect.y += self.vel_y * dt

        # Simple collision with platforms (only vertical correction)
        for plat in platforms:
            if self.rect.colliderect(plat) and self.vel_y > 0:
                self.rect.bottom = plat.top
                self.vel_y = 0

    def draw(self, screen, scroll_x):
        # Draw player relative to camera scroll offset
        screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))

# --------------------------------------------------
# ParallaxLayer Class
# --------------------------------------------------
class ParallaxLayer:
    def __init__(self, image, speed):
        """
        image: Pygame Surface representing this background layer.
        speed: A value between 0 and 1. Lower speeds indicate layers that move slower (appear distant).
        """
        self.image = image
        self.speed = speed
        self.width = self.image.get_width()

    def draw(self, screen, scroll_x):
        # Calculate the horizontal offset for the layer.
        offset = - (scroll_x * self.speed) % self.width
        # Draw the image twice to cover wide screens with a seamless tiling effect.
        screen.blit(self.image, (offset - self.width, 0))
        screen.blit(self.image, (offset, 0))

# --------------------------------------------------
# Enemy Class
# --------------------------------------------------
class Enemy:
    def __init__(self, x, y):
        self.image = pygame.Surface((40, 40))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, dt):
        # Future enemy logic (e.g., patrolling) would go here.
        pass

    def draw(self, screen, scroll_x):
        screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))

# --------------------------------------------------
# Collectible Class
# --------------------------------------------------
class Collectible:
    def __init__(self, x, y):
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen, scroll_x):
        screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))

# --------------------------------------------------
# Main Game Loop
# --------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("2D Platformer with Parallax Scrolling")
    clock = pygame.time.Clock()

    # Create the player
    player = Player(100, 400)

    # Define level platform (a ground platform that spans the level's width)
    level_width = 2000
    ground = pygame.Rect(0, 500, level_width, 100)
    platforms = [ground]

    # --------------------------------------------------
    # Create Parallax Background Layers
    # --------------------------------------------------
    layers = []

    # Distant mountains layer (moves the slowest)
    mountains = pygame.Surface((1600, SCREEN_HEIGHT))
    mountains.fill((100, 100, 255))
    # Draw a simple mountain shape for visualization
    pygame.draw.polygon(mountains, (50, 50, 200), [(100, 400), (300, 250), (500, 400)])
    layers.append(ParallaxLayer(mountains, 0.2))

    # Mid-ground forest layer
    forest = pygame.Surface((1600, SCREEN_HEIGHT), pygame.SRCALPHA)
    forest.fill((0, 0, 0, 0))  # Transparent background
    # Draw simple tree trunks
    for i in range(0, 1600, 150):
        pygame.draw.rect(forest, (34, 139, 34), (i, 350, 30, 150))
    layers.append(ParallaxLayer(forest, 0.4))

    # Foreground details layer (moves faster than the other two)
    foreground = pygame.Surface((1600, SCREEN_HEIGHT), pygame.SRCALPHA)
    foreground.fill((0, 0, 0, 0))
    # Draw simple torches or bushes
    for i in range(0, 1600, 200):
        pygame.draw.circle(foreground, (200, 100, 50), (i + 50, 450), 20)
    layers.append(ParallaxLayer(foreground, 0.6))

    # --------------------------------------------------
    # Create Enemies and Collectibles
    # --------------------------------------------------
    enemies = [Enemy(600, 460)]
    collectibles = [Collectible(800, 460), Collectible(1200, 460)]

    scroll_x = 0

    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000  # Delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update game objects
        player.update(dt, platforms)
        for enemy in enemies:
            enemy.update(dt)

        # Compute camera scroll offset to center the player horizontally.
        scroll_x = player.rect.centerx - SCREEN_WIDTH // 2
        # Clamp scrolling so it doesn't show beyond the level boundaries.
        scroll_x = max(0, min(scroll_x, level_width - SCREEN_WIDTH))

        # Clear screen
        screen.fill(BLACK)

        # Draw each parallax background layer.
        for layer in layers:
            layer.draw(screen, scroll_x)

        # Draw ground (platform) with scroll offset.
        ground_rect = pygame.Rect(ground.x - scroll_x, ground.y, ground.width, ground.height)
        pygame.draw.rect(screen, (139, 69, 19), ground_rect)

        # Draw enemies and collectibles.
        for enemy in enemies:
            enemy.draw(screen, scroll_x)
        for collectible in collectibles:
            collectible.draw(screen, scroll_x)

        # Draw the player.
        player.draw(screen, scroll_x)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
