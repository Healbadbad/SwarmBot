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
		# print(theOut)

	toSend = '' #+ str(index) + ' '
	for item in individual:
		toSend = toSend + str(item) + ' '
	toSend = toSend[:-1] + '\n'
	# a = array('B', toSend)
	a = toSend.encode('ascii')
	# print("Yay Connected")
	print(a)
	theOut = str(process.communicate(a)[0].rstrip()) #b"1 2 3 4 5\n"
	# print(theOut)
	# score = int(theOut.split("\\")[2].split(" ")[1])
	# index = int(theOut.split("\\")[2].split(" ")[0][1:])#
	score = int(theOut.split("\\")[2][1:])
	print(score)
	return score

def evalAgentsThreaded(offspring):
	fits = []
	pool = ThreadPool(processes=8)
	# for k in range(len(offspring)):
		# print(offspring[k])
		# async_result = pool.apply_async(toolbox.evaluate, (offspring[k],k))
	rets = pool.map(toolbox.evaluate, offspring)
	return rets
	# for k in range(len(offspring)):
	# 	index, return_val = async_result.get()
	# 	print(index, return_val)


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

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
toolbox.register("attr_bool", random.uniform, -100, 100)
toolbox.register("individual", tools.initCycle, creator.Individual, seq, n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evalAgent)
toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mutate", tools.mutGaussian, indpb=0.5, mu=0, sigma=3)
toolbox.register("select", tools.selTournament, tournsize=3)

# tools.cxOnePoint(indpb)

population = toolbox.population(n=50)
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

logbook = tools.Logbook()
logbook.header = ["gen", "evals"] + stats.fields

# print population
try:
	NGEN=40
	# global
	for gen in range(NGEN):
	    q = PriorityQueue()
	    print("Beginning Generation:",gen)
	    offspring = algorithms.varAnd(population, toolbox, cxpb=0.1, mutpb=0.4)
	    fits = evalAgentsThreaded(offspring)
	    for fit, ind in zip(fits, offspring):
	        ind.fitness.values = [fit]
	        q.put((1/(fit+1),ind))
	    # for i in range(len(fits)):
	    # 	q.put(offspring[i], 1/(fits[i] +1))
	    top10 = []
	    for i in range(10):
	    	# print("here?")
	    	top10.append(q.get()[1])
	    print(top10)
	    logbook.record(gen=gen, evals=len(offspring), **stats.compile(offspring))

	    print(logbook.stream)
	    for newind in toolbox.select(offspring, k=len(population)-10):
	    	top10.append(newind)
	    population = top10

	    # print("pop:")
	    # print(population)
	top10 = tools.selBest(population, k=10)
	print("Top10 were:")
	print("goalForce separationForce enemySeparationForce alignmentForce cohesiveForce ")
	for top in top10:
		print(top)
except:
	pass
print("\n")
print(offspring,"\n", logbook)