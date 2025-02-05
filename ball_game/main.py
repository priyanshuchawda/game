import pygame
import math
import sys
import os

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
CENTER = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Pygame Physics Simulation")

# Clock for FPS control
clock = pygame.time.Clock()
FPS = 60

# Colors
BG_COLOR = (10, 10, 30)
HEX_COLOR = (0, 255, 255)
GLOW_COLOR = (0, 150, 150)
BALL_COLOR = (255, 100, 100)
TRAIL_COLOR = (255, 150, 150)

# Physics constants
GRAVITY = pygame.Vector2(0, 0.5)  # pixels per frame^2
DRAG_COEFF = 0.99  # air resistance
FRICTION = 0.98  # friction on collision contact
BOUNCE_RESTITUTION = 0.8  # energy loss on impact

# Global toggle for gravity
gravity_on = True

# Sound (optional): Ensure you have a "bounce.wav" in the same directory
if os.path.exists("bounce.wav"):
    bounce_sound = pygame.mixer.Sound("bounce.wav")
else:
    bounce_sound = None

# Helper function to compute the perpendicular of a vector
def perpendicular(vec):
    return pygame.Vector2(-vec.y, vec.x)

class Ball:
    def __init__(self, pos, radius=15):
        self.pos = pygame.Vector2(pos)
        self.radius = radius
        self.vel = pygame.Vector2(3, -2)
        self.acc = pygame.Vector2(0, 0)
        self.elasticity = 0.8  # can be adjusted with mouse scroll
        self.trail = []  # store previous positions for trailing effect

    def apply_force(self, force):
        self.acc += force

    def update(self):
        # Apply gravity if enabled
        if gravity_on:
            self.apply_force(GRAVITY)

        # Air resistance
        self.vel *= DRAG_COEFF

        # Update velocity and position
        self.vel += self.acc
        self.pos += self.vel
        self.acc = pygame.Vector2(0, 0)

        # Record trail
        self.trail.append(self.pos.copy())
        if len(self.trail) > 15:
            self.trail.pop(0)

    def draw(self, surface):
        # Draw trailing effect
        if len(self.trail) > 1:
            for i in range(1, len(self.trail)):
                alpha = int(255 * i / len(self.trail))
                color = (TRAIL_COLOR[0], TRAIL_COLOR[1], TRAIL_COLOR[2], alpha)
                # Create a surface with per-pixel alpha for trail segments
                trail_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, color, (self.radius, self.radius), self.radius)
                surface.blit(trail_surf, (self.trail[i].x - self.radius, self.trail[i].y - self.radius))
        # Draw ball
        pygame.draw.circle(surface, BALL_COLOR, (int(self.pos.x), int(self.pos.y)), self.radius)

    def reset(self, pos):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(3, -2)
        self.acc = pygame.Vector2(0, 0)
        self.trail = []

class Hexagon:
    def __init__(self, center, radius=250):
        self.center = pygame.Vector2(center)
        self.radius = radius
        self.rotation = 0  # in radians
        self.rotation_speed = 0.01  # radians per frame

    def update(self):
        self.rotation += self.rotation_speed

    def get_vertices(self):
        vertices = []
        for i in range(6):
            angle = self.rotation + math.radians(60 * i)
            x = self.center.x + self.radius * math.cos(angle)
            y = self.center.y + self.radius * math.sin(angle)
            vertices.append(pygame.Vector2(x, y))
        return vertices

    def draw(self, surface):
        vertices = self.get_vertices()
        # Draw glowing edges: first draw a thicker semi-transparent line behind
        glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(glow_surf, (*GLOW_COLOR, 100), vertices, width=8)
        surface.blit(glow_surf, (0, 0))
        # Draw main hexagon
        pygame.draw.polygon(surface, HEX_COLOR, vertices, width=3)

def point_line_distance(point, line_start, line_end):
    # Compute the distance from a point to a line segment
    line = line_end - line_start
    if line.length() == 0:
        return (point - line_start).length(), line_start
    t = max(0, min(1, (point - line_start).dot(line) / line.length_squared()))
    projection = line_start + t * line
    distance = (point - projection).length()
    return distance, projection

