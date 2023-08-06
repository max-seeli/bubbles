from random import random, randint, seed
import numpy as np

from bubbles import *
from window import *

class Map():

    def __init__(self, width, height, start, goal, obstacles, optimal_path):
        self.width = width
        self.height = height
        self.start = start
        self.goal = goal
        self.obstacles = obstacles

        self.optimal_path = optimal_path # list of checkpoints

        self.window = None
        
        self.distance_start_to_goal = max(0, self.start.distance_to_checkpoint(self.goal) - self.start.radius - self.goal.radius)
        
    def simulate(self, bubbles, visualize=True):
        if visualize and self.window is None:
            self.window = BubbleWindow(self.width, self.height)

        for bubble in bubbles:
            bubble.init(self.start.x, self.start.y)

        def step():
            self.move_bubbles(bubbles)
            self.check_collisions(bubbles)

            if visualize:
                self.draw(self.window.canvas, bubbles)
                if all([bubble.disabled for bubble in bubbles]):
                    self.window.stop()

        if visualize:
            self.window.step_function = step
            self.window.start()
        else:
            while not all([bubble.disabled for bubble in bubbles]):
                step()
    
    def move_bubbles(self, bubbles):
        for bubble in bubbles:
            bubble.move()
    

    def check_collisions(self, bubbles):
        for bubble in bubbles:
            if self.bubble_border_collision(bubble) or self.bubble_obstacles_collision(bubble):
                bubble.color = "red"
                bubble.disabled = True
            if self.bubble_goal_collision(bubble):
                bubble.color = "green"
                bubble.disabled = True
                bubble.won = True
    
    def bubble_border_collision(self, bubble):
        if bubble.x - bubble.radius < 0 or bubble.x + bubble.radius > self.width or bubble.y - bubble.radius < 0 or bubble.y + bubble.radius > self.height:
            return True
        return False

    def bubble_obstacles_collision(self, bubble):
        for obstacle in self.obstacles:
            if obstacle.distance_to(bubble.x, bubble.y) < bubble.radius:
                return True
        return False
    
    def bubble_goal_collision(self, bubble):
        if self.goal.distance_to(bubble.x, bubble.y) < bubble.radius + self.goal.radius:
            return True
        return False
    
    def point_in_bounds(self, x, y):
        return x >= 0 and x <= self.width and y >= 0 and y <= self.height
    
    def show(self, info_text=""):
        show_window = BubbleWindow(self.width, self.height)
        show_window.status_text = info_text
        self.draw(show_window.canvas, [])
        self.draw_path(show_window.canvas, self.optimal_path)

        show_window.bind("<Button-1>", lambda _: show_window.close())
        show_window.start()

    def draw(self, canvas, bubbles):
        self.start.draw(canvas)
        self.goal.draw(canvas)
        for obstacle in self.obstacles:
            obstacle.draw(canvas)
        for bubble in bubbles:
            bubble.draw(canvas)

    def draw_path(self, canvas, path):

        for i in range(len(path) - 1):
            canvas.create_line(path[i].x, path[i].y, path[i + 1].x, path[i + 1].y, fill="red", width=10, arrow=tk.LAST)


class Box():
    def __init__(self, x, y, width, height, color="black"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def distance_to(self, x, y):
        dx = max(self.x - x, 0, x - self.x - self.width)
        dy = max(self.y - y, 0, y - self.y - self.height)
        return (dx**2 + dy**2)**0.5

    def draw(self, canvas):
        canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height, fill=self.color)

class Checkpoint():
    def __init__(self, x, y, radius=15, color="orange"):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def distance_to(self, x, y):
        return ((self.x - x)**2 + (self.y - y)**2)**0.5
    
    def distance_to_checkpoint(self, checkpoint):
        return ((self.x - checkpoint.x)**2 + (self.y - checkpoint.y)**2)**0.5

    def draw(self, canvas):
        canvas.create_circle(self.x, self.y, self.radius, color=self.color)

