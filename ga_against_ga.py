# GA

import random
import numpy as np
from monopoly import play
from prettytable import PrettyTable
import logging
import datetime
import os

epochs = 1000
population_size = 5
resolution = 4
base = 1
acceptable_value = 4
crossover_rate = 0.6
beta = 0.2
mutation_rate = 0.2
elitism_size = 1
consecutive_epochs = 5
n_players_per_match = resolution

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
logging.info(f"CONSECUTIVE_EPOCHS: {consecutive_epochs}")
logging.info('')

def genetic_algorithm(epochs, population_size, resolution, base, acceptable_value, consecutive_epochs, crossover_rate, beta, mutation_rate, elitism_size):
    
    # create first generation
    logging.info("Creating the first generation")
    current_solutions = []
    last_best_solution = [-2,-2,-2,-2,-2]
    count_same_best = 0
    for _ in range(population_size):
        to_add = []
        for _ in range(resolution):
            to_add.append(random.uniform(-base, base))
        current_solutions.append(to_add)

    for i in range(len(current_solutions)):
        logging.info(f"Solution {i}: {current_solutions[i]}")
    
    # initiate GA
    for current_epoch in range(epochs):
        
        # apply fitness function
        logging.info('')
        logging.info(f"EPOCH: {current_epoch+1} - Applying fitness function (Play monopoly)")
        logging.info('')
        ranked_current_solutions = []

        result = play(current_solutions, n_players_per_match)

        print("RESULTADO: ")
        print(result)
        print("\n")

        for index in range(population_size):
            ranked_current_solutions.append((result[index],current_solutions[index]))

        ranked_current_solutions = sorted(ranked_current_solutions, key=lambda x: x[0])
        logging.info('EPOCH: {current_epoch+1} - Sorted ranked solutions:')
        for solution in ranked_current_solutions:
            logging.info(f"{solution}")
        
        # show best result
        logging.info(f"EPOCH: {current_epoch+1} - BEST SOLUTION")
        logging.info('')
        logging.info(f"{ranked_current_solutions[population_size - 1]}")
        print(ranked_current_solutions[population_size - 1])
        

        # condition to stop
        tolerance = 1e-4  # Defina a tolerância conforme necessário
        logging.info('')
        logging.info(f'Reached stop condition?')
        logging.info('')
        
        if ranked_current_solutions[population_size - 1][0] >= acceptable_value:
            if all(abs(a - b) < tolerance for a, b in zip(ranked_current_solutions[population_size - 1][1], last_best_solution)):
                count_same_best += 1
                logging.info(f'Consecutive best: {count_same_best}')
                if count_same_best >= consecutive_epochs-1:
                    logging.info('YES')
                    logging.info(f'FINAL EPOCH: {current_epoch+1}')
                    break
            else:
                last_best_solution = ranked_current_solutions[population_size - 1][1]
                count_same_best = 0
        logging.info('NO')

        logging.info('')
        logging.info('Applying selection throw roulette wheel')
        logging.info('')
        # selection (roulette wheel)
        results = [x[0] for x in ranked_current_solutions]
        sum_value = sum(results)
        cumulative_probs_selection = [x/sum_value for x in results]
        for index in range(1, population_size):
            cumulative_probs_selection[index] += cumulative_probs_selection[index - 1]
        
        new_gen = []
        for _ in range(population_size):
            chosen = random.uniform(0, 1)
            for index_pop in range(population_size):
                if chosen <= cumulative_probs_selection[index_pop] or index_pop == population_size - 1:
                    new_gen.append(ranked_current_solutions[index_pop][1])
                    break
        new_gen = np.random.permutation(new_gen)

        logging.info('')
        logging.info(f'New generation after roulette wheel:\n {new_gen}')
        logging.info('')

        logging.info('')
        logging.info('Applying crossover')
        logging.info('')
        
        # crossover (radcliff)
        for idx in range(int(population_size/2)):
            prob_cross = random.uniform(0, 1)
            if prob_cross <= crossover_rate:
                parent1_location = idx*2
                parent2_location = parent1_location + 1
                son1 = new_gen[parent1_location]
                son2 = new_gen[parent2_location]
                for coef_index in range(resolution):
                    son1[coef_index] = new_gen[parent1_location][coef_index] + ((1 - beta)*new_gen[parent2_location][coef_index])
                    if son1[coef_index] > base:
                        son1[coef_index] = base
                    if son1[coef_index] < -base:
                        son1[coef_index] = -base
                    son2[coef_index] = ((1 - beta)*new_gen[parent1_location][coef_index]) + new_gen[parent2_location][coef_index]
                    if son2[coef_index] > base:
                        son2[coef_index] = base
                    if son2[coef_index] < -base:
                        son2[coef_index] = -base
                new_gen[parent1_location] = son1
                new_gen[parent2_location] = son2

        logging.info('')
        logging.info(f'New generation after crossover:\n {new_gen}')
        logging.info('')

        logging.info('')
        logging.info('Applying mutation')
        logging.info('')
        
        # mutation
        for pop_index in range(population_size):
            for coef_index in range(resolution):
                prob_mut = random.uniform(0, 1)
                if prob_mut <= mutation_rate:
                    new_value = new_gen[pop_index][coef_index]
                    while new_value == new_gen[pop_index][coef_index]:
                        new_value = random.uniform(-base, base)
                    new_gen[pop_index][coef_index] = new_value
        

        logging.info('')
        logging.info(f'New generation after mutation:\n {new_gen}')
        logging.info('')


        logging.info('')
        logging.info('Applying elitism')
        logging.info('')

        for elitsim_index in range(elitism_size):
            if ranked_current_solutions[population_size - 1 - elitsim_index][0] >= acceptable_value:
                new_gen[elitsim_index] = ranked_current_solutions[population_size - 1 - elitsim_index][0]
        
        solutions = new_gen

        logging.info('')
        logging.info(f'New generation after elitism:\n {solutions}')
        logging.info('')
        logging.info(f"ENDING: EPOCH {current_epoch+1}")
        logging.info('')

    logging.info('')
    logging.info(f'Solutions returned: {ranked_current_solutions[population_size - 1]}')
    logging.info('')

        
    return ranked_current_solutions[population_size - 1]


genetic_algorithm(epochs, population_size, resolution, base, acceptable_value, consecutive_epochs, crossover_rate, beta, mutation_rate, elitism_size)