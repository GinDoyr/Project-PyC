import arcade
import arcade.clock
import math
import numpy as np

# -----Options-----
NUM_RAYS = 90  # Must be between 1 and 90. might change later on
SOLID_RAYS = False  # Can be somewhat glitchy. For best results, set NUM_RAYS to 360 (well...)
NUM_WALLS = 5  # The amount of randomly generated walls
MAX_DOTS = 10000  # heey finally one of my own :D max "lidar" generated dots
MIN_RAY_LEN = 300
DOT_SPEED = 3
# ------------------

window = arcade.Window(1200, 600, 'raytest')
window.center_window()

mx, my = 600, 400
ray_len = MIN_RAY_LEN
lastClosestPoint = (0, 0)
rays = []
walls = []
lidar_walls = []
walldots = []
left = False
right = False
up = False
down = False
up1 = False
down1 = False
lidar_flag = False
ray_flag = False
DEBUG_FLAG = False
draw_wall = True
intersect_count = 0


class Ray:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle  # Store angle for sorting
        self.dir = (math.cos(angle), math.sin(angle))
        self.last_hit_wall = None  # Track last wall this ray hit

    def update(self, mx, my):
        self.x = mx
        self.y = my

    def checkCollision(self, wall):
        x1, y1 = wall.start_pos
        x2, y2 = wall.end_pos
        x3, y3 = self.x, self.y

        denominator = (x1 - x2) * (-self.dir[1]) - (y1 - y2) * (-self.dir[0])
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
        # Multiple visible ranges for partially hidden walls
        self.visible_ranges = []  # List of (start, end) tuples
        self.current_hits = []  # Store current ray hits this frame
        self.active_rays = set()  # Track which rays are currently hitting this wall
        self.was_hit = False  # Track if wall was hit in current frame
        self.hit = False  # Track if wall was ever hit
        self.flag = False  # i truly hope this helps to remove the rays from the walls

        # Wall vector calculations
        self.vector = (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
        self.length = math.sqrt(self.vector[0] ** 2 + self.vector[1] ** 2)
        self.direction = (self.vector[0] / self.length, self.vector[1] / self.length) if self.length > 0 else (0, 0)

        # For tracking extreme points
        self.leftmost_hit = None
        self.rightmost_hit = None

    def get_random_point(self):
        start, end = self.visible_ranges[np.random.choice(len(self.visible_ranges))]
        t = np.random.uniform(0, 1)
        x = start[0] + t * (end[0] - start[0])
        y = start[1] + t * (end[1] - start[1])
        return x, y

    def update_visible_ranges(self):
        if not self.was_hit:
            # If wall wasn't hit this frame but was hit before
            if self.hit:
                # Check if any rays are still active on this wall
                if not [ray for ray in self.active_rays if ray.last_hit_wall == self]:
                    # No active rays left - reset everything
                    self.visible_ranges = []
                    lidar_walls.remove(self)
                    self.leftmost_hit = None
                    self.rightmost_hit = None
                    self.hit = False
            return

        # Mark that wall was hit at least once
        self.hit = True

        # Convert hits to parameters along the wall
        hit_params = [self.point_to_parameter(hit) for hit in self.current_hits]
        hit_params.sort()

        # Group consecutive hits into visible ranges
        if hit_params:
            # Convert parameters back to points
            self.visible_ranges = [
                (self.parameter_to_point(hit_params[0]), self.parameter_to_point(hit_params[-1]))
            ]
            if self not in lidar_walls:
                lidar_walls.append(self)

            # Update extreme hits
            self.leftmost_hit = self.parameter_to_point(hit_params[0])
            self.rightmost_hit = self.parameter_to_point(hit_params[-1])

        # Reset for next frame
        self.current_hits = []
        self.was_hit = False

    def point_to_parameter(self, point):
        """Convert point to parameter t (0-1) along wall"""
        if self.length == 0:
            return 0
        dx = point[0] - self.start_pos[0]
        dy = point[1] - self.start_pos[1]
        return (dx * self.direction[0] + dy * self.direction[1]) / self.length

    def parameter_to_point(self, t):
        """Convert parameter t to point on wall"""
        x = self.start_pos[0] + t * self.vector[0]
        y = self.start_pos[1] + t * self.vector[1]
        return x, y

    def draw(self):
        if draw_wall:
            arcade.draw_line(*self.start_pos, *self.end_pos, arcade.color.WHITE, 3)

        # DEBUGGING YEEEAH
        if DEBUG_FLAG:
            if self.visible_ranges:
                arcade.draw_line(*self.visible_ranges[0][0], *self.visible_ranges[0][1], arcade.color.MAGENTA, 2)
            if self.leftmost_hit:
                arcade.draw_point(*self.leftmost_hit, arcade.color.BLUE, 10)
            if self.rightmost_hit:
                arcade.draw_point(*self.rightmost_hit, arcade.color.PURPLE, 10)


# rays init
start = 0
end = 90
for i in range(start, end, int(90 / NUM_RAYS)):
    rays.append(Ray(mx, my, math.radians(i)))

middle = (end//4, end//2+end//4)


def drawRays(rays, walls):
    global lastClosestPoint, intersect_count
    for i, ray in enumerate(rays):
        closest = ray_len
        closest_point = None
        closest_wall = None
        intersect_count += 1
        for wall in walls:
            intersect = ray.checkCollision(wall)
            intersect_count += 1
            if intersect:
                wall.flag = True
                distance = math.sqrt((ray.x - intersect[0]) ** 2 + (ray.y - intersect[1]) ** 2)
                if distance < closest:
                    closest = distance
                    closest_point = intersect
                    closest_wall = wall

        if closest_point is None:
            closest_point = [ray.x + closest * math.cos(ray.angle), ray.y + closest * math.sin(ray.angle)]
            ray.last_hit_wall = None
        if closest_wall:
            closest_wall.current_hits.append(closest_point)
            closest_wall.was_hit = True

            if ray.last_hit_wall != closest_wall:
                if ray.last_hit_wall:
                    ray.last_hit_wall.active_rays.discard(ray)
                closest_wall.active_rays.add(ray)
                ray.last_hit_wall = closest_wall
            if i == 0:
                rays[0] = (closest_wall, closest_point)
            elif i == len(rays) - 1:
                rays[-1] = (closest_wall, closest_point)

        if not ray_flag:
            if i == 0 or i == len(rays) - 1:
                arcade.draw_line(ray.x, ray.y, closest_point[0], closest_point[1],
                                 arcade.color.GREEN)
        else:
            if SOLID_RAYS:
                arcade.draw_polygon_filled([(mx, my), closest_point, lastClosestPoint],
                                           arcade.color.WHITE)
                lastClosestPoint = closest_point
            else:
                arcade.draw_line(ray.x, ray.y, closest_point[0], closest_point[1],
                                 arcade.color.GREEN if i == 0 or i == len(rays) - 1
                                 else arcade.color.WHITE)
        arcade.draw_point(closest_point[0], closest_point[1], arcade.color.GREEN, size=3)

    for wall in walls:
        wall.update_visible_ranges()
        if wall.flag:
            wall.was_hit = False
            wall.active_rays.clear()


def getDot():
    wall = lidar_walls[np.random.choice(len(lidar_walls))]
    point = wall.get_random_point()
    walldots.append(point)


def drawDots():
    arcade.draw_points(walldots, arcade.color.TEAL, 4)
    if len(walldots) > MAX_DOTS:
        walldots.remove(walldots[0])


def generateWalls(flag=True):
    walls.clear()
    if flag:
        walls.append(Wall((0, 0), (window.width, 0)))
        walls.append(Wall((0, 0), (0, window.height)))
        walls.append(Wall((window.width, 0), (window.width, window.height)))
        walls.append(Wall((0, window.height), (window.width, window.height)))

    for i in range(NUM_WALLS):
        start_x = np.random.randint(0, window.width)
        start_y = np.random.randint(0, window.height)
        end_x = np.random.randint(0, window.width)
        end_y = np.random.randint(0, window.height)
        walls.append(Wall((start_x, start_y), (end_x, end_y)))


def changeRays():
    global start, end, up1, down1, DEBUG_FLAG, ray_len
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
        if down and (end - start != 0):
            start += 1
            end -= 1
        if up1 and (end - start != 360):
            start -= 1
            end += 1
            up1 = False
        if down1 and (end - start != 0):
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
        self.fps = 0.0
        self.fpstext = arcade.Text(x=5.0, y=self.height - 14, text=f'FPS: {self.fps}')
        self.inttext = arcade.Text(x=5.0, y=14.0, text=f'Intersection: {intersect_count}')
        self.clocker = arcade.clock.Clock()
        self.recharge_flag = True

    def on_draw(self):
        global intersect_count
        self.clear()
        intersect_count = 0

        for wall in walls:
            wall.draw()
        drawRays([ray for ray in rays], [wall for wall in walls])
        drawDots()

        self.fpstext.draw()
        self.inttext.draw()

    def on_update(self, delta_time: float):
        changeRays()
        if not self.recharge_flag:
            self.clocker.tick(delta_time)
            if self.clocker.ticks % DOT_SPEED == 0:
                self.recharge_flag = True
        if lidar_flag and lidar_walls and self.recharge_flag:
            getDot()
            self.recharge_flag = False
        self.fps = round(1 / delta_time, 2)
        self.fpstext.text = f'FPS: {self.fps}'
        self.inttext.text = f'Intersection: {intersect_count}'

    def on_key_press(self, key, key_modifiers):
        global left, right, up, down, lidar_flag, ray_flag, DEBUG_FLAG, draw_wall
        if key == arcade.key.SPACE:
            lidar_walls.clear()
            generateWalls(self.flag)
        if key == arcade.key.J:
            self.flag = not self.flag
            lidar_walls.clear()
            generateWalls(self.flag)
        if key == arcade.key.H:
            DEBUG_FLAG = not DEBUG_FLAG
        if key == arcade.key.B:
            draw_wall = not draw_wall
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
        if key == arcade.key.K:
            walldots.clear()
        if key == arcade.key.R:
            ray_flag = not ray_flag

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
