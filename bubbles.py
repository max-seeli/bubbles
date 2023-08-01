"""
@file bubbles.py
@author Maximilian Seeliger (maximilian.seeliger@gmail.com)
@brief An environment for bubbles to move around in and learn to avoid obstacles.
@date 2023-07-31
 
@details This project intends to create a sandbox for experimenting with different 
         kinds of learning algorithms in the context of solving the simple problem
         of bubbles moving around in a 2D environment and learning to avoid obstacles
         and reach a goal.
"""

import tkinter as tk
from random import uniform

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

class Bubble():
    
    def __init__(self, move_sequence=None, move_sequence_length=10, base_color="pink"):
        
        self.base_color = base_color
        self.radius = 5

        # simulation values
        self.x = 0
        self.y = 0
        self.color = self.base_color 
        self.disabled = False
        self.won = False
        self.move_sequence_index = 0

        self.step_size = 10

        self.initialize_move_sequence(move_sequence, move_sequence_length)

    def initialize_move_sequence(self, move_sequence, move_sequence_length):
        if move_sequence is None:
            self.move_sequence = [(uniform(-1, 1), uniform(-1, 1)) for _ in range(move_sequence_length)]
        else:
            self.move_sequence = move_sequence

    def init(self, x, y):
        self.x = x
        self.y = y
        self.color = self.base_color
        self.disabled = False
        self.won = False
        self.move_sequence_index = 0

    def move(self):
        if self.disabled:
            return
        if len(self.move_sequence) > self.move_sequence_index:
            dx, dy = self.move_sequence[self.move_sequence_index]
            self.x += dx * self.step_size
            self.y += dy * self.step_size
            self.move_sequence_index += 1
        else:
            self.disabled = True


    def draw(self, canvas):
        canvas.create_circle(self.x, self.y, self.radius, color=self.color)

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

class Map():
    def __init__(self, start, goal, obstacles, window):
        self.start = start
        self.goal = goal
        self.obstacles = obstacles

        self.window = window
        
        self.distance_start_to_goal = self.start.distance_to_checkpoint(self.goal)
        

        
    def simulate(self, bubbles):
        
        for bubble in bubbles:
            bubble.init(self.start.x, self.start.y)

        def step():
            if all([bubble.disabled for bubble in bubbles]):
                self.window.stop()
                return bubbles
            self.move_bubbles(bubbles)
            self.check_collisions(bubbles)
            
            self.draw(self.window.canvas, bubbles)

        self.window.step_function = step
        self.window.start()
        

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
        if bubble.x - bubble.radius < 0 or bubble.x + bubble.radius > self.window.width or bubble.y - bubble.radius < 0 or bubble.y + bubble.radius > self.window.height:
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

    def draw(self, canvas, bubbles):
        self.start.draw(canvas)
        self.goal.draw(canvas)
        for obstacle in self.obstacles:
            obstacle.draw(canvas)
        for bubble in bubbles:
            bubble.draw(canvas)

class BubbleWindow(tk.Tk):

    class BubbleCanvas(tk.Canvas):
        def __init__(self, master, width, height, bg="white"):
            super().__init__(master, width=width, height=height, bg=bg)
            self.master = master
            self.width = width
            self.height = height

        def create_circle(self, x, y, radius, color="black"):
            self.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color)

    def __init__(self, width, height, step_function=None):
        super().__init__()
        self.width = width
        self.height = height
        
        self.step_function = step_function # function to be called every frame
    
        self.setup()
    
    def setup(self):
        self.title("Bubbles")
        self.canvas = self.BubbleCanvas(self, width=self.width, height=self.height)
        self.canvas.grid(row=0, column=0)

        self.after(1, self.event_loop)

    def event_loop(self):
        self.canvas.delete("all")
        if self.step_function is not None:
            self.step_function()
        self.after(1, self.event_loop)

    def start(self):
        self.mainloop()

    def stop(self):
        self.quit()
