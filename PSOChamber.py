# from Starbot import Starbot
import time

import random
from deap import creator, base, tools, algorithms
import math
import subprocess
from array import array
from multiprocessing.pool import ThreadPool
import threading
from queue import PriorityQueue
import numpy as np
from deap import benchmarks
import operator

def evalAgent(individual):
	''' Launches a subprocess of Starbot.py with given parameters, and returns
		The final Score earned by this individual
	'''
	appPath = 'python'
	readyForCommand = False

	commandAndArgs = [appPath, 'Starbot.py'] 
	process = subprocess.Popen(commandAndArgs, 
	                           stdin=subprocess.PIPE, 
	                           stdout=subprocess.PIPE, 
	                           stderr=subprocess.STDOUT)

	theOut = ''
	while theOut != "b'QQQ'":
		theOut = str(process.stdout.readline().rstrip())

	toSend = '' #+ str(index) + ' '
	for item in individual:
		toSend = toSend + str(item) + ' '
	toSend = toSend[:-1] + '\n'
	a = toSend.encode('ascii')
	print(a)
	theOut = str(process.communicate(a)[0].rstrip()) #b"1 2 3 4 5\n"

	score = int(theOut.split("\\")[2][1:])
	print(score)
	return (score,)

def evalAgentsThreaded(offspring):
	fits = []
	pool = ThreadPool(processes=8)

	rets = pool.map(toolbox.evaluate, offspring)
	return rets

def xfunc(part):
	return (1/((part[0]*part[0])*(part[1]*part[1]) + 1),)

def generate(size, pmin, pmax, smin, smax):
    part = creator.Particle([
    random.uniform(-10,10),	random.uniform(-10,10),	random.uniform(-10,10),	random.uniform(-10,10),	random.uniform(-10,10),	random.uniform(50,150),	random.uniform(-10,10),	random.uniform(1,5)])
    part.speed = [random.uniform(smin, smax) for _ in range(size)]
    part.smin = smin
    part.smax = smax
    return part

def updateParticle(part, best, phi1, phi2):
    u1 = (random.uniform(0, phi1) for _ in range(len(part)))
    u2 = (random.uniform(0, phi2) for _ in range(len(part)))
    v_u1 = map(operator.mul, u1, map(operator.sub, part.best, part))
    v_u2 = map(operator.mul, u2, map(operator.sub, best, part))
    part.speed = list(map(operator.add, part.speed, map(operator.add, v_u1, v_u2)))
    for i, speed in enumerate(part.speed):
        if speed < part.smin:
            part.speed[i] = part.smin
        elif speed > part.smax:
            part.speed[i] = part.smax
    part[:] = list(map(operator.add, part, part.speed))


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Particle", list, fitness=creator.FitnessMax, speed=list, smin=None, smax=None, best=None)

seq = [lambda:random.uniform(-10,10),
	lambda:random.uniform(-10,10),
	lambda:random.uniform(-10,10),
	lambda:random.uniform(-10,10),
	lambda:random.uniform(-10,10),
	lambda:random.uniform(50,150),
	lambda:random.uniform(-10,10),
	lambda:random.uniform(1,5)
      ]

toolbox = base.Toolbox()
# toolbox.register("attr_bool", random.uniform, -100, 100)
# toolbox.register("individual", tools.initCycle, creator.Individual, seq, n=1)
toolbox.register("Particle", generate, size=8, pmin=-6, pmax=6, smin=-3, smax=3)
toolbox.register("population", tools.initRepeat, list, toolbox.Particle)

toolbox.register("evaluate", evalAgent)
toolbox.register("update", updateParticle, phi1=1.0, phi2=1.0)

# toolbox.register("mate", tools.cxOnePoint)
# toolbox.register("mutate", tools.mutGaussian, indpb=0.5, mu=0, sigma=3)
# toolbox.register("select", tools.selTournament, tournsize=3)

# tools.cxOnePoint(indpb)

# individual = toolbox.Particle()
# print(individual,individual.speed)

# population = toolbox.population(n=50)
# # print population
# try:
# 	NGEN=40
# 	# global
# 	for gen in range(NGEN):
# 	    q = PriorityQueue()
# 	    print("Beginning Generation:",gen)
# 	    offspring = algorithms.varAnd(population, toolbox, cxpb=0.1, mutpb=0.4)
# 	    fits = evalAgentsThreaded(offspring)

# 	    for fit, ind in zip(fits, offspring):
# 	        ind.fitness.values = [fit]
# 	        q.put((1/(fit+1),ind))
# 	    # for i in range(len(fits)):
# 	    # 	q.put(offspring[i], 1/(fits[i] +1))
# 	    top10 = []
# 	    for i in range(10):
# 	    	top10.append(q.get()[1])
# 	    # print(top10)
# 	    for newind in toolbox.select(offspring, k=len(population)-10):
# 	    	top10.append(newind)
# 	    population = top10
# 	    # print("pop:")
# 	    # print(population)
# 	top10 = tools.selBest(population, k=10)
# 	print("Top10 were:")
# 	print("goalForce separationForce enemySeparationForce alignmentForce cohesiveForce ")
# 	for top in top10:
# 		print(top)
# except KeyboardInterrupt:
# 	print("Top10 were:")
# 	print("goalForce separationForce enemySeparationForce alignmentForce cohesiveForce ")
# 	for top in top10:
# 		print(top)
# toolbox.register("evaluate", benchmarks.h1)





pop = toolbox.population(n=50)
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

logbook = tools.Logbook()
logbook.header = ["gen", "evals"] + stats.fields

GEN = 40
best = None

for g in range(GEN):
    # print(g)
    fits = evalAgentsThreaded(pop)
    # fits = []
    # for part in pop:
    # 	fits.append(toolbox.evaluate(part))
    for fit, part in zip(fits, pop):
        # part.fitness.values = toolbox.evaluate(part)
        # print(toolbox.evaluate(part))
        part.fitness.values = fit
        if not part.best or part.best.fitness < part.fitness:
            part.best = creator.Particle(part)
            part.best.fitness.values = part.fitness.values
        if not best or best.fitness < part.fitness:
            best = creator.Particle(part)
            best.fitness.values = part.fitness.values
    for part in pop:
        toolbox.update(part, best)

    # Gather all the fitnesses in one list and print the stats
    logbook.record(gen=g, evals=len(pop), **stats.compile(pop))
    print(logbook.stream)
print("\n")
print(pop,"\n", logbook,"\n", best)