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
from random import randint, random, uniform, gauss

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
    
    def __init__(self, x, y, color="blue"):
        self.x = x
        self.y = y
        self.radius = 5
        self.color = color

        self.disabled = False

        self.step_size = 10
    

    def initialize_move_sequence(self, move_sequence=None, length=10):
        if move_sequence is None:
            self.move_sequence = [(uniform(-1, 1), uniform(-1, 1)) for _ in range(length)]
        else:
            self.move_sequence = move_sequence
    
    def move(self, sequence_index):
        if self.disabled:
            return
        if len(self.move_sequence) > sequence_index:
            dx, dy = self.move_sequence[sequence_index]
            self.x += dx * self.step_size
            self.y += dy * self.step_size
        else:
            self.disabled = True

    def draw(self, canvas):
        canvas.create_oval(self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius, fill=self.color)

class Map():
    def __init__(self, start, goal, obstacles):
        self.start = start
        self.goal = goal
        self.checkpoint_radius = 15
        self.obstacles = obstacles

        self.window = BubbleWindow()

        
    def simulate(self, bubbles):
        sequence_index = 0
        for bubble in bubbles:
            bubble.disabled = False
            bubble.x = self.start["x"]
            bubble.y = self.start["y"]
            bubble.color = "blue"

        def step():
            nonlocal sequence_index
            if all([bubble.disabled for bubble in bubbles]):
                self.window.stop()
                return bubbles
            map.move_bubbles(bubbles, sequence_index)
            sequence_index += 1
            map.check_collisions(bubbles)
            
            map.draw(self.window.canvas, bubbles)

        self.window.step_function = step
        self.window.start()
        

    def move_bubbles(self, bubbles, sequence_index):
        for bubble in bubbles:
            bubble.move(sequence_index)
    

    def check_collisions(self, bubbles):
        for bubble in bubbles:
            if self.bubble_border_collision(bubble) or self.bubble_obstacles_collision(bubble):
                bubble.color = "red"
                bubble.disabled = True
            if self.bubble_goal_collision(bubble):
                bubble.color = "green"
                bubble.disabled = True
    
    def bubble_border_collision(self, bubble):
        if bubble.x - bubble.radius < 0 or bubble.x + bubble.radius > MAP_WIDTH or bubble.y - bubble.radius < 0 or bubble.y + bubble.radius > MAP_HEIGHT:
            return True
        return False

    def bubble_obstacles_collision(self, bubble):
        for obstacle in self.obstacles:
            if bubble.x + bubble.radius > obstacle.x and bubble.x - bubble.radius < obstacle.x + obstacle.width and bubble.y + bubble.radius > obstacle.y and bubble.y - bubble.radius < obstacle.y + obstacle.height:
                return True
        return False
    
    def bubble_goal_collision(self, bubble):
        if ((bubble.x - goal["x"])**2 + (bubble.y - goal["y"])**2)**0.5 < bubble.radius + self.checkpoint_radius:
            return True
        return False

    def draw(self, canvas, bubbles):
        canvas.create_oval(self.start["x"] - self.checkpoint_radius, self.start["y"] - self.checkpoint_radius, self.start["x"] + self.checkpoint_radius, self.start["y"] + self.checkpoint_radius, fill="green")
        canvas.create_oval(self.goal["x"] - self.checkpoint_radius, self.goal["y"] - self.checkpoint_radius, self.goal["x"] + self.checkpoint_radius, self.goal["y"] + self.checkpoint_radius, fill="red")
        for obstacle in self.obstacles:
            obstacle.draw(canvas)
        for bubble in bubbles:
            bubble.draw(canvas)

class BubbleWindow():
    def __init__(self, step_function=None, framerate=10):
        self.step_function = step_function
        self.framerate = framerate
    
        self.setup()
    
    def setup(self):
        self.root = tk.Tk()
        self.root.title("Bubbles")
        self.canvas = tk.Canvas(self.root, width=MAP_WIDTH, height=MAP_HEIGHT, bg="white")
        self.canvas.grid(row=0, column=0)

        self.root.after(int(1000 / self.framerate), self.event_loop)

    def event_loop(self):
        self.canvas.delete("all")
        if self.step_function is not None:
            self.step_function()
        self.root.after(int(1000 / self.framerate), self.event_loop)

    def start(self):
        self.root.mainloop()

    def stop(self):
        self.root.quit()
        

class EvolutionaryAlgorithm():
    def __init__(self, map, population_size=100, mutation_rate=0.01, mutation_strength=0.1):
        self.map = map
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength

        self.population = []
        self.solution_length = 100
        self.initialize_population()

    def initialize_population(self):
        for _ in range(self.population_size):
            bubble = Bubble(self.map.start["x"], self.map.start["y"])
            bubble.initialize_move_sequence(length=self.solution_length)
            self.population.append(bubble)        

    def evaluate_population(self):
        for bubble in self.population:
            bubble.fitness = self.evaluate_performance(bubble)
    
    def evaluate_performance(self, bubble):
        distance = (bubble.x - self.map.goal["x"])**2 + (bubble.y - self.map.goal["y"])**2
        return -distance

    def natural_selection(self):
        sorted_population = sorted(self.population, key=lambda bubble: bubble.fitness, reverse=True)
        
        survivors = sorted_population[:int(self.population_size / 2)]
        lucky_losers = sorted_population[int(self.population_size / 2):]
        for bubble in lucky_losers:
            if random() < 0.1:
                survivors.append(bubble)

        return survivors

    def breed(self, parents, n):
        offspring = []
        for _ in range(n):
            mother = parents[randint(0, len(parents) - 1)]
            father = parents[randint(0, len(parents) - 1)]

            child = self.crossover(mother, father)
            self.mutate(child)

            offspring.append(child)
        return offspring
        
    def crossover(self, mother, father):
        ms1 = mother.move_sequence
        ms2 = father.move_sequence

        selection = [0 if random() < 0.5 else 1 for _ in range(self.solution_length)]
        ms = []
        for s in zip(ms1, ms2, selection):
            ms.append(s[s[2]])

        child = Bubble(self.map.start["x"], self.map.start["y"])        
        child.initialize_move_sequence(move_sequence=ms)
        return child

    def mutate(self, bubbles):
        # handle lists and single items
        if type(bubbles) != list:
            bubbles = [bubbles]
        for bubble in bubbles:    
            for i in range(self.solution_length):
                if random() < self.mutation_rate:
                    bubble.move_sequence[i] = (
                        bubble.move_sequence[i][0] + gauss(0, self.mutation_strength),
                        bubble.move_sequence[i][1] + gauss(0, self.mutation_strength)
                    )


    def run(self):
        self.map.simulate(self.population)
        self.evaluate_population()
        survivors = self.natural_selection()
        print(len(survivors))
        self.mutate(survivors)
        offspring = self.breed(survivors, self.population_size - len(survivors))

        self.population = survivors + offspring
        

start = {
    "x": 50,
    "y": 500
}

goal = {
    "x": 950,
    "y": 500
}

obstacles = [
    Box(200, 400, 30, 600),
    Box(350, 20, 30, 400),
    Box(450, 700, 30, 200),
]

map = Map(start, goal, obstacles)

evolution = EvolutionaryAlgorithm(map, population_size=100, mutation_rate=0.05, mutation_strength=0.1)
for _ in range(100):
    evolution.run()