def handle_collision(ball, hexagon):
    vertices = hexagon.get_vertices()
    collided = False
    # Check collision with each edge of the hexagon
    for i in range(len(vertices)):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % len(vertices)]
        distance, closest_point = point_line_distance(ball.pos, p1, p2)
        if distance < ball.radius:
            collided = True
            # Compute the normal of the edge
            edge = p2 - p1
            normal = perpendicular(edge).normalize()

            # Determine the wall's velocity at the collision point due to hexagon rotation.
            # (Assuming rotation about the center)
            r_vec = closest_point - hexagon.center
            # The tangential velocity is perpendicular to r_vec.
            wall_tangent = perpendicular(r_vec).normalize()
            wall_velocity = wall_tangent * hexagon.rotation_speed * r_vec.length()

            # Compute relative velocity (ball relative to wall)
            relative_vel = ball.vel - wall_velocity

            # Reflect the relative velocity about the normal:
            # v' = v - 2*(v dot n)*n
            dot = relative_vel.dot(normal)
            reflection = relative_vel - 2 * dot * normal

            # Add back the wall velocity
            ball.vel = (reflection + wall_velocity) * ball.elasticity

            # Apply friction effect along the wall tangent
            tangent_component = ball.vel.dot(wall_tangent)
            ball.vel -= wall_tangent * (1 - FRICTION) * tangent_component

            # Adjust ball position to prevent sinking into the wall:
            overlap = ball.radius - distance
            ball.pos += normal * overlap

            if bounce_sound:
                bounce_sound.play()
    return collided

def reset_simulation(ball):
    ball.reset(CENTER)

def main():
    global gravity_on
    # Create instances
    ball = Ball(CENTER)
    hexagon = Hexagon(CENTER)

    dragging = False  # track mouse dragging
    offset = pygame.Vector2(0, 0)  # offset from ball center during dragging

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Keyboard controls
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    hexagon.rotation_speed -= 0.005
                if event.key == pygame.K_RIGHT:
                    hexagon.rotation_speed += 0.005
                if event.key == pygame.K_SPACE:
                    gravity_on = not gravity_on
                if event.key == pygame.K_r:
                    reset_simulation(ball)
                # Toggle rotation direction with 'd' key
                if event.key == pygame.K_d:
                    hexagon.rotation_speed = -hexagon.rotation_speed

            # Mouse controls: dragging the ball
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.Vector2(event.pos)
                # Left click to drag
                if event.button == 1:
                    if (mouse_pos - ball.pos).length() < ball.radius:
                        dragging = True
                        offset = ball.pos - mouse_pos
                # Mouse wheel to adjust elasticity
                if event.button == 4:  # scroll up
                    ball.elasticity = min(1.0, ball.elasticity + 0.05)
                if event.button == 5:  # scroll down
                    ball.elasticity = max(0.5, ball.elasticity - 0.05)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

        if dragging:
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            ball.pos = mouse_pos + offset
            ball.vel = pygame.Vector2(0, 0)  # reset velocity when repositioning

        # Update physics and objects
        if not dragging:
            ball.update()
        hexagon.update()

        # Handle collisions with the rotating hexagon
        handle_collision(ball, hexagon)

        # Simple boundary conditions (if the ball goes off-screen, wrap it around)
        if ball.pos.x < 0: ball.pos.x = WIDTH
        if ball.pos.x > WIDTH: ball.pos.x = 0
        if ball.pos.y < 0: ball.pos.y = HEIGHT
        if ball.pos.y > HEIGHT: ball.pos.y = 0

        # Rendering
        screen.fill(BG_COLOR)
        hexagon.draw(screen)
        ball.draw(screen)

        # Display info (optional)
        font = pygame.font.SysFont("Arial", 18)
        info_text = f"Rotation Speed: {hexagon.rotation_speed:.3f} | Gravity: {'On' if gravity_on else 'Off'} | Elasticity: {ball.elasticity:.2f}"
        text_surf = font.render(info_text, True, (255, 255, 255))
        screen.blit(text_surf, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
