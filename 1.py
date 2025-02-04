import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Breaker Game")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)

# Paddle properties
paddle_width = 100
paddle_height = 15
paddle_speed = 7
paddle = pygame.Rect(WIDTH // 2 - paddle_width // 2, HEIGHT - 40, paddle_width, paddle_height)

# Ball properties
ball_radius = 10
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_dx = 4
ball_dy = -4

# Brick properties and layout
brick_rows = 5
brick_cols = 10
brick_width = WIDTH // brick_cols
brick_height = 30
bricks = []

# Create bricks in a grid with a little gap between them
for row in range(brick_rows):
    for col in range(brick_cols):
        brick_x = col * brick_width
        brick_y = row * brick_height + 50  # start 50 pixels from the top
        brick = pygame.Rect(brick_x, brick_y, brick_width - 2, brick_height - 2)
        bricks.append(brick)

# Main game loop
running = True
while running:
    clock.tick(60)  # Run at 60 frames per second

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.x -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.x += paddle_speed

    # Move the ball
    ball_x += ball_dx
    ball_y += ball_dy

    # Wall collision (left/right)
    if ball_x - ball_radius < 0 or ball_x + ball_radius > WIDTH:
        ball_dx = -ball_dx

    # Collision with the top of the window
    if ball_y - ball_radius < 0:
        ball_dy = -ball_dy

    # Collision with the bottom of the window (missed by the paddle)
    if ball_y + ball_radius > HEIGHT:
        # Reset the ball and paddle positions
        ball_x, ball_y = WIDTH // 2, HEIGHT // 2
        ball_dx = random.choice([-4, 4])
        ball_dy = -4
        paddle.x = WIDTH // 2 - paddle_width // 2

    # Paddle collision (simple check: if the ball is hitting the paddle from above)
    if paddle.collidepoint(ball_x, ball_y + ball_radius):
        ball_dy = -ball_dy

    # Brick collision detection
    ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius * 2, ball_radius * 2)
    hit_index = ball_rect.collidelist(bricks)
    if hit_index != -1:
        # Remove the hit brick and reverse the ball's vertical direction
        del bricks[hit_index]
        ball_dy = -ball_dy

    # Drawing everything on the screen
    screen.fill(BLACK)
    pygame.draw.rect(screen, BLUE, paddle)
    pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_radius)
    for brick in bricks:
        pygame.draw.rect(screen, RED, brick)

    pygame.display.flip()

# Quit the game
pygame.quit()
sys.exit()
