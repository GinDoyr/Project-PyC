import arcade
import math
import numpy as np

# -----Options-----
NUM_RAYS = 90  # Must be between 1 and 360 (90 testing)
SOLID_RAYS = False  # Can be somewhat glitchy. For best results, set NUM_RAYS to 360
NUM_WALLS = 5  # The amount of randomly generated walls
MAX_DOTS = 1000  # heey finally one of my own :D max "lidar" generated dots
MAX_RAY_LEN = 400
# ------------------

window = arcade.Window(1200, 600, 'raytest')
window.center_window()

mx, my = 600, 400
lastClosestPoint = (0, 0)
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
bvh_root = None


class Ray:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle  # Store angle for sorting
        self.end_x = self.x + MAX_RAY_LEN*math.cos(self.angle)
        self.end_y = self.y + MAX_RAY_LEN*math.sin(self.angle)
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
            arcade.draw_point(*self.leftmost_hit, arcade.color.BLUE, 10)
        if self.rightmost_hit:
            arcade.draw_point(*self.rightmost_hit, arcade.color.PURPLE, 10)

class BVHNode:  # я чутка позаимствовал, извините Е.Д. :)
    def __init__(self, walls):
        self.aabb = self._compute_node_aabb(walls)
        self.walls = walls
        self.left = None
        self.right = None
        self.wall_normals = [self._compute_wall_normal(wall) for wall in walls]
        # Добавляем случайный цвет для визуализации
        self.color = (
            np.random.randint(50, 200),
            np.random.randint(50, 200),
            np.random.randint(50, 200),
            80  # Полупрозрачный
        )

    def _compute_node_aabb(self, walls):
        """Приватный метод: вычисляет AABB только для этого узла"""
        min_x = min(min(wall.start_pos[0], wall.end_pos[0]) for wall in walls)
        max_x = max(max(wall.start_pos[0], wall.end_pos[0]) for wall in walls)
        min_y = min(min(wall.start_pos[1], wall.end_pos[1]) for wall in walls)
        max_y = max(max(wall.start_pos[1], wall.end_pos[1]) for wall in walls)
        return (min_x, min_y, max_x, max_y)

    def _compute_wall_normal(self, wall):
        """Приватный метод: вычисляет нормаль конкретной стены"""
        (x1, y1), (x2, y2) = wall.start_pos, wall.end_pos
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        normal = (-dy/length, dx/length)
        # Корректировка направления нормали
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        if (mid_x * normal[0] + mid_y * normal[1]) < 0:
            normal = (-normal[0], -normal[1])
        return normal


def build_bvh(walls, depth=0, max_depth=20):
    """Рекурсивно строит BVH-дерево с автоматическим определением осей разделения."""

    # Базовый случай - создаём лист
    if len(walls) <= 4 or depth >= max_depth:
        return BVHNode(walls)

    # 1. Вычисляем общий AABB для всех стен
    all_min_x = min(min(wall.start_pos[0], wall.end_pos[0]) for wall in walls)
    all_max_x = max(max(wall.start_pos[0], wall.end_pos[0]) for wall in walls)
    all_min_y = min(min(wall.start_pos[1], wall.end_pos[1]) for wall in walls)
    all_max_y = max(max(wall.start_pos[1], wall.end_pos[1]) for wall in walls)

    # 2. Определяем лучшую ось для разделения (x или y)
    dx = all_max_x - all_min_x
    dy = all_max_y - all_min_y
    axis = 0 if dx > dy else 1  # 0 - ось X, 1 - ось Y

    # 3. Сортируем стены по средней точке на выбранной оси
    walls_sorted = sorted(walls, key=lambda wall: (
            (wall.start_pos[axis] + wall.end_pos[axis]) / 2))  # Средняя точка стены

    # 4. Разделяем стены примерно пополам
    mid = len(walls_sorted) // 2
    left_walls = walls_sorted[:mid]
    right_walls = walls_sorted[mid:]

    # 5. Рекурсивно строим левое и правое поддеревья
    node = BVHNode(walls)  # Создаём узел (но пока без детей)
    node.left = build_bvh(left_walls, depth + 1, max_depth)
    node.right = build_bvh(right_walls, depth + 1, max_depth)

    return node


