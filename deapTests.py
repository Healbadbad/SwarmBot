import random
from deap import creator, base, tools, algorithms

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_bool", random.uniform, -100, 100)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalOneMax(individual):
    return 1/(individual[0]*individual[0] +1)

toolbox.register("evaluate", evalOneMax)
toolbox.register("mate", tools.cxBlend, alpha = 0.2)
toolbox.register("mutate", tools.mutGaussian, indpb=0.9, mu=5, sigma=2)
toolbox.register("select", tools.selTournament, tournsize=3)

# tools.crossover.cxBlend

population = toolbox.population(n=300)

NGEN=40
for gen in range(NGEN):
    offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.1)
    fits = toolbox.map(toolbox.evaluate, offspring)
    for fit, ind in zip(fits, offspring):
        ind.fitness.values = [fit]
    population = toolbox.select(offspring, k=len(population))
top10 = tools.selBest(population, k=10)
print top10

ind = toolbox.individual()
ind.