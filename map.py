from random import random, randint
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

        self.optimal_path = optimal_path

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
    
    def show(self):
        show_window = BubbleWindow(self.width, self.height)
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
        # path is a list of Checkpoints
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
        
    def generate(self, width, height):
        start, goal = self.generate_start_goal(width, height)
        optimal_path = self.generate_path(width, height, start, goal)
        obstacles = self.generate_obstacles_for_optimal_path(width, height, optimal_path)
        return Map(width, height, start, goal, obstacles, optimal_path)

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
        

    def generate_path(self, width, height, start, goal):
        
        direct_path = np.array([goal.x - start.x, goal.y - start.y], dtype=np.float64)
        unit_direct_path = direct_path / np.linalg.norm(direct_path)
        direct_path_length = np.linalg.norm(direct_path)

        perpendicular_path = np.array([direct_path[1], -direct_path[0]], dtype=np.float64)
        unit_perpendicular_path = perpendicular_path / np.linalg.norm(perpendicular_path)

        checkpoints = [start]
        
        num_checkpoints = 10
        path_length_per_checkpoint = direct_path_length / (num_checkpoints +1)

        for _ in range(num_checkpoints):
            perpendicular_adjustment = unit_perpendicular_path * (random() - 0.5) * 2 * path_length_per_checkpoint
            checkpoints.append(Checkpoint(
                max(width * 0.05, min(width - 0.05 * width, checkpoints[-1].x + unit_direct_path[0] * path_length_per_checkpoint + perpendicular_adjustment[0])),
                max(height * 0.05, min(height - 0.05 * height, checkpoints[-1].y + unit_direct_path[1] * path_length_per_checkpoint + perpendicular_adjustment[1])),
            ))
        
        # adjust the last checkpoint to be the goal
        checkpoints.append(goal)

        return checkpoints

    def generate_obstacles_for_optimal_path(self, width, height, optimal_path):
        obstacles = []

        gap = 40
        size = 5

        for path_checkpoint in optimal_path[1:-2]:
            obstacles.append(Box(
                path_checkpoint.x - size / 2,
                0,
                size,
                path_checkpoint.y - gap / 2
            ))
            obstacles.append(Box(
                path_checkpoint.x - size / 2,
                path_checkpoint.y + gap / 2,
                size,
                height - path_checkpoint.y - gap / 2
            ))
        
        return obstacles

    
def generate_default_map():
    width, height = 1000, 1000

    start = Checkpoint(50, 500)
    goal = Checkpoint(950, 500)
    obstacles = [
        Box(200, 400, 30, 600),
        Box(350, 20, 30, 400),
        Box(450, 700, 30, 200),
    ]

    return Map(width, height, start, goal, obstacles, [start, goal])

if __name__ == "__main__":
    map = MapGenerator().generate(1000, 1000)
    map.show()
