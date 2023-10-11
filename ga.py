# GA

import random
import numpy as np
from monopoly import executar_simulacoes


def genetic_algorithm(epochs, population_size, resolution, base, acceptable_value, crossover_rate, beta, mutation_rate, elitism_size):
    
    # create first generation
    solutions = []
    for _ in range(population_size):
        to_add = []
        for _ in range(resolution):
            to_add.append(random.uniform(-base, base))
        solutions.append(to_add)
    
    # initiate GA
    rankedsolutions = []
    for i in range(epochs):
        
        # apply fitness function
        for s in solutions:
            rankedsolutions.append((executar_simulacoes(s[0],s[1]),s))
        rankedsolutions.sort()
        
        # show best result
        print(f"=== Gen {i} best solutions === ")
        print(rankedsolutions[population_size - 1])
        
        # condition to stop
        if rankedsolutions[population_size - 1][0] >= acceptable_value:
            break
        
        # selection (roulette wheel)
        results = [x[0] for x in rankedsolutions]
        sum_value = sum(results)
        cumulative_probs_selection = [x/sum_value for x in results]
        for i in range(1, population_size):
            cumulative_probs_selection[i] += cumulative_probs_selection[i - 1]
        
        new_gen = []
        for i in range(population_size):
            chosen = random.uniform(0, 1)
            for j in range(population_size):
                if chosen <= cumulative_probs_selection[j] or j == population_size - 1:
                    new_gen.append(rankedsolutions[j][1])
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
        print(rankedsolutions)
        print(new_gen)
        for i in range(elitism_size):
            print(i)
            new_gen[i] = rankedsolutions[population_size - 1 - i][1]
        print(new_gen)
        
        solutions = new_gen
        
    return rankedsolutions[population_size - 1]

epochs = 1
population_size = 10
resolution = 2
base = 0.5
acceptable_value = 500
crossover_rate = 0.6
beta = 0.2
mutation_rate = 0.2
elitism_size = 1
print(genetic_algorithm(epochs, population_size, resolution, base, acceptable_value, crossover_rate, beta, mutation_rate, elitism_size))