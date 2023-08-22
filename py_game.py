from PIL import Image
import pygame
import math

CANVAS_X_MIN = -10
CANVAS_X_MAX = 10
CANVAS_Y_MIN = -10
CANVAS_Y_MAX = 10

DEFAULT_COLOR = (10, 10, 10)
WIDTH = 1000
HEIGHT = 1000

TICK_DURATION = 1/500
GRAVITY = 9.8
DRAG_COEF = 1 - 1/2000


class Point():
    def __init__(self, x, y, color):
        self.initialX = x
        self.initialY = y
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.color = color
        self.stopped = False

    def toPixel(self):
        pixelX = (self.x - CANVAS_X_MIN) / \
            (CANVAS_X_MAX - CANVAS_X_MIN) * WIDTH
        pixelY = (self.y - CANVAS_Y_MIN) / \
            (CANVAS_Y_MAX - CANVAS_Y_MIN) * HEIGHT
        return (int(pixelX), int(pixelY))

    def initialToPixel(self):
        pixelX = (self.initialX - CANVAS_X_MIN) / \
            (CANVAS_X_MAX - CANVAS_X_MIN) * WIDTH
        pixelY = (self.initialY - CANVAS_Y_MIN) / \
            (CANVAS_Y_MAX - CANVAS_Y_MIN) * HEIGHT
        return (int(pixelX), int(pixelY))

    def tick(self):
        self.x += self.dx
        self.y += self.dy
        self.dx *= DRAG_COEF
        self.dy *= DRAG_COEF

    def dist(self, point):
        return math.sqrt((self.x - point.x)**2 + (self.y - point.y)**2)

    def attrack(self, point):
        distance = self.dist(point)

        if (distance < 0.3):
            point.dx = 0
            point.dy = 0
            point.stopped = True
            point.color = self.color
            return

        attractionStrength = 1 / distance ** 3

        point.dx += (self.x - point.x) * attractionStrength * TICK_DURATION
        point.dy += (self.y - point.y) * attractionStrength * TICK_DURATION


def putPixel(img, pixel, color):
    x = pixel[0]
    y = pixel[1]
    if (0 <= x < WIDTH and 0 <= y < HEIGHT):
        img.putpixel(pixel, color)


def pillowImageToPyGame(pilImage):
    return pygame.image.fromstring(pilImage.tobytes(), pilImage.size, pilImage.mode)


img = Image.new("RGB", (WIDTH, HEIGHT), color=DEFAULT_COLOR)

points = []
for x in range(-100, 100):
    for y in range(-100, 100):
        points += [Point(x / 10, y / 10, "white")]

attractors = [Point(-2, 3, "red"), Point(2, -5, "blue"), Point(4, 6, "green")]


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # RENDER YOUR GAME HERE

    for attractor in attractors:
        pygame.draw.circle(screen, attractor.color, attractor.toPixel(), 10)

    for point in points:
        if point.stopped:
            pygame.draw.circle(screen, point.color, point.initialToPixel(), 4)
        else:
            pygame.draw.circle(screen, point.color, point.toPixel(), 1)
            for attractor in attractors:
                attractor.attrack(point)
            point.tick()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
