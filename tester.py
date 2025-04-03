import arcade
import math
import random
import numpy as np

# -----Options-----
NUM_RAYS = 90  # Must be between 1 and 360 (90 testing)
SOLID_RAYS = False  # Can be somewhat glitchy. For best results, set NUM_RAYS to 360
NUM_WALLS = 5  # The amount of randomly generated walls
# ------------------

window = arcade.Window(1200, 600, 'raytest')
window.center_window()

mx, my = 600, 400
lastClosestPoint = (0, 0)
running = True
rays = []
walls = []
dots = []
left = False
right = False
up = False
down = False
up1 = False
down1 = False
lidar_flag = False


class Ray:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.dir = (math.cos(angle), math.sin(angle))

    def update(self, mx, my):
        self.x = mx
        self.y = my

    def checkCollision(self, wall):
        x1, y1 = wall.start_pos
        x2, y2 = wall.end_pos
        x3, y3 = self.x, self.y

        # Using line-line intersection formula to get intersection point of ray and wall
        # Where (x1, y1), (x2, y2) are the ray pos and (x3, y3), (x4, y4) are the wall pos  (ed.: other way, no?)
        denominator = (x1 - x2) * (-self.dir[1]) - (y1 - y2) * (-self.dir[0])  #-self.dir[n] bcs x3 - x4 = self.x - (self.x + self.dir[n])
        numerator = (x1 - x3) * (-self.dir[1]) - (y1 - y3) * (-self.dir[0])
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
    if lidar_flag:
        chosen = np.random.randint(0, len(rays)+1, size=10)
        ind = 0
    lastClosestPoint = (0, 0)
    for ray in rays:
        closest = 10000
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
            if lidar_flag:
                if ind in chosen and lastClosestPoint != (0, 0):
                    try:
                        if closestPoint[0] == lastClosestPoint[0] == window.width:
                            x = window.width - 1
                        else:
                            x = np.random.uniform(min(closestPoint[0], lastClosestPoint[0]),
                                                  max(closestPoint[0], lastClosestPoint[0]))
                        if closestPoint[1] == lastClosestPoint[1] == window.height:
                            y = window.height - 1
                        else:
                            y = np.random.uniform(min(closestPoint[1], lastClosestPoint[1]),
                                                  max(closestPoint[1], lastClosestPoint[1]))
                        dots.append((x, y, arcade.color.RED, 3.0))
                    except Exception as e:
                        print(f'failed to create! {closestPoint}, {lastClosestPoint}\n{e}')
                ind += 1
                lastClosestPoint = closestPoint
            if SOLID_RAYS:
                arcade.draw_polygon_filled([(mx, my), closestPoint, lastClosestPoint], arcade.color.WHITE)
                lastClosestPoint = closestPoint


def drawDots():
    for dot in dots:
        arcade.draw_point(*dot)
        if len(dots) > 300:
            dots.remove(dots[0])


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


def changeRays():
    global start, end, up1, down1
    if left or right or up or down or up1 or down1:
        if left:
            start += 1
            end += 1
        if right:
            start -= 1
            end -= 1
        if up and (end - start != 360):
            start -= 1
            end += 1
        if down:
            start += 1
            end -= 1
        if up1 and (end - start != 360):
            start -= 1
            end += 1
            up1 = False
        if down1:
            start += 1
            end -= 1
            down1 = False
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

        drawRays([ray for ray in rays], [wall for wall in walls])
        drawDots()

    def on_update(self, delta_time: float):
        changeRays()

    def on_key_press(self, key, key_modifiers):
        global left, right, up, down, lidar_flag
        if key == arcade.key.SPACE:
            generateWalls(self.flag)
        if key == arcade.key.H:
            self.flag = not self.flag
            generateWalls(self.flag)
        if key == arcade.key.G:
            global SOLID_RAYS
            SOLID_RAYS = not SOLID_RAYS
        if key == arcade.key.LEFT:
            left = True
        if key == arcade.key.RIGHT:
            right = True
        if key == arcade.key.UP:
            up = True
        if key == arcade.key.DOWN:
            down = True
        if key == arcade.key.F:
            lidar_flag = True

    def on_key_release(self, key: int, _modifiers: int) -> bool | None:
        global left, right, up, down, lidar_flag
        if key == arcade.key.LEFT:
            left = False
        if key == arcade.key.RIGHT:
            right = False
        if key == arcade.key.UP:
            up = False
        if key == arcade.key.DOWN:
            down = False
        if key == arcade.key.F:
            lidar_flag = False

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        global mx, my
        mx, my = x, y
        for ray in rays:
            ray.update(mx, my)

    def on_mouse_press(self, x, y, button, modifiers):
        global left, right, up, down
        if button == arcade.MOUSE_BUTTON_LEFT:
            left = True
        if button == arcade.MOUSE_BUTTON_RIGHT:
            right = True
        if button == arcade.MOUSE_BUTTON_MIDDLE:
            up = False
            down = False

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        global up1, down1
        if scroll_y > 0:
            up1 = True
        else:
            down1 = True

    def on_mouse_release(self, x, y, button, modifiers):
        global left, right
        if button == arcade.MOUSE_BUTTON_LEFT:
            left = False
        if button == arcade.MOUSE_BUTTON_RIGHT:
            right = False


def main():
    game = GameView()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
