import pygame
import math
import sys

# ------------------
# Configuration
# ------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

BALL_RADIUS = 15
GRAVITY = 0.5
AIR_FRICTION = 0.995
RESTITUTION = 0.8  # bounce energy retention

HEX_RADIUS = 250
HEX_CENTER = (WIDTH // 2, HEIGHT // 2)
ANGULAR_VELOCITY = 0.02
initial_hex_angle = 0.0

WALL_FRICTION = 0.9

# ------------------
# Vector Helper Functions
# ------------------
def vector_add(a, b):
    return (a[0] + b[0], a[1] + b[1])

def vector_sub(a, b):
    return (a[0] - b[0], a[1] - b[1])

def vector_mul(a, scalar):
    return (a[0] * scalar, a[1] * scalar)

def vector_length(v):
    return math.hypot(v[0], v[1])

def vector_normalize(v):
    len_v = vector_length(v)
    if len_v == 0:
        return (0, 0)
    return (v[0] / len_v, v[1] / len_v)

def perpendicular(v):
    return (-v[1], v[0])

def reflect_velocity(v, n):
    dot = v[0] * n[0] + v[1] * n[1]
    return (v[0] - 2 * dot * n[0], v[1] - 2 * dot * n[1])

# ------------------
# Hexagon and Rotation Helpers
# ------------------
def compute_hexagon_vertices(center, radius, angle_offset):
    cx, cy = center
    vertices = []
    for i in range(6):
        angle = angle_offset + i * (2 * math.pi / 6)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        vertices.append((x, y))
    return vertices

def closest_point_on_segment(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    ab = (bx - ax, by - ay)
    ab_len_sq = ab[0]**2 + ab[1]**2
    if ab_len_sq == 0:
        return a
    t = ((px - ax) * ab[0] + (py - ay) * ab[1]) / ab_len_sq
    t = max(0, min(1, t))
    return (ax + t * ab[0], ay + t * ab[1])

# ------------------
# Pygame Initialization
# ------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in a Spinning Hexagon")
clock = pygame.time.Clock()

# ------------------
# Initial Conditions
# ------------------
ball_pos = [WIDTH // 2, HEIGHT // 2 - 100]
ball_vel = [5, 0]
hex_angle = initial_hex_angle

# ------------------
# Main Loop
# ------------------
running = True
while running:
    dt = clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ------------------
    # Update Ball Physics
    # ------------------
    # Apply gravity
    ball_vel[1] += GRAVITY
    # Apply air friction
    ball_vel[0] *= AIR_FRICTION
    ball_vel[1] *= AIR_FRICTION
    # Update ball position
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # ------------------
    # Update Hexagon Rotation
    # ------------------
    hex_angle += ANGULAR_VELOCITY
    hex_vertices = compute_hexagon_vertices(HEX_CENTER, HEX_RADIUS, hex_angle)

    # ------------------
    # Collision Detection & Response
    # ------------------
    # For each edge of the hexagon, check for collision with the ball.
    for i in range(6):
        a = hex_vertices[i]
        b = hex_vertices[(i + 1) % 6]
        closest = closest_point_on_segment(ball_pos, a, b)
        # Vector from closest point on wall to ball center
        dist_vec = vector_sub(ball_pos, closest)
        dist = vector_length(dist_vec)
        if dist < BALL_RADIUS:
            # Compute collision normal (pointing outward from the wall)
            n = vector_normalize(dist_vec) if dist != 0 else (0, -1)
            # Calculate the velocity of the wall at the collision point.
            contact_vec = vector_sub(closest, HEX_CENTER)
            wall_velocity = vector_mul(perpendicular(contact_vec), ANGULAR_VELOCITY)
            # Relative velocity of the ball with respect to the moving wall.
            v_rel = vector_sub(ball_vel, wall_velocity)
            # Reflect the relative velocity about the normal.
            v_rel_normal = v_rel[0] * n[0] + v_rel[1] * n[1]
            v_rel_reflected = (v_rel[0] - 2 * v_rel_normal * n[0],
                               v_rel[1] - 2 * v_rel_normal * n[1])
            # Apply restitution to simulate energy loss on impact.
            v_rel_reflected = vector_mul(v_rel_reflected, RESTITUTION)
            # Apply wall friction along the tangent direction.
            tangent = perpendicular(n)
            v_rel_tangent = v_rel[0] * tangent[0] + v_rel[1] * tangent[1]
            v_rel_tangent *= WALL_FRICTION
            # Combine the normal and tangent components.
            # First, remove any tangent from the reflected velocity...
            proj = (v_rel_reflected[0] * tangent[0] + v_rel_reflected[1] * tangent[1])
            v_rel_after = (v_rel_reflected[0] + tangent[0] * (v_rel_tangent - proj),
                           v_rel_reflected[1] + tangent[1] * (v_rel_tangent - proj))
            # Update ball velocity: add back the wall velocity.
            ball_vel = list(vector_add(v_rel_after, wall_velocity))
            # Correct the ball's position to prevent sticking (instantaneous penetration correction).
            penetration = BALL_RADIUS - dist
            correction = vector_mul(n, penetration + 0.5)  # small extra push out
            ball_pos = list(vector_add(ball_pos, correction))

    # ------------------
    # Rendering
    # ------------------
    screen.fill((30, 30, 30))
    pygame.draw.polygon(screen, (200, 200, 200), hex_vertices, 3)
    pygame.draw.circle(screen, (220, 50, 50), (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)
    pygame.display.flip()

pygame.quit()
sys.exit()
