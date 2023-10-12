# GA

import random
import numpy as np
from monopoly import play
from prettytable import PrettyTable
import logging
import datetime
import os

epochs = 1
population_size = 1
resolution = 4
base = 1
acceptable_value = 5000
crossover_rate = 0.6
beta = 0.2
mutation_rate = 0.2
elitism_size = 1

logging.info('')
logging.info(f"PARAMETERS OF SIMULATION")
logging.info(f"EPOCHS: {epochs}")
logging.info(f"POPULATION_SIZE: {population_size}")
logging.info(f"RESOLUTION: {resolution}")
logging.info(f"BASE: {base}")
logging.info(f"ACCETABLE_VALUE: {acceptable_value}")
logging.info(f"CROSSOVER_RATE: {crossover_rate}")
logging.info(f"MUTATION_RATE: {mutation_rate}")
logging.info(f"ELITISM_SIZE: {elitism_size}")
logging.info('')

def genetic_algorithm(epochs, population_size, resolution, base, acceptable_value, crossover_rate, beta, mutation_rate, elitism_size):
    
    # create first generation
    logging.info("Creating the first generation")
    solutions = []
    for _ in range(population_size):
        to_add = []
        for _ in range(resolution):
            to_add.append(random.uniform(-base, base))
        solutions.append(to_add)

    for i in range(len(solutions)):
        logging.info(f"Solution {i}: {solutions[i]}")
    
    # initiate GA
    ranked_solutions = []
    for i in range(epochs):
        
        # apply fitness function
        logging.info('')
        logging.info(f"Applying fitness function (Play monopoly)")
        logging.info('')
        for s in solutions:
            result = play(s)
            print("RESULTADO: ")
            print(result)
            print("\n")

            logging.info('')
            logging.info(f"Applyed solution: {s} - Result: {result}")

            ranked_solutions.append((result,s))

        logging.info('Ranking the solutions:')
        
        ranked_solutions.sort()
        for solution in ranked_solutions:
            logging.info(f"{solution}")
        
        # show best result
        print(f"GENERATION {i} BEST SOLUTIONS")
        logging.info('')
        logging.info('BEST SOLUTION:')
        logging.info(f"{ranked_solutions[population_size - 1]}")
        print(ranked_solutions[population_size - 1])
        
        # condition to stop
        if ranked_solutions[population_size - 1][0] >= acceptable_value:
            break
        
        # selection (roulette wheel)
        results = [x[0] for x in ranked_solutions]
        sum_value = sum(results)
        cumulative_probs_selection = [x/sum_value for x in results]
        for i in range(1, population_size):
            cumulative_probs_selection[i] += cumulative_probs_selection[i - 1]
        
        new_gen = []
        for i in range(population_size):
            chosen = random.uniform(0, 1)
            for j in range(population_size):
                if chosen <= cumulative_probs_selection[j] or j == population_size - 1:
                    new_gen.append(ranked_solutions[j][1])
                    break
        new_gen = np.random.permutation(new_gen)
        
        # crossover (radcliff)
        for i in range(int(population_size/2)):
            prob_cross = random.uniform(0, 1)
            if prob_cross <= crossover_rate:
                parent1_location = i*2
                parent2_location = parent1_location + 1
                son1 = new_gen[parent1_location]
                son2 = new_gen[parent2_location]
                for j in range(resolution):
                    son1[j] = new_gen[parent1_location][j] + ((1 - beta)*new_gen[parent2_location][j])
                    if son1[j] > base:
                        son1[j] = base
                    if son1[j] < -base:
                        son1[j] = -base
                    son2[j] = ((1 - beta)*new_gen[parent1_location][j]) + new_gen[parent2_location][j]
                    if son2[j] > base:
                        son2[j] = base
                    if son2[j] < -base:
                        son2[j] = -base
                new_gen[parent1_location] = son1
                new_gen[parent2_location] = son2
        
        # mutation
        for i in range(population_size):
            for j in range(resolution):
                prob_mut = random.uniform(0, 1)
                if prob_mut <= mutation_rate:
                    new_value = new_gen[i][j]
                    while new_value == new_gen[i][j]:
                        new_value = random.uniform(-base, base)
                    new_gen[i][j] = new_value
        
        # elitism
        # print(ranked_solutions)
        # print(new_gen)
        for i in range(elitism_size):
            print(i)
            new_gen[i] = ranked_solutions[population_size - 1 - i][1]
        # print(new_gen)
        
        solutions = new_gen
    print()
    print(f"Final Ranked solutions: {ranked_solutions}")
        
    return ranked_solutions[population_size - 1]


genetic_algorithm(epochs, population_size, resolution, base, acceptable_value, crossover_rate, beta, mutation_rate, elitism_size)