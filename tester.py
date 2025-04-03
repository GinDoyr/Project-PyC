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
        self.angle = angle  # Store angle for sorting
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
        # Initialize range markers
        self.range_start = None
        self.range_end = None
        self.current_hits = []  # Store current ray hits this frame
        self.active_rays = set()  # Track which rays are currently hitting this wall

        # Calculate wall vector
        self.vector = (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
        self.length = math.sqrt(self.vector[0] ** 2 + self.vector[1] ** 2)

        # Normalized direction vector
        if self.length > 0:
            self.direction = (self.vector[0] / self.length, self.vector[1] / self.length)
        else:
            self.direction = (0, 0)

    def get_random_point(self):
        if self.range_start is None or self.range_end is None:
            return None

        # Convert range points to parameters along the wall
        start_param = self.point_to_parameter(self.range_start)
        end_param = self.point_to_parameter(self.range_end)

        # Ensure start_param is less than end_param
        if start_param > end_param:
            start_param, end_param = end_param, start_param

        # Generate random point within the range
        t = random.uniform(start_param, end_param)
        x = self.start_pos[0] + t * self.vector[0]
        y = self.start_pos[1] + t * self.vector[1]
        return (x, y)

    def point_to_parameter(self, point):
        """Convert a point on the wall to a parameter t (0-1) along the wall"""
        if self.length == 0:
            return 0
        dx = point[0] - self.start_pos[0]
        dy = point[1] - self.start_pos[1]
        return (dx * self.direction[0] + dy * self.direction[1]) / self.length

    def update_range(self):
        if not self.current_hits:
            # No rays hitting this wall - reset range and active rays
            self.range_start = None
            self.range_end = None
            self.active_rays.clear()
            return

        # Convert all hit points to parameters
        params = [self.point_to_parameter(hit) for hit in self.current_hits]
        min_param = min(params)
        max_param = max(params)

        # Get corresponding points
        min_point = self.parameter_to_point(min_param)
        max_point = self.parameter_to_point(max_param)

        # Always update range based on current hits
        self.range_start = min_point
        self.range_end = max_point

        # Reset current hits for next frame
        self.current_hits = []

    def parameter_to_point(self, t):
        """Convert parameter t (0-1) to a point on the wall"""
        x = self.start_pos[0] + t * self.vector[0]
        y = self.start_pos[1] + t * self.vector[1]
        return (x, y)

    def draw(self):
        arcade.draw_line(self.start_pos[0], self.start_pos[1],
                         self.end_pos[0], self.end_pos[1], arcade.color.WHITE, 3)
        # Draw range markers if they exist
        if self.range_start is not None:
            arcade.draw_point(self.range_start[0], self.range_start[1],
                              arcade.color.RED, 10)
        if self.range_end is not None:
            arcade.draw_point(self.range_end[0], self.range_end[1],
                              arcade.color.PURPLE, 10)


# Initialize rays
start = 0
end = 90
for i in range(start, end, int(90 / NUM_RAYS)):
    rays.append(Ray(mx, my, math.radians(i)))


def drawRays(rays, walls):
    global lastClosestPoint
    if lidar_flag:
        chosen = np.random.randint(0, len(rays) + 1, size=10)
        ind = 0

    # Sort rays by angle for proper left/right determination
    sorted_rays = sorted(rays, key=lambda ray: ray.angle)

    # Reset current hits for all walls
    for wall in walls:
        wall.current_hits = []

    # Track which walls are hit this frame
    hit_walls = set()

    # First pass: collect all hits
    for ray in sorted_rays:
        closest = float('inf')
        closest_point = None
        closest_wall = None

        for wall in walls:
            intersect = ray.checkCollision(wall)
            if intersect:
                distance = math.sqrt((ray.x - intersect[0]) ** 2 + (ray.y - intersect[1]) ** 2)
                if distance < closest:
                    closest = distance
                    closest_point = intersect
                    closest_wall = wall

        if closest_wall and closest_point:
            closest_wall.current_hits.append(closest_point)
            hit_walls.add(closest_wall)

            # Track ray's current wall
            if ray.last_hit_wall != closest_wall:
                if ray.last_hit_wall:
                    ray.last_hit_wall.active_rays.discard(ray)
                closest_wall.active_rays.add(ray)
                ray.last_hit_wall = closest_wall

            # Draw the ray if it's first or last
            if ray == sorted_rays[0] or ray == sorted_rays[-1]:
                arcade.draw_line(ray.x, ray.y, closest_point[0], closest_point[1],
                                 arcade.color.GREEN)

            if lidar_flag:
                if ind in chosen and lastClosestPoint != (0, 0):
                    try:
                        x = 0
                        y = 0
                        dots.append((x, y, arcade.color.RED, 3.0))
                    except Exception as e:
                        print(f'failed to create! {closest_point}, {lastClosestPoint}\n{e}')
                ind += 1
                lastClosestPoint = closest_point

            if SOLID_RAYS:
                arcade.draw_polygon_filled([(mx, my), closest_point, lastClosestPoint],
                                           arcade.color.WHITE)
                lastClosestPoint = closest_point

    # Second pass: update ranges for all walls
    for wall in walls:
        wall.update_range()


# [Rest of the code remains the same...]

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
