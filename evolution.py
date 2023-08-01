"""
@file evolution.py
@author Maximilian Seeliger (maximilian.seeliger@gmail.com)
@brief An evolutionary algorithm (genetic algorithm) to find a solution to the path
       finding problem defined in the map.
@date 2023-08-1
 
@details The evolutionary algorithm uses the linear distance to the goal as a fitness
         function and uses crossover and mutation to evolve the population.
"""

from random import random, randint, gauss, seed
from numpy import polyfit, poly1d
from bubbles import *

class EvolutionaryAlgorithm():
    def __init__(self, map, population_size=1000, mutation_rate=0.05, mutation_strength=0.3):
        self.map = map
        
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength

        self.population = []
        self.solution_length = 200
        
        self.initialize_population()

    def initialize_population(self):
        self.population = [Bubble(move_sequence_length=self.solution_length) 
                           for _ in range(self.population_size)]        

    def evaluate_population(self):
        
        coefficients = polyfit([0, self.map.distance_start_to_goal], [1, 0], deg=1)
        distance_to_fitness = poly1d(coefficients)
        
        for bubble in self.population:
            bubble.fitness = distance_to_fitness(self.evaluate_distance(bubble))
    

    def evaluate_distance(self, bubble):
        distance = self.map.goal.distance_to(bubble.x, bubble.y)
        return distance

    def natural_selection(self):
        
        survivors = self.population[:int(self.population_size / 2)]
        lucky_losers = self.population[int(self.population_size / 2):]
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
        cutoff = randint(0, self.solution_length)
        return Bubble(move_sequence=mother.move_sequence[:cutoff] + father.move_sequence[cutoff:])

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
        self.population = sorted(self.population, key=lambda bubble: bubble.fitness, reverse=True)
        best = self.population[0].fitness
        avg = sum([bubble.fitness for bubble in self.population]) / len(self.population)

        survivors = self.natural_selection()
        offspring = self.breed(survivors, self.population_size - len(survivors))
        self.mutate(survivors)
        
        self.population = survivors + offspring

        return best, avg


if __name__ == "__main__":

    seed(0)

    window = BubbleWindow(1000, 1000)

    start = Checkpoint(50, 500)
    goal = Checkpoint(950, 500)
    obstacles = [
        Box(200, 400, 30, 600),
        Box(350, 20, 30, 400),
        Box(450, 700, 30, 200),
    ]

    map = Map(start, goal, obstacles, window)

    evolution = EvolutionaryAlgorithm(map)
    
    status_text = tk.StringVar(value="Starting...")
    label = tk.Label(window, textvariable=status_text, fg="black", font=("Helvetica", 16))
    label.grid(row=1, column=0)

    for i in range(100): # 100 generations
        
        best, avg = evolution.run()
        
        status = "Generation: {} Best: {:.2f}% Avg: {:.2f}%".format(i + 1, best * 100, avg * 100)
        status_text.set(status)
        print(status)