class MapGenerator():
        
    def generate_default_map(self):
        
        width, height = 1000, 1000

        start = Checkpoint(50, 500)
        goal = Checkpoint(950, 500)
        obstacles = [
            Box(200, 400, 30, 600),
            Box(350, 20, 30, 400),
            Box(450, 700, 30, 200),
        ]

        path = self.generate_path(width, height, start, goal, obstacles)

        return Map(width, height, start, goal, obstacles, path)


    def generate(self, width, height):
        start, goal = self.generate_start_goal(width, height)
        obstacles = self.generate_obstacles(height, start, goal)
        path = self.generate_path(width, height, start, goal, obstacles)
        return Map(width, height, start, goal, obstacles, path)

    def generate_start_goal(self, width, height, orientation=0):
        # orientation: 0 = horizontal, 1 = vertical
        orientation_length = width if orientation == 0 else height
        perpendicular_length = height if orientation == 0 else width

        # choose a random start in the second most outest 5% of the map
        a = [orientation_length * 0.05, orientation_length * 0.95]

        b = np.interp([random(), random()], [0, 1], [perpendicular_length * 0.05, perpendicular_length * 0.95])

        x = a if orientation == 0 else b
        y = b if orientation == 0 else a

        start = Checkpoint(x[0], y[0], color="blue")
        goal = Checkpoint(x[1], y[1], color="green")

        return start, goal
    
    def generate_obstacles(self, height, start, goal, n=None):
        
        obstacle_space = [start.x + start.radius, goal.x - goal.radius]
        total_obstacle_space = obstacle_space[1] - obstacle_space[0]
        
        obstacle_width = 30
        min_obstacle_height = 50

        min_obstacle_margin = 50
        
        if n is None:
            n = randint(1, 10)

        total_obstacle_width = obstacle_width * n
        total_obstacle_margin_spaces = n + 1

        obstacle_margin = (total_obstacle_space - total_obstacle_width) // total_obstacle_margin_spaces

        if obstacle_margin < 50:
            n = (total_obstacle_space - min_obstacle_margin) // (obstacle_width + min_obstacle_margin)
            return self.generate_obstacles(height, start, goal, n)

        obstacle_margin_range = [obstacle_margin, obstacle_margin]

        obstacles = []
        
        last_obstacle_x = start.x
        for _ in range(n):
            y = randint(0, height - min_obstacle_height)
            obstacles.append(Box(
                last_obstacle_x + randint(obstacle_margin_range[0], obstacle_margin_range[1]),
                y,
                obstacle_width,
                randint(min_obstacle_height, height - y),
            ))
            last_obstacle_x = obstacles[-1].x + obstacle_width

        return obstacles

    def generate_path(self, width, height, start, goal, obstacles):

        path = self.generate_path_rec(width, height, start, goal, obstacles)
        path = self.backtrack_path(path, obstacles)
        return path    

    def generate_path_rec(self, width, height, start, goal, x_sorted_obstacles):
        
        remaining_obstacles = [obstacle for obstacle in x_sorted_obstacles if obstacle.x + obstacle.width > start.x and obstacle.x < goal.x]

        for obstacle in remaining_obstacles:
            collision = self.find_collision(start, goal, obstacle)

            if not collision["collision"]:
                continue

            if collision["first_collision"] == "left":
                checkpoint1 = Checkpoint(obstacle.x, obstacle.y - 1)
                checkpoint2 = Checkpoint(obstacle.x, obstacle.y + obstacle.height + 1)
                
                path1 = self.generate_path_rec(width, height, start, checkpoint1, x_sorted_obstacles) + self.generate_path_rec(width, height, checkpoint1, goal, x_sorted_obstacles)
                path2 = self.generate_path_rec(width, height, start, checkpoint2, x_sorted_obstacles) + self.generate_path_rec(width, height, checkpoint2, goal, x_sorted_obstacles)
                
                return path1 if self.calculate_path_length(path1) < self.calculate_path_length(path2) else path2
            elif collision["first_collision"] == "top" or collision["first_collision"] == "bottom":
                y_offset = -1 if collision["first_collision"] == "top" else obstacle.height + 1
                checkpoint = Checkpoint(obstacle.x + obstacle.width, obstacle.y + y_offset)
                path = self.generate_path_rec(width, height, start, checkpoint, x_sorted_obstacles) + self.generate_path_rec(width, height, checkpoint, goal, x_sorted_obstacles)
                return path

        return [start, goal]        
    
    def backtrack_path(self, path, obstacles):
        # remove checkpoints that are not necessary
        # e.g. if there is a straight line from start to goal, remove all checkpoints in between
        i = 0
        while i < len(path) - 2:
            if len(self.find_all_collisions(path[i], path[i + 2], obstacles)) == 0:
                path.pop(i + 1)
                i = 0
            else:
                i += 1 
        return path
    
    def find_all_collisions(self, start, goal, obstacles):
        collisions = []
        for obstacle in obstacles:
            collision = self.find_collision(start, goal, obstacle)
            if collision["collision"]:
                collisions.append(collision)
        return collisions
    
    """
    Returns specific collision information

               top
             _______
            |       |
        left|       | right 
            |       |
            |_______|
              bottom

    {
        "left": True/False,
        "right": True/False,
        "top": True/False,
        "bottom": True/False
        "first_collision": "left"/"right"/"top"/"bottom"
    }
    """
    def find_collision(self, start, goal, obstacle):

        # represent the line from start to goal as a np pair of points
        line = np.array([
            [start.x, start.y],
            [goal.x, goal.y]
        ])

        # represent the obstacle as a list of np pairs of points
        obstacle_lines = {
            "top": np.array([
                [obstacle.x, obstacle.y],
                [obstacle.x + obstacle.width, obstacle.y]
            ]),
            "left": np.array([
                [obstacle.x, obstacle.y],
                [obstacle.x, obstacle.y + obstacle.height]
            ]),
            "right": np.array([
                [obstacle.x + obstacle.width, obstacle.y],
                [obstacle.x + obstacle.width, obstacle.y + obstacle.height]
            ]),
            "bottom": np.array([
                [obstacle.x, obstacle.y + obstacle.height],
                [obstacle.x + obstacle.width, obstacle.y + obstacle.height]
            ]),
        } 

        collsion_info = {
            "collision": False,
            "left": False,
            "right": False,
            "top": False,
            "bottom": False,
            "first_collision": None
        }

        intersection_points = {
            "left": None,
            "right": None,
            "top": None,
            "bottom": None
        }

        # check if the line intersects with any of the obstacle lines
        for side, obstacle in obstacle_lines.items():
            intersection = self.line_intersection(line, obstacle)
            if intersection is not None:
                collsion_info[side] = True
                collsion_info["collision"] = True
                intersection_points[side] = intersection
                if side == "left":
                    collsion_info["first_collision"] = "left"

        if collsion_info["collision"] and collsion_info["first_collision"] is None:
            # check if distance to top or bottom is smaller
            if intersection_points["top"] is None:
                collsion_info["first_collision"] = "bottom"
            elif intersection_points["bottom"] is None:
                collsion_info["first_collision"] = "top"
            else:
                if start.distance_to(
                    intersection_points["top"][0],
                    intersection_points["top"][1]
                    ) < start.distance_to(
                    intersection_points["bottom"][0],
                    intersection_points["bottom"][1]):
                    collsion_info["first_collision"] = "top"
                else:
                    collsion_info["first_collision"] = "bottom"

        return collsion_info


    def line_intersection(self, line1, line2):
        # Calculate the intersection point of two line segments.
        p1, p2 = line1
        p3, p4 = line2
        v1 = p2 - p1
        v2 = p4 - p3
        
        cp = np.cross(v1, v2)
        # check if the lines are parallel
        if cp == 0:
            return None

        # check if the intersection point is within the line segments
        b = p3 - p1
        s = np.cross(b, v2) / cp
        t = np.cross(b, v1) / cp

        if s >= 0 and s <= 1 and t >= 0 and t <= 1:
            return p1 + s * v1        
        return None
        
    def calculate_path_length(self, path):
        length = 0
        for i in range(len(path) - 1):
            length += path[i].distance_to_checkpoint(path[i + 1])
        return length

if __name__ == "__main__":
    while True:
        current_seed = randint(0, 1000000000)
        print("Seed:", current_seed)
        seed(current_seed)
        map = MapGenerator().generate(1000, 1000)
        map.show()
