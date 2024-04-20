import pygame
import numpy as np
import random, sys, math, time
import Electonic

pygame.init()
current_time = time.time()
random.seed(current_time)
# Seting up the display
WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
# color
def random_color():
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255))
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0,0,0)
GRAY = (128,128,128)
DARK_GRAY = (169,169,169)
Cyan = (0,255,255)
DIM_GRAY = (105,105,105)

# Initialize lasers
lasers = []
for i in range(5):
    ty = random.choice(["down","up"])
    laser_X = HEIGHT - 20
    if ty != "down":
        laser_X = 0
    laser = Electonic.Laser(200 + i * 50, laser_X, ty, light_color=RED)
    lasers.append(laser)

# box
class Box:
    def __init__(self, x, y, width, height, active_color, inactive_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.color = self.inactive_color
        self.dragging = False
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
                self.dragging = True
                self.color = self.active_color
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            self.color = self.inactive_color
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_pos = pygame.mouse.get_pos()
                self.x = max(0, min(mouse_pos[0] - self.width / 2, WIDTH - self.width))
                self.y = max(0, min(mouse_pos[1] - self.height / 2, HEIGHT - self.height))
box = Box(WIDTH / 2, HEIGHT / 2, 50, 50, BLACK, BLUE)

# ground
class Ground:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = DIM_GRAY
        self.outlineColor = DARK_GRAY
        self.splits_width = self.width // 50
        self.splits_height = self.height // 50
    
    def draw(self, screen):
        for y in range(self.splits_height):
            for x in range(self.splits_width):
                pygame.draw.rect(screen, self.color, (x * 50, y * 50, 50, 50))
                pygame.draw.rect(screen, self.outlineColor, (x * 50, y * 50, 50, 50),2)
ground = Ground(0,0, WIDTH, HEIGHT)

# door
class Door:
    def __init__(self, x, y, grid_size=50):
        self.x = x
        self.y = y
        self.width = grid_size
        self.height = grid_size * 2
        self.text = "Door"
        self.textColor = BLACK
        self.font_size = min(self.width // len(self.text) + 10, self.height)
        self.font = pygame.font.Font(None, self.font_size)
    
    def draw(self, screen):
        pygame.draw.rect(screen, Cyan, (self.x, self.y, self.width, self.height))
        text_surface = self.font.render(self.text, True, self.textColor)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def random_edge_position(self, window_height):
        x = 0
        grid_row = random.randint(1, ground.splits_height - 2)
        y = grid_row * 50
        self.x, self.y = x, y
        return self.x, self.y
door = Door(10,10)
door.x, door.y = door.random_edge_position(HEIGHT)

detector = Electonic.Detector(100,0,50,25, WIDTH // 50, HEIGHT // 50, WHITE)
detector.makePath(door)
# This is running the game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        # Handle events for all lasers
        for laser in lasers:
            laser.handle_event(event)
        box.handle_event(event)
    screen.fill(WHITE)
    ground.draw(screen)

    # I don't know why this works, but it works
    # Update and draw all lasers
    for laser in lasers:
        laser_end_y = 0 if laser.direction == "down" else HEIGHT
        collision_with_door = door.get_rect().clipline(laser.line_start, (laser.line_start[0], laser_end_y))
        collision_with_box = box.get_rect().clipline(laser.line_start, laser.line_end)
        collision_with_detector = detector.get_rect().clipline(laser.line_start, laser.line_end)
        # collision with the box, possibly shortening the laser further
        if collision_with_box:
            laser.line_end = collision_with_box[1]
        # check detector
        elif collision_with_detector:
            detector.toggle_activation(collision_with_detector)
            laser.line_end = collision_with_detector[1]
        # collision with the door
        elif collision_with_door:
            laser.line_end = collision_with_door[1]
        else:
            laser.line_end = (laser.line_start[0], laser_end_y)                                                                              
        laser.draw(screen)

    box.draw(screen)
    detector.draw(screen)
    door.draw(screen)
    # This is to update the scene
    clock.tick(64)
    pygame.display.flip()
    pygame.display.update()