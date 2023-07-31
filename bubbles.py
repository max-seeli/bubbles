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
from random import randint

MAP_WIDTH = 1000
MAP_HEIGHT = 1000

class Box():
    def __init__(self, x, y, width, height, color="black"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, canvas):
        canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height, fill=self.color)

class Bubble():
    
    MOVES = [
            (1, 0), # right
            (0, 1), # down
            (-1, 0), # left
            (0, -1), # up
    ]
    
    def __init__(self, x, y, color="blue"):
        self.x = x
        self.y = y
        self.radius = 5
        self.color = color

        self.step_size = 10
    

    def initialize_move_sequence(self, move_sequence=None, length=10):
        if move_sequence is None:
            self.move_sequence = [randint(0, 3) for _ in range(length)]
        else:
            self.move_sequence = move_sequence
    
    def move(self):
        if len(self.move_sequence) > 0:
            dx, dy = self.MOVES[self.move_sequence[0]]
            self.x += dx * self.step_size
            self.y += dy * self.step_size
            self.move_sequence = self.move_sequence[1:]

    def draw(self, canvas):
        canvas.create_oval(self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius, fill=self.color)

class Map():
    def __init__(self, start, goal, obstacles):
        self.start = start
        self.goal = goal
        self.checkpoint_radius = 15
        self.obstacles = obstacles
        
        self.bubbles = []
        
        self.eliminated_bubbles = []
        self.won_bubbles = []

    def add_bubbles(self, n=1):
        for _ in range(n):
            bubble = Bubble(self.start["x"], self.start["y"])

            bubble.initialize_move_sequence()
            self.bubbles.append(bubble)

    def move_bubbles(self):
        for bubble in self.bubbles:
            bubble.move()
    

    def check_collisions(self):
        collisions = []
        winners = []
        for bubble in self.bubbles:
            if bubble.x - bubble.radius < 0 or bubble.x + bubble.radius > MAP_WIDTH or bubble.y - bubble.radius < 0 or bubble.y + bubble.radius > MAP_HEIGHT:
                collisions.append(bubble)
            if ((bubble.x - goal["x"])**2 + (bubble.y - goal["y"])**2)**0.5 < bubble.radius + self.checkpoint_radius:
                winners.append(bubble)
            for obstacle in self.obstacles:
                if bubble.x + bubble.radius > obstacle.x and bubble.x - bubble.radius < obstacle.x + obstacle.width and bubble.y + bubble.radius > obstacle.y and bubble.y - bubble.radius < obstacle.y + obstacle.height:
                    collisions.append(bubble)
        for bubble in collisions:
            bubble.color = "red"
            self.bubbles.remove(bubble)
            self.eliminated_bubbles.append(bubble)
        for bubble in winners:
            bubble.color = "green"
            self.bubbles.remove(bubble)
            self.won_bubbles.append(bubble)

    def draw(self, canvas):
        canvas.create_oval(self.start["x"] - self.checkpoint_radius, self.start["y"] - self.checkpoint_radius, self.start["x"] + self.checkpoint_radius, self.start["y"] + self.checkpoint_radius, fill="green")
        canvas.create_oval(self.goal["x"] - self.checkpoint_radius, self.goal["y"] - self.checkpoint_radius, self.goal["x"] + self.checkpoint_radius, self.goal["y"] + self.checkpoint_radius, fill="red")
        for obstacle in self.obstacles:
            obstacle.draw(canvas)
        for bubble in self.bubbles + self.eliminated_bubbles + self.won_bubbles:
            bubble.draw(canvas)


# create the window
root = tk.Tk()
root.title("Bubbles")

# create a canvas to draw on
canvas = tk.Canvas(root, width=MAP_WIDTH, height=MAP_HEIGHT, bg="white")
canvas.grid(row=0, column=0)

start = {
    "x": 50,
    "y": 500
}

goal = {
    "x": 950,
    "y": 500
}

obstacles = [
    Box(200, 200, 30, 600),
    Box(350, 20, 30, 400),
    Box(450, 700, 30, 200),
]

map = Map(start, goal, obstacles)
map.add_bubbles(n=10)

framerate = 10

# start the event loop
def event_loop():
    map.move_bubbles()
    map.check_collisions()
    canvas.delete("all")
    map.draw(canvas)
    
    root.after(int(1000 / framerate), event_loop)

root.after(int(1000 / framerate), event_loop)
root.mainloop()
