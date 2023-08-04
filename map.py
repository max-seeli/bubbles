import time

from bubbles import *
from window import *

class Map():

    def __init__(self, width, height, start, goal, obstacles):
        self.width = width
        self.height = height
        self.start = start
        self.goal = goal
        self.obstacles = obstacles

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
    
    def show_map(self):
        show_window = BubbleWindow(self.width, self.height)
        self.draw(show_window.canvas, [])
        show_window.bind("<Button-1>", lambda _: show_window.close())
        show_window.start()

    def draw(self, canvas, bubbles):
        self.start.draw(canvas)
        self.goal.draw(canvas)
        for obstacle in self.obstacles:
            obstacle.draw(canvas)
        for bubble in bubbles:
            bubble.draw(canvas)


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

def generate_map():
    width, height = 1000, 1000

    start = Checkpoint(50, 500)
    goal = Checkpoint(950, 500)
    obstacles = [
        Box(200, 400, 30, 600),
        Box(350, 20, 30, 400),
        Box(450, 700, 30, 200),
    ]

    return Map(width, height, start, goal, obstacles)


if __name__ == "__main__":
    map = generate_map()
    map.show_map()
