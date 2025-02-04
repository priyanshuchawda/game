import pygame
import math
import sys

# ----- Configuration Constants -----
WIDTH, HEIGHT = 800, 600
FPS = 60

# Ball physics
BALL_RADIUS = 15
GRAVITY = 0.5            # acceleration due to gravity
AIR_FRICTION = 0.995     # velocity damping per frame (simulate air resistance)
RESTITUTION = 0.8        # bounciness on collision

# Hexagon parameters
HEX_RADIUS = 250         # distance from center to vertex
HEX_CENTER = (WIDTH // 2, HEIGHT // 2)
ANGULAR_VELOCITY = 0.02  # radians per frame
initial_hex_angle = 0.0

# Collision friction (affecting tangential component on impact)
WALL_FRICTION = 0.9

# ----- Helper Functions -----
def rotate_point(point, angle, center):
    """Rotate a point around a center by a given angle (radians)."""
    cx, cy = center
    x, y = point
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    x_new = cx + cos_a * (x - cx) - sin_a * (y - cy)
    y_new = cy + sin_a * (x - cx) + cos_a * (y - cy)
    return (x_new, y_new)

def compute_hexagon_vertices(center, radius, angle_offset):
    """Return the vertices of a hexagon rotated by angle_offset."""
    cx, cy = center
    vertices = []
    for i in range(6):
        angle = angle_offset + i * (2 * math.pi / 6)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        vertices.append((x, y))
    return vertices

def closest_point_on_segment(p, a, b):
    """Return the closest point from p to line segment ab."""
    ax, ay = a
    bx, by = b
    px, py = p
    abx = bx - ax
    aby = by - ay
    ab_len_sq = abx * abx + aby * aby
    if ab_len_sq == 0:
        return a
    t = ((px - ax) * abx + (py - ay) * aby) / ab_len_sq
    t = max(0, min(1, t))
    return (ax + t * abx, ay + t * aby)

def reflect_velocity(v, n):
    """Reflect velocity vector v about normal n."""
    dot = v[0] * n[0] + v[1] * n[1]
    return (v[0] - 2 * dot * n[0], v[1] - 2 * dot * n[1])

def vector_sub(a, b):
    return (a[0] - b[0], a[1] - b[1])

def vector_add(a, b):
    return (a[0] + b[0], a[1] + b[1])

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

# ----- Pygame Setup -----
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in a Spinning Hexagon")
clock = pygame.time.Clock()

# ----- Initial Conditions -----
ball_pos = [WIDTH // 2, HEIGHT // 2 - 100]
ball_vel = [5, 0]

hex_angle = initial_hex_angle

# ----- Main Loop -----
running = True
while running:
    dt = clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Update Physics ---
    # Apply gravity
    ball_vel[1] += GRAVITY

    # Apply air friction
    ball_vel[0] *= AIR_FRICTION
    ball_vel[1] *= AIR_FRICTION

    # Update ball position
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Update hexagon rotation
    hex_angle += ANGULAR_VELOCITY

    # Get current hexagon vertices (rotated)
    hex_vertices = compute_hexagon_vertices(HEX_CENTER, HEX_RADIUS, hex_angle)

    # --- Collision Detection and Response ---
    # Check collision against each hexagon edge
    for i in range(6):
        a = hex_vertices[i]
        b = hex_vertices[(i + 1) % 6]
        # Find closest point on edge to ball center
        closest = closest_point_on_segment(ball_pos, a, b)
        dist_vec = vector_sub(ball_pos, closest)
        dist = vector_length(dist_vec)
        if dist < BALL_RADIUS:
            # Compute collision normal (from edge toward ball)
            if dist == 0:
                # Avoid division by zero
                n = (0, -1)
            else:
                n = vector_normalize(dist_vec)
            
            # Compute wall velocity at contact point due to hexagon rotation
            # The wall rotates about HEX_CENTER
            contact_vec = vector_sub(closest, HEX_CENTER)
            wall_vel = vector_mul(perpendicular(contact_vec), ANGULAR_VELOCITY)
            
            # Relative velocity
            v_rel = vector_sub(ball_vel, wall_vel)
            
            # Reflect relative velocity
            v_rel_normal = v_rel[0] * n[0] + v_rel[1] * n[1]
            v_rel_reflected = (v_rel[0] - 2 * v_rel_normal * n[0],
                               v_rel[1] - 2 * v_rel_normal * n[1])
            
            # Apply friction to tangential component
            tangent = perpendicular(n)
            v_rel_tangent = v_rel[0] * tangent[0] + v_rel[1] * tangent[1]
            v_rel_tangent *= WALL_FRICTION
            v_rel_after = (
                v_rel_reflected[0] + tangent[0] * (v_rel_tangent - (v_rel_reflected[0] * tangent[0] + v_rel_reflected[1] * tangent[1])),
                v_rel_reflected[1] + tangent[1] * (v_rel_tangent - (v_rel_reflected[0] * tangent[0] + v_rel_reflected[1] * tangent[1]))
            )
            
            # Set new ball velocity (add back the wall velocity) and ensure it remains a list
            ball_vel = list(vector_add(v_rel_after, wall_vel))
            
            # Correct penetration: push the ball out of the wall along n and ensure ball_pos remains a list
            penetration = BALL_RADIUS - dist
            ball_pos = list(vector_add(ball_pos, vector_mul(n, penetration + 0.5)))

    # --- Drawing ---
    screen.fill((30, 30, 30))  # dark background

    # Draw hexagon (as a white polygon)
    pygame.draw.polygon(screen, (200, 200, 200), hex_vertices, 3)

    # Draw ball (as a red circle)
    pygame.draw.circle(screen, (220, 50, 50), (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)

    pygame.display.flip()

pygame.quit()
sys.exit()
