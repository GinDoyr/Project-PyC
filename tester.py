import arcade
import math
import random

# -----Options-----
WINDOW_SIZE = (1200, 800)  # Width x Height in pixels
NUM_RAYS = 90  # Must be between 1 and 360 (90 testing)
SOLID_RAYS = False  # Can be somewhat glitchy. For best results, set NUM_RAYS to 360
NUM_WALLS = 5  # The amount of randomly generated walls
# ------------------

window = arcade.Window(1200, 800, 'raytest')
window.center_window()

mx, my = 600, 400
lastClosestPoint = (0, 0)
running = True
rays = []
walls = []
particles = []


class Ray:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.dir = (math.cos(angle), math.sin(angle))

    def update(self, mx, my):
        self.x = mx
        self.y = my
    
    def checkCollision(self, wall):
        x1 = wall.start_pos[0]
        y1 = wall.start_pos[1]
        x2 = wall.end_pos[0]
        y2 = wall.end_pos[1]

        x3 = self.x
        y3 = self.y
        x4 = self.x + self.dir[0]
        y4 = self.y + self.dir[1]

        # Using line-line intersection formula to get intersection point of ray and wall
        # Where (x1, y1), (x2, y2) are the ray pos and (x3, y3), (x4, y4) are the wall pos
        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        numerator = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
        if denominator == 0:
            return None

        t = numerator / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

        if 1 > t > 0 and u > 0:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            collidePos = [x, y]
            return collidePos


class Wall:
    def __init__(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.slope_x = end_pos[0] - start_pos[0]
        self.slope_y = end_pos[1] - start_pos[1]
        if self.slope_x == 0:
            self.slope = 0
        else:
            self.slope = self.slope_y / self.slope_x
        self.length = math.sqrt(self.slope_x ** 2 + self.slope_y ** 2)

    def draw(self):
        arcade.draw_line(self.start_pos[0], self.start_pos[1], self.end_pos[0], self.end_pos[1], arcade.color.WHITE, 3)


start = 0
end = 90
for i in range(start, end, int(90 / NUM_RAYS)):
    rays.append(Ray(mx, my, math.radians(i)))


def drawRays(rays, walls):
    global lastClosestPoint
    for ray in rays:
        closest = 100000
        closestPoint = None
        for wall in walls:
            intersectPoint = ray.checkCollision(wall)
            if intersectPoint is not None:
                # Get distance between ray source and intersect point
                ray_dx = ray.x - intersectPoint[0]
                ray_dy = ray.y - intersectPoint[1]
                # If the intersect point is closer than the previous closest intersect point, it becomes the closest intersect point
                distance = math.sqrt(ray_dx ** 2 + ray_dy ** 2)
                if (distance < closest):
                    closest = distance
                    closestPoint = intersectPoint

        if closestPoint is not None:
            arcade.draw_line(ray.x, ray.y, closestPoint[0], closestPoint[1], arcade.color.WHITE)
            if SOLID_RAYS:
                arcade.draw_polygon_filled([(mx, my), closestPoint, lastClosestPoint], arcade.color.WHITE)
                lastClosestPoint = closestPoint


def generateWalls(flag=True):
    walls.clear()
    if flag:
        walls.append(Wall((0, 0), (window.width, 0)))
        walls.append(Wall((0, 0), (0, window.height)))
        walls.append(Wall((window.width, 0), (window.width, window.height)))
        walls.append(Wall((0, window.height), (window.width, window.height)))

    for i in range(NUM_WALLS):
        start_x = random.randint(0, window.width)
        start_y = random.randint(0, window.height)
        end_x = random.randint(0, window.width)
        end_y = random.randint(0, window.height)
        walls.append(Wall((start_x, start_y), (end_x, end_y)))


def changeRays(st, ed):
    global start,end
    start += st
    end += ed
    rays.clear()
    for i in range(start, end, int(90 / NUM_RAYS)):
        rays.append(Ray(mx, my, math.radians(i)))


class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK
        generateWalls()
        self.flag = True

    def on_draw(self):
        self.clear()

        for wall in walls:
            wall.draw()

        for particle in particles:
            particle.draw()

        drawRays([ray for ray in rays], [wall for wall in walls])

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.SPACE:
            generateWalls(self.flag)
        if key == arcade.key.H:
            self.flag = not self.flag
            generateWalls(self.flag)
        if key == arcade.key.G:
            global SOLID_RAYS
            SOLID_RAYS = not SOLID_RAYS
        if key == arcade.key.LEFT:
            changeRays(1, 1)
        if key == arcade.key.RIGHT:
            changeRays(-1, -1)
        if key == arcade.key.UP:
            changeRays(-1, 1)
        if key == arcade.key.DOWN:
            changeRays(1, -1)

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        global mx, my
        mx, my = x, y
        for ray in rays:
            ray.update(mx, my)


def main():
    game = GameView()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
