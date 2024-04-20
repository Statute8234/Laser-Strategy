import pygame
import random, time
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

WIDTH, HEIGHT = 700, 700
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
# Laser base class
class Laser:
    def __init__(self, x, y, direction, width=20, height=20, active_color=BLACK, inactive_color=RED, light_color=random_color()):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.color = inactive_color
        self.light_color = light_color
        self.direction = direction  # 'up' or 'down'
        self.line_start = 0
        self.line_end = 0
        self.update_line()
        self.dragging = False

    def draw(self, screen):
        pygame.draw.line(screen, self.light_color, self.line_start, self.line_end, 2)
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def update_line(self):
        mid_x = self.x + (self.width / 2)
        if self.direction == 'down':
            self.line_start = (mid_x, HEIGHT)
            self.line_end = (mid_x, self.y)
        else:
            self.line_start = (mid_x, 0)
            self.line_end = (mid_x, self.y)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN and self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
            self.dragging = True
            self.color = self.active_color
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            self.color = self.inactive_color
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.x = max(0, min(mouse_pos[0] - self.width / 2, WIDTH - self.width))
            self.update_line()

# detector 
class Detector:
    def __init__(self, x, y, width, height, screen_width, screen_height, bodyColor):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.detector_x = self.x + 13
        self.detector_y = self.y + 13
        self.detector_width = self.width // 2
        self.detector_height = self.height // 2
        self.active_color = RED
        self.color = bodyColor
        # Make sure screen_width and screen_height are integers
        self.matrixWidth = int(screen_width)
        self.matrixHeight = int(screen_height)
        self.matrix = []
        self.radius = 5
        self.activated = False
        self.activation_time = 0
        self.activation_duration = 1

    def buildMatrix(self):
        self.matrix = [[1] * self.matrixWidth for _ in range(self.matrixHeight)]

    def makePath(self, door):
        self.buildMatrix()
        self.grid = Grid(matrix=self.matrix)
        self.start = self.grid.node(self.x // 50, 0)
        end_y = door.y // 50
        while True:
            end_x = door.x // 50
            if (end_x, end_y) != (self.start.x, self.start.y):
                self.end = self.grid.node(end_x, end_y)
                break

        self.finder = AStarFinder()
        self.path, self.runs = self.finder.find_path(self.start, self.end, self.grid)
        self.path_coordinates = [(node.x, node.y) for node in self.path]

    def get_rect(self):
        return pygame.Rect(self.detector_x, self.detector_y, self.detector_width, self.detector_height)
    
    def toggle_activation(self, activate):
        if activate:
            self.activated = True
            self.activation_time = time.time()  # Record the current time of activation
        else:
            self.activated = False

    def update(self):
        # Automatically deactivate after the duration expires
        if self.activated and (time.time() - self.activation_time) > self.activation_duration:
            self.activated = False

    def draw(self, screen):
        self.update()  # Ensure the activation status is updated before drawing
        self.active_color = RED if self.activated else DARK_GRAY

        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.active_color, (self.detector_x, self.detector_y, self.detector_width, self.detector_height))
        
        for x, y in self.path_coordinates:
            pygame.draw.circle(screen, self.active_color, (x * 50 + self.radius, y * 50 + self.radius), self.radius)
            pygame.draw.circle(screen, BLACK, (x * 50 + self.radius, y * 50 + self.radius), self.radius, 2)
