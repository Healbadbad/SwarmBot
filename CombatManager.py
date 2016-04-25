import cybw
from boid import LearningBoid
Broodwar = cybw.Broodwar

class CombatManager():
	''' A class to manage Allied and enemy units, and 
		provide Overarching combat goals
	'''
	def __init__(self):
		self.units = []
		self.buildings = []
		self.drones = []
		self.enemies = []
		self.enemyBuildings = []
		self.targetStrategy = self.enemyCenter
		self.target = []
		# temp = cybw.Unit().getT


	def takeUnit(self, unit):
		''' Receives a unit, and puts it into the correct group of unit/building
			and ally/enemy '''
		print(unit.getInitialType())
		if unit.getPlayer() == Broodwar.self():
			if unit.getType().isBuilding():
				self.buildings.append(unit)
			else: 
				if unit.getType().isWorker():
					self.drones.append(unit)
				else:	
					# 
					self.units.append(LearningBoid(unit))
		else:
			if unit.getType().isBuilding():
				self.enemyBuildings.append(unit)
			else: 
				self.enemies.append(unit)

	def removeUnit(self, unit):
		if unit.getPlayer() == Broodwar.self():
			if unit.getType().isBuilding():
				self.buildings.remove(unit)
			else: 
				if unit.getType().isWorker():
					self.drones.remove(unit)
				else:
					for boid in self.units:
						if boid.isUnit(unit):
							print("Commander Removed a unit")
							self.units.remove(boid)
		else:
			if unit.getType().isBuilding():
				self.enemyBuildings.append(unit)
			else: 
				self.enemies.remove(unit)
				print("Commander Removed an enemy unit provide reward?")

	def enemyCenter(self):
		''' a method to calculate the center of all enemies 
			acts as a basic form of attack move on a group'''
		center = [0,0]
		length = len(self.enemies)
		for enemy in self.enemies:
			center[0] = center[0] + enemy.getPosition().getX()/length
			center[1] = center[1] + enemy.getPosition().getY()/length

		return [cybw.Position(center[0], center[1])]

	def setAttackPos(self, posx, posy):
		''' Takes a positon and treats it like an attack move for all combat units '''
		result = cybw.Position(posx, posy)
		self.target = [result]

	def signalVictory(self):
		''' we won the match, take an action such as training'''
		pass

	def signalDefeat(self):
		''' we lost the match, take an action such as training'''
		pass

	def goalDiagnostics(self):
		statStr = "Commander Goal: " + str(self.targetStrategy())
		Broodwar.drawTextScreen(cybw.Position(40, 0), statStr)

	def boidDiagnostics(self):
		''' Draw objects to screen to help visualize what each boid is doing '''
		drawColor = cybw.Colors.Blue
		visionRange = 130
		for boid in self.units:
			# if boid.getTargetLocation().isPo
			Broodwar.drawCircleMap(boid.getPosition(), visionRange, drawColor)
			try:
				Broodwar.drawLineMap(boid.getPosition(), boid.getTargetLocation(), drawColor)
			except:
				Broodwar.drawLineMap(boid.getPosition(), boid.getTargetLocation().getPosition(), cybw.Colors.Red)


	def moveDiagnostics(self):
		''' Print information about each boid'''
		line = 2
		for unit in self.units:
			line += 1
			statStr = str(unit.getType()) + ": " + str(unit.getPosition()) + " Target: " + str(unit.getTargetLocation()) #getTargetLocation() 
			Broodwar.drawTextScreen(cybw.Position(5, 12*line), statStr)

	def update(self):
		''' run the logic for the list of units
			Give commands to units to engage path planning and flocking '''

		for boid in self.units:
			# TODO:  Add an algorithm to probabilistically give attack targets
			for target in self.targetStrategy():
				boid.setGeneralTarget(target)
			boid.update(self.units, self.enemies)

		self.goalDiagnostics()
		self.boidDiagnostics()
		self.moveDiagnostics()