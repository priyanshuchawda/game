import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
# Set the display mode to full screen using the FULLSCREEN flag
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Block Breaker Game")
clock = pygame.time.Clock()

# Fonts for text rendering
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)

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

def create_bricks():
    global bricks
    bricks = []
    for row in range(brick_rows):
        for col in range(brick_cols):
            brick_x = col * brick_width
            brick_y = row * brick_height + 50  # start 50 pixels from the top
            brick = pygame.Rect(brick_x, brick_y, brick_width - 2, brick_height - 2)
            bricks.append(brick)

create_bricks()

# Game state variables
lives = 3
paused = False
game_over = False

# Timing variables (in milliseconds)
start_time = pygame.time.get_ticks()
final_time = None  # Will store the time when the game ends

# Option for high speed ball
high_speed_mode = False

# Button properties
restart_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 50, 100, 50)
pause_button = pygame.Rect(WIDTH - 120, 10, 100, 40)
# High speed toggle button (positioned below the pause button)
speed_button = pygame.Rect(WIDTH - 120, 60, 100, 40)

def reset_ball_and_paddle():
    global ball_x, ball_y, ball_dx, ball_dy, paddle
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    base_speed = 6 if high_speed_mode else 4
    ball_dx = random.choice([-base_speed, base_speed])
    ball_dy = -base_speed
    paddle.x = WIDTH // 2 - paddle_width // 2

def reset_game():
    global lives, game_over, paused, start_time, final_time
    lives = 3
    game_over = False
    paused = False
    final_time = None
    reset_ball_and_paddle()
    create_bricks()
    start_time = pygame.time.get_ticks()

def update_ball_speed():
    """Update the current ball speed based on the high_speed_mode flag while preserving direction."""
    global ball_dx, ball_dy
    base_speed = 6 if high_speed_mode else 4
    ball_dx = base_speed if ball_dx > 0 else -base_speed
    ball_dy = base_speed if ball_dy > 0 else -base_speed

# Main game loop
running = True
while running:
    clock.tick(60)  # Run at 60 frames per second

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Key events for pause and restart
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p and not game_over:
                paused = not paused
            if event.key == pygame.K_r and game_over:
                reset_game()

        # Mouse button events
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Restart button (only when game over)
            if game_over and restart_button.collidepoint(mouse_pos):
                reset_game()
            # Pause button (only when game is active)
            if not game_over and pause_button.collidepoint(mouse_pos):
                paused = not paused
            # Speed toggle button (only when game is active)
            if not game_over and speed_button.collidepoint(mouse_pos):
                high_speed_mode = not high_speed_mode
                # Update ball speed immediately based on the new mode
                update_ball_speed()

    # Only update game logic if not paused and not game over
    if not paused and not game_over:
        # Handle paddle movement via keyboard
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.x -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.x += paddle_speed

        # Handle paddle movement via mouse
        mouse_x, _ = pygame.mouse.get_pos()
        paddle.x = mouse_x - paddle_width // 2
        if paddle.left < 0:
            paddle.left = 0
        if paddle.right > WIDTH:
            paddle.right = WIDTH

        # Move the ball
        ball_x += ball_dx
        ball_y += ball_dy

        # Wall collision (left/right)
        if ball_x - ball_radius < 0 or ball_x + ball_radius > WIDTH:
            ball_dx = -ball_dx

        # Collision with the top of the window
        if ball_y - ball_radius < 0:
            ball_dy = -ball_dy

        # Collision with the bottom (missed by paddle)
        if ball_y + ball_radius > HEIGHT:
            lives -= 1
            if lives > 0:
                reset_ball_and_paddle()
            else:
                game_over = True
                # Record final time only once when game is over
                if final_time is None:
                    final_time = pygame.time.get_ticks()

        # Paddle collision (simple check: ball hitting paddle from above)
        if paddle.collidepoint(ball_x, ball_y + ball_radius):
            ball_dy = -ball_dy

        # Brick collision detection
        ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius,
                                ball_radius * 2, ball_radius * 2)
        hit_index = ball_rect.collidelist(bricks)
        if hit_index != -1:
            del bricks[hit_index]
            ball_dy = -ball_dy

    # Drawing everything on the screen
    screen.fill(BLACK)

    # Draw game elements if not game over
    if not game_over:
        pygame.draw.rect(screen, BLUE, paddle)
        pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_radius)
        for brick in bricks:
            pygame.draw.rect(screen, RED, brick)

    # Display lives count
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(lives_text, (10, 10))

    # Draw the pause button (only if game is not over)
    if not game_over:
        pygame.draw.rect(screen, BLUE, pause_button)
        button_text = "Resume" if paused else "Pause"
        pause_text = font.render(button_text, True, WHITE)
        pause_text_rect = pause_text.get_rect(center=pause_button.center)
        screen.blit(pause_text, pause_text_rect)

        # Draw the speed toggle button
        pygame.draw.rect(screen, BLUE, speed_button)
        speed_text = "Normal" if high_speed_mode else "High"
        speed_label = font.render(speed_text, True, WHITE)
        speed_label_rect = speed_label.get_rect(center=speed_button.center)
        screen.blit(speed_label, speed_label_rect)

    # Pause overlay
    if paused and not game_over:
        pause_overlay = big_font.render("Paused", True, GREEN)
        pause_rect = pause_overlay.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(pause_overlay, pause_rect)

    # Game over overlay and restart button
    if game_over:
        over_text = big_font.render("Game Over", True, RED)
        over_rect = over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(over_text, over_rect)
        
        # Calculate and display elapsed time using the stored final_time
        elapsed_time = (final_time - start_time) / 1000  # seconds
        time_text = font.render(f"Time: {elapsed_time:.2f} seconds", True, WHITE)
        time_rect = time_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(time_text, time_rect)

        pygame.draw.rect(screen, BLUE, restart_button)
        restart_text = font.render("Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=restart_button.center)
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()

# Quit the game
pygame.quit()
sys.exit()
