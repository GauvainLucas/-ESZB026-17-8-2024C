import pygame
import serial
import math

# Initialize constants
SIDE_LENGTH = 1000
ANGLE_BOUNDS = 80
ANGLE_STEP = 2
HISTORY_SIZE = 10
POINTS_HISTORY_SIZE = 500
MAX_DISTANCE = 100

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 1920, 1024
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Radar Simulation")

# Colors
BLACK = (0, 0, 0)
GREEN = (20, 255, 40)
GRAY = (100, 100, 100)

# Radar center
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT
RADIUS = SIDE_LENGTH // 2
LEFT_ANGLE_RAD = math.radians(-ANGLE_BOUNDS) - math.pi / 2
RIGHT_ANGLE_RAD = math.radians(ANGLE_BOUNDS) - math.pi / 2

# Data structures
echoes = [0] * 80
history = []
points = [(0, 0)] * POINTS_HISTORY_SIZE

# Initialize angle
angle = -40

# Serial setup
SERIAL_PORT = "/dev/pts/8"
BAUD_RATE = 115200
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

def draw_radar():
    pygame.draw.circle(screen, GRAY, (CENTER_X, CENTER_Y), RADIUS, 1)
    for i in range(0, SIDE_LENGTH // 100):
        pygame.draw.arc(screen, GRAY, (CENTER_X - 50 * i, CENTER_Y - 50 * i, 100 * i, 100 * i), LEFT_ANGLE_RAD, RIGHT_ANGLE_RAD, 1)

    for i in range(0, ANGLE_BOUNDS * 2 // 20):
        angle = -ANGLE_BOUNDS + i * 20
        rad_angle = math.radians(angle)
        end_x = CENTER_X + RADIUS * math.sin(rad_angle)
        end_y = CENTER_Y - RADIUS * math.cos(rad_angle)
        pygame.draw.line(screen, GRAY, (CENTER_X, CENTER_Y), (end_x, end_y), 1)

def draw_objects():
    for i in range(1, 80):
        distance = i * 12.5
        radian = math.radians(angle)
        x = distance * math.sin(radian)
        y = distance * math.cos(radian)
        px, py = int(CENTER_X + x), int(CENTER_Y - y)
        points[i % POINTS_HISTORY_SIZE] = (px, py)

        for px, py in points:
            if px != 0 and py != 0:
                pygame.draw.ellipse(screen, GREEN, (px - 2, py - 2, 4, 4))

def process_serial():
    global angle
    line = ser.readline().decode('utf-8').strip()
    if line:
        values = line.split(',')
        try:
            angle = int(values[0])
            for i in range(1, 80):
                echoes[i] = int(values[i])
        except ValueError:
            pass

# Main loop
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    process_serial()
    draw_radar()
    draw_objects()

    pygame.display.flip()

pygame.quit()
ser.close()
