import arcade
import math
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
ray_flag = False


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
        # Multiple visible ranges for partially hidden walls
        self.visible_ranges = []  # List of (start, end) tuples
        self.current_hits = []  # Store current ray hits this frame
        self.active_rays = set()  # Track which rays are currently hitting this wall
        self.was_hit = False  # Track if wall was hit in current frame
        self.any_hit = False  # Track if wall was ever hit

        # Wall vector calculations
        self.vector = (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
        self.length = math.sqrt(self.vector[0] ** 2 + self.vector[1] ** 2)
        self.direction = (self.vector[0] / self.length, self.vector[1] / self.length) if self.length > 0 else (0, 0)

        # For tracking extreme points
        self.leftmost_hit = None
        self.rightmost_hit = None

    def get_random_point(self):
        if not self.visible_ranges:
            return None

        segment = self.visible_ranges[np.random.choice(len(self.visible_ranges))]
        start, end = segment

        # Generate random point in this segment
        t = np.random.uniform(0, 1)
        x = start[0] + t * (end[0] - start[0])
        y = start[1] + t * (end[1] - start[1])
        return (x, y)

    def update_visible_ranges(self):
        if not self.was_hit:
            # If wall wasn't hit this frame but was hit before
            if self.any_hit:
                # Check if any rays are still active on this wall
                active_rays_on_wall = [ray for ray in self.active_rays if ray.last_hit_wall == self]
                if not active_rays_on_wall:
                    # No active rays left - reset everything
                    self.visible_ranges = []
                    self.leftmost_hit = None
                    self.rightmost_hit = None
                    self.any_hit = False
            return

        # Mark that wall was hit at least once
        self.any_hit = True

        # Convert hits to parameters along the wall
        hit_params = [self.point_to_parameter(hit) for hit in self.current_hits]
        hit_params.sort()

        # Group consecutive hits into visible ranges
        ranges = []
        if hit_params:
            current_start = hit_params[0]

            for i in range(1, len(hit_params)):
                if hit_params[i] - hit_params[i - 1] > 0.05:  # Threshold for gap detection
                    ranges.append((current_start, hit_params[i - 1]))
                    current_start = hit_params[i]

            ranges.append((current_start, hit_params[-1]))

            # Convert parameters back to points
            self.visible_ranges = [
                (self.parameter_to_point(start), self.parameter_to_point(end))
                for start, end in ranges
            ]

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
        return (x, y)

    def draw(self):
        # Draw main wall
        arcade.draw_line(*self.start_pos, *self.end_pos, arcade.color.WHITE, 3)

        # Draw visible ranges in green
        for start, end in self.visible_ranges:
            arcade.draw_line(*start, *end, arcade.color.GREEN, 2)

        # Draw extreme points
        if self.leftmost_hit:
            arcade.draw_point(*self.leftmost_hit, arcade.color.RED, 10)
        if self.rightmost_hit:
            arcade.draw_point(*self.rightmost_hit, arcade.color.PURPLE, 10)

# Initialize rays
start = 0
end = 90
for i in range(start, end, int(90 / NUM_RAYS)):
    rays.append(Ray(mx, my, math.radians(i)))


def drawRays(rays, walls):
    global lastClosestPoint
    # Sort rays by angle
    sorted_rays = sorted(rays, key=lambda ray: ray.angle)

    # Reset current hits for all walls and mark as not hit this frame
    for wall in walls:
        wall.current_hits = []
        wall.was_hit = False

    # Track extreme rays
    extreme_hits = {'left': None, 'right': None}

    for i, ray in enumerate(sorted_rays):
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
            closest_wall.was_hit = True  # Mark wall as hit this frame

            # Update ray's last hit wall
            if ray.last_hit_wall != closest_wall:
                if ray.last_hit_wall:
                    ray.last_hit_wall.active_rays.discard(ray)
                closest_wall.active_rays.add(ray)
                ray.last_hit_wall = closest_wall

            # Track extreme hits
            if i == 0:  # Leftmost ray
                extreme_hits['left'] = (closest_wall, closest_point)
            elif i == len(sorted_rays) - 1:  # Rightmost ray
                extreme_hits['right'] = (closest_wall, closest_point)

            # Draw the ray
            if not ray_flag:
                if i == 0 or i == len(sorted_rays) - 1:
                    arcade.draw_line(ray.x, ray.y, closest_point[0], closest_point[1],
                                     arcade.color.GREEN)
            else:
                arcade.draw_line(ray.x, ray.y, closest_point[0], closest_point[1],
                                 arcade.color.GREEN if i == 0 or i == len(sorted_rays) - 1
                                 else arcade.color.WHITE)
            if SOLID_RAYS:
                arcade.draw_polygon_filled([(mx, my), closest_point, lastClosestPoint],
                                           arcade.color.WHITE)
                lastClosestPoint = closest_point

    for wall in walls:
        wall.update_visible_ranges()
        if lidar_flag:
            if wall.visible_ranges:
                point = wall.get_random_point()
                if point:
                    dots.append((*point, arcade.color.RED, 4))

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
        start_x = np.random.randint(0, window.width)
        start_y = np.random.randint(0, window.height)
        end_x = np.random.randint(0, window.width)
        end_y = np.random.randint(0, window.height)
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
        self.fps = 0.0

    def on_draw(self):
        self.clear()

        for wall in walls:
            wall.draw()

        drawRays([ray for ray in rays], [wall for wall in walls])
        drawDots()
        arcade.Text(x=5.0, y=self.height - 14, text=f'FPS: {self.fps}').draw()

    def on_update(self, delta_time: float):
        changeRays()
        self.fps = round(1/delta_time, 2)

    def on_key_press(self, key, key_modifiers):
        global left, right, up, down, lidar_flag, ray_flag
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
        if key == arcade.key.K:
            dots.clear()
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
