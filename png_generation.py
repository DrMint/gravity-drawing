
import png
import math

MULTIPLIER = 1 / 30
WIDTH = int(2160 * MULTIPLIER)
HEIGTH = int(3840 * MULTIPLIER)
ITERATION = 200

ITERATION_DURATION = 20 * MULTIPLIER
DISTANCE_TRESHOLD = 20 * MULTIPLIER


DRAG_COEF = 1


print("MULTIPLIER", MULTIPLIER)
print("WIDTH", WIDTH)
print("HEIGTH", HEIGTH)
print("ITERATION", ITERATION)
print("ITERATION_DURATION", ITERATION_DURATION)
print("DISTANCE_TRESHOLD", DISTANCE_TRESHOLD)
print("DRAG_COEF", DRAG_COEF)



def writePNG(name, data):
    with open(name + ".png", "wb") as f:
        w = png.Writer(width=WIDTH, height=HEIGTH,
                       greyscale=False, compression=9)
        w.write(f, rows)


class Point():
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.color = color
        self.stopped = False

    def tick(self):
        self.x += self.dx
        self.y += self.dy
        self.dx *= DRAG_COEF
        self.dy *= DRAG_COEF


class Attractor(Point):
    def __init__(self, x, y, strength, color):
        super().__init__(x, y, color)
        self.strength = strength

    def attract(self, point):

        xDistance = self.x - point.x
        yDistance = self.y - point.y

        distance = math.sqrt(xDistance ** 2 + yDistance ** 2)

        if (distance < DISTANCE_TRESHOLD):
            point.dx = 0
            point.dy = 0
            point.stopped = True
            point.color = self.color
            return

        attractionStrength = self.strength / distance ** 2

        point.dx += xDistance * attractionStrength * ITERATION_DURATION ** 2
        point.dy += yDistance * attractionStrength * ITERATION_DURATION ** 2


attractors = [Attractor(0.31 * WIDTH, 0.36 * HEIGTH, 1, (255, 0, 0)),
              Attractor(0.81 * WIDTH, 0.45 * HEIGTH, 1, (0, 0, 255)),
              Attractor(0.42 * WIDTH, 0.65 * HEIGTH, 1, (0, 255, 0))]

rows = []
for y in range(HEIGTH):
    row = []
    for x in range(WIDTH):
        point = Point(x, y, (0, 0, 0))
        iteration = 0
        while (not point.stopped and iteration < ITERATION):
            for attractor in attractors:
                attractor.attract(point)
            point.tick()
            iteration += 1
        row += (point.color)
    rows += [row]

writePNG("testing_" + str(int(MULTIPLIER * 100000)), rows)
