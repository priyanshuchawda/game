import pygame
import random
import sys

# Constants
WIDTH, HEIGHT = 480, 640
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0)

class PlayerShip(pygame.sprite.Sprite):
    """Player spaceship sprite with movement and shooting capabilities."""
    def __init__(self, pos):
        super().__init__()
        # For now, we just create a simple polygon to represent the ship.
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, BLUE, [(0,30), (20,0), (40,30)])
        self.rect = self.image.get_rect(center=pos)
        self.speed = 5
        self.last_shot = pygame.time.get_ticks()
        self.shot_cooldown = 250  # milliseconds

    def update(self, keys_pressed=None):
        # Only update movement if keys_pressed is provided.
        if keys_pressed:
            if keys_pressed[pygame.K_LEFT]:
                self.rect.x -= self.speed
            if keys_pressed[pygame.K_RIGHT]:
                self.rect.x += self.speed
            if keys_pressed[pygame.K_UP]:
                self.rect.y -= self.speed
            if keys_pressed[pygame.K_DOWN]:
                self.rect.y += self.speed

        # Keep player within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shot_cooldown:
            self.last_shot = now
            return Laser(self.rect.centerx, self.rect.top)
        return None

class EnemyShip(pygame.sprite.Sprite):
    """Enemy ship sprite that drifts downward."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        # Simple pixel art style design for the enemy.
        self.image.fill(RED)
        pygame.draw.rect(self.image, YELLOW, (5, 5, 20, 20))
        self.rect = self.image.get_rect(center=(x, y))
        self.speedy = random.randint(1, 3)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

class Laser(pygame.sprite.Sprite):
    """Player laser shot sprite."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Particle(pygame.sprite.Sprite):
    """Particle sprite for laser effects and explosion debris."""
    def __init__(self, x, y, color):
        super().__init__()
        self.radius = random.randint(2, 4)
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.speedx = random.uniform(-2, 2)
        self.speedy = random.uniform(-2, 2)
        self.life = random.randint(20, 40)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        self.life -= 1
        if self.life <= 0:
            self.kill()

def draw_background(screen, offset):
    """
    Draws a simple scrolling starfield background.
    In a full game you might want to load a pixel art nebula background.
    """
    screen.fill(BLACK)
    # Draw stars at random positions; offset makes the field look like it's scrolling.
    for i in range(50):  # 50 stars
        x = random.randrange(0, WIDTH)
        y = (random.randrange(0, HEIGHT) + offset) % HEIGHT
        pygame.draw.circle(screen, WHITE, (x, y), 1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Retro Arcade Space Shooter")
    clock = pygame.time.Clock()

    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    laser_group = pygame.sprite.Group()
    particle_group = pygame.sprite.Group()

    # Create the player
    player = PlayerShip((WIDTH // 2, HEIGHT - 50))
    all_sprites.add(player)

    score = 0
    enemy_spawn_event = pygame.USEREVENT + 1
    pygame.time.set_timer(enemy_spawn_event, 1000)  # spawn an enemy every second

    background_offset = 0
    running = True

    while running:
        clock.tick(FPS)
        background_offset += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == enemy_spawn_event:
                x = random.randint(20, WIDTH - 20)
                enemy = EnemyShip(x, -20)
                all_sprites.add(enemy)
                enemy_group.add(enemy)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    laser = player.shoot()
                    if laser:
                        all_sprites.add(laser)
                        laser_group.add(laser)
                        # Create a brief particle effect at the laser's starting location.
                        for _ in range(5):
                            particle = Particle(laser.rect.centerx, laser.rect.centery, GREEN)
                            all_sprites.add(particle)
                            particle_group.add(particle)

        keys_pressed = pygame.key.get_pressed()
        player.update(keys_pressed)

        all_sprites.update()

        # Check for laser collisions with enemies.
        hits = pygame.sprite.groupcollide(enemy_group, laser_group, True, True)
        for hit in hits:
            score += 10
            # Spawn particles to simulate an explosion.
            for _ in range(20):
                particle = Particle(hit.rect.centerx, hit.rect.centery, RED)
                all_sprites.add(particle)
                particle_group.add(particle)

        # Check for collisions between the player and enemies.
        if pygame.sprite.spritecollideany(player, enemy_group):
            # Create an explosion effect for the player's ship.
            for _ in range(30):
                particle = Particle(player.rect.centerx, player.rect.centery, YELLOW)
                all_sprites.add(particle)
                particle_group.add(particle)
            running = False

        draw_background(screen, background_offset)
        all_sprites.draw(screen)

        # Draw the score on screen.
        font = pygame.font.SysFont("Arial", 20)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