def draw_bvh(node):
    if node is None:
        return
    min_x, min_y, max_x, max_y = map(int, node.aabb)
    arcade.draw_rect_outline(arcade.rect.XYWH(min_x, min_y, max_x - min_x, max_y - min_y), node.color, 2)
    # Рекурсивно рисуем левую и правую ветви
    draw_bvh(node.left)
    draw_bvh(node.right)


def intersect_bvh_with_counting(node, ray, return_wall=False):
    """Поиск с подсчётом и возвратом стены"""
    if node is None:
        return (None, float('inf'), None) if return_wall else (None, float('inf'))

    if not aabb_intersects_ray(node.aabb, ray):
        return (None, float('inf'), None) if return_wall else (None, float('inf'))

    if node.left is None and node.right is None:
        closest_intersection = None
        min_distance = float('inf')
        hit_wall = None

        for i, wall in enumerate(node.walls):
            intersection = ray.checkCollision(wall)
            if intersection:
                dist = math.hypot(intersection[0] - ray.x, intersection[1] - ray.y)
                if dist < min_distance:
                    min_distance = dist
                    closest_intersection = intersection
                    hit_wall = wall

        if return_wall:
            return closest_intersection, min_distance, hit_wall
        return closest_intersection, min_distance

    left_result = intersect_bvh_with_counting(node.left, ray, return_wall)
    right_result = intersect_bvh_with_counting(node.right, ray, return_wall)

    if return_wall:
        left_intersection, left_dist, left_wall = left_result
        right_intersection, right_dist, right_wall = right_result
        if left_dist < right_dist:
            return left_intersection, left_dist, left_wall
        return right_intersection, right_dist, right_wall
    else:
        left_intersection, left_dist = left_result
        right_intersection, right_dist = right_result
        if left_dist < right_dist:
            return left_intersection, left_dist
        return right_intersection, right_dist

def aabb_intersects_ray(aabb, ray):
    """Проверяет, пересекает ли луч ограничивающий объем (AABB)"""
    min_x, min_y, max_x, max_y = aabb

    if (ray.x < min_x and ray.end_x < min_x) or (ray.x > max_x and ray.end_x > max_x):
        return False
    if (ray.y < min_y and ray.end_y < min_y) or (ray.y > max_y and ray.end_y > max_y):
        return False
    return True

def point_on_segment(p, a, b):
    """Проверяет, лежит ли точка p на отрезке ab."""
    px, py = p
    ax, ay = a
    bx, by = b
    cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax)
    if abs(cross) > 1e-6:
        return False
    min_x = min(ax, bx)
    max_x = max(ax, bx)
    min_y = min(ay, by)
    max_y = max(ay, by)
    return (min_x <= px <= max_x) and (min_y <= py <= max_y)


# Initialize rays
start = 0
end = 90
for i in range(start, end, int(90 / NUM_RAYS)):
    rays.append(Ray(mx, my, math.radians(i)))


def drawRays(rays, walls):
    global lastClosestPoint, bvh_root
    # Sort rays by angle
    sorted_rays = sorted(rays, key=lambda ray: ray.angle)

    # Reset current hits for all walls and mark as not hit this frame
    for wall in walls:
        wall.current_hits = []
        wall.was_hit = False

    # Track extreme rays
    extreme_hits = {'left': None, 'right': None}

    for i, ray in enumerate(sorted_rays):
        closest = MAX_RAY_LEN
        closest_point = None
        closest_wall = None

        for wall in walls:
            intersect = intersect_bvh_with_counting(bvh_root, ray)[0]
            print(intersect)
            if intersect:
                distance = math.sqrt((ray.x - intersect[0]) ** 2 + (ray.y - intersect[1]) ** 2)
                if distance < closest:
                    closest = distance
                    closest_point = intersect
                    closest_wall = wall

        if closest_point is None:
            closest_point = [ray.end_x, ray.end_y]
        if closest_wall:
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
                    dots.append(point)


def drawDots():
    arcade.draw_points(dots, arcade.color.RED, 4)
    if len(dots) > MAX_DOTS:
        dots.remove(dots[0])


def generateWalls(flag=True):
    global bvh_root
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
    bvh_root = build_bvh(walls)


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
