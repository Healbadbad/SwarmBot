import cybw
import time
from math import cos, sin

client = cybw.BWAPIClient
Broodwar = cybw.Broodwar



# Input Data:
# Self:
# 	Position?
# 	Health
# 	Armor
# 	Damage
# 	Cost in resources
# 	Number of attackers*
# 	Flying
# 	Unit Type

# Nearby Enemies:
# 	Distance
# 	Health
# 	Armor
# Damage
# 	Cost in resources
# 	Number of attackers*
# 	Unit Type

# Nearby Allies:
# 	Distance
# 	Health
# 	Armor
# Damage
# 	Cost in resources
# 	Number of attackers*
# 	Unit Type

# Output Data - Flocking Parameters::
# Vision Range
# Separation Force
# Alignment Force
# Cohesive Force


class LearningBoid():
	def __init__(self, actualUnit):
		self.unit = actualUnit
		self.generalTarget = '' 
		self.attackTarget = []
		self.moveDirection = [0,0]
		self.flockingAlgorithm = self.flockingV1
		self.targetLocation = cybw.Position(1000,200)
		self.decideAttackTarget = self.attackLowEnemy
		self.visionRange = 130
		self.attackState = False
		self.attackCoooldown = self.getType().groundWeapon().damageCooldown() + 3
		self.attackFrames = 0
		self.maxAttackers = 2

	def getPosition(self):
		return self.unit.getPosition()

	def getAngle(self):
		return self.unit.getAngle()

	def getUnit(self):
		return self.unit

	def getType(self):
		return self.unit.getType()

	def getMoveDirection(self):
		return self.moveDirection

	def getHealth(self):
		# Scale to percentage instead of raw value?
		return self.unit.getHitPoints()

	def getArmor(self):
		# TODO: Include armor from upgrades
		return self.unit.getType().armor()

	def getSpeed(self):
		return self.unit.getType().topSpeed()

	def getDamage(self):
		groundDmg = self.getType().groundWeapon().damageAmount()
		airDmg = self.getType().airWeapon().damageAmount()
		return groundDmg

	def getDestroyScore(self):
		return self.unit.getType().destroyScore()

	def isFlying(self):
		return self.getType().isFlyer() +1 -1

	def getHitPoints(self):
		return self.unit.getHitPoints()


	def getDefenseType(self):
		''' returns an array for isorganic, isrobotic, ismechanical'''
		return self.getType().isOrganic() + 1 - 1, self.getType().isRobotic() + 1 - 1, self.getType().isMechanical() + 1 - 1

	def getFeatures(self):
		''' Return a vector of features for this Unit, for input to the Network '''
		# Figure out how to include Damage type, size and isOrganic/isRobotic/isMechanical in the network
		features = []

		pos = self.getPosition()
		posx = pos.getX()
		posy = pos.getY()
		health = self.getHealth()
		armor = self.getArmor()
		speed = self.getSpeed()
		damage = self.getDamage()
		value = self.getDestroyScore()
		flying = self.isFlying()
		isorganic, isrobotic, ismechanical = self.getDefenseType()
		features = [posx,
					posy,
					health,
					armor,
					speed,
					damage,
					value,
					flying,
					isorganic,
					isrobotic,
					ismechanical]
		return features

	def calculateFlockingParameters(self):
		
		pass

	def giveGeneticParameters(self, params):
		self.params = params
		self.attackCoooldown = self.getType().groundWeapon().damageCooldown() + int(self.params[6])
		self.maxAttackers = params[7]


	def getGeneticParameters(self):
		# self.visionRange

		return self.params[5], self.params[0], self.params[1], self.params[2], self.params[3], self.params[4]

	def getStaticFlockingParameters(self):
		# Vision Range
		# Separation Force
		# Alignment Force
		# Cohesive Force
		visionRange = self.visionRange # Good?
		goalForce = 1/20
		separationForce = 1/500
		enemySeparationForce = 1
		alignmentForce = 1/20
		cohesiveForce = 1/20
		return visionRange, goalForce, separationForce, enemySeparationForce, alignmentForce, cohesiveForce

	def isUnit(self, toCheck):
		if toCheck == self.unit:
			return True
		return False

	def setGeneralTarget(self, target):
		''' A target received from the CommandManager 
			Can be a position or enemy unit
		'''
		self.generalTarget = target

	def applyGoalForce(self, strength):
		try:
			dx = self.generalTarget.getX() - self.unit.getPosition().getX();
			dy = self.generalTarget.getY() - self.unit.getPosition().getY();
		except:
			dx = self.generalTarget.getPosition().getX() - self.unit.getPosition().getX();
			dy = self.generalTarget.getPosition().getY() - self.unit.getPosition().getY();

		self.moveDirection[0] += dx * strength;
		self.moveDirection[1] += dy * strength;

	def applyCohesion(self, allies, strength):
		dx = 0
		dy = 0
		if len(allies) == 1:
			return
		for ally in allies:
			if not ally.isUnit(self.unit):
				dx += ally.getPosition().getX();
				dy += ally.getPosition().getY();
		dx = dx / (len(allies) - 1);
		dy = dy / (len(allies) - 1);
		self.moveDirection[0] += (dx - self.unit.getPosition().getX()) * strength;
		self.moveDirection[1] += (dy - self.unit.getPosition().getY()) * strength;

	def applySeparation(self, allies, strength):
		dx = 0
		dy = 0
		if len(allies) == 1:
			return
		for ally in allies:
			if not ally.isUnit(self.unit):
				# print('there is another unit')
				dx -= ally.getPosition().getX() - self.unit.getPosition().getX();
				dy -= ally.getPosition().getY() - self.unit.getPosition().getY();
		# dx = dx / (len(allies) - 1);
		# dy = dy / (len(allies) - 1);
		# print(dx,dy)
		self.moveDirection[0] += dx * strength;
		self.moveDirection[1] += dy * strength;

	def applyEnemySeparation(self, enemies, strength):
		dx = 0
		dy = 0
		if len(enemies) == 1:
			return
		for enemy in enemies:
			if not enemy.isUnit(self.unit):
				# print('there is another unit')
				dx -= enemy.getPosition().getX() - self.unit.getPosition().getX();
				dy -= enemy.getPosition().getY() - self.unit.getPosition().getY();
		# dx = dx / (len(allies) - 1);
		# dy = dy / (len(allies) - 1);
		# print(dx,dy)
		self.moveDirection[0] += dx * strength;
		self.moveDirection[1] += dy * strength;

	def applyalignment(self, allies, strength):
		dx = 0
		dy = 0
		if len(allies) == 1:
			return
		for ally in allies:
			if not ally.isUnit(self.unit):
				dx += cos(ally.getAngle());
				dy += sin(ally.getAngle());
		dx = dx / (len(allies) - 1);
		dy = dy / (len(allies) - 1);
		self.moveDirection[0] += (dx - cos(self.unit.getAngle())) * strength;
		self.moveDirection[1] += (dy - sin(self.unit.getAngle())) * strength;

	def flockingV1(self, allies, enemies, values):
		visionRange, goalForce, separationForce, enemySeparationForce, alignmentForce, cohesiveForce = values
		self.applySeparation(allies, separationForce)
		self.applyGoalForce(goalForce)
		self.applyEnemySeparation(allies, enemySeparationForce)
		self.applyalignment(allies, alignmentForce)
		self.applyCohesion(allies, cohesiveForce)
		

	def getTargetLocation(self):
		return self.targetLocation

	def attackClosestEnemy(self, enemies):
		if len(enemies) < 0:
			return 'This is bad'

		closest = enemies[0]
		mindst = 99999999
		for enemy in enemies:
			dst = self.unit.getDistance(enemy.getUnit())
			if dst < mindst:
				mindst = dst
				closest = enemy

		return closest

	def attackLowEnemy(self, enemies):
		if len(enemies) < 0:
			return 'This is bad'

		best = enemies[0]
		maxScore = 0
		for enemy in enemies:
			if enemy.getAttackers() < int(self.maxAttackers):
				score = 1/((enemy.getHitPoints()/enemy.getUnit().getType().maxHitPoints()) * ((self.unit.getDistance(enemy.getUnit()) +1)/self.visionRange))
				if score > maxScore:
					maxScore = score
					best = enemy

		return best


	def update(self, allies, enemies):
		''' Update loop for individual units and implementation of our hybrid algorithm
			Will find a path to its general target, then use flocking behavior for local control
			Flocking parameters will be tuned using a learning algorithm
		'''

		#for now, values are harcoded just to make sure it works
		values = self.getGeneticParameters()
		visionRange = values[0]
		self.moveDirection = [0,0]

		# Determine If using Flocking or A*
		flocking = False
		nearbyEnemies = []
		nearbyAllies = []
		
		for enemy in enemies:
			if self.unit.getDistance(enemy.getUnit()) < visionRange:
				flocking = True
				nearbyEnemies.append(enemy)
		
		for ally in allies:
			if self.unit.getDistance(ally.getUnit()) < visionRange:
				nearbyAllies.append(ally)

		if self.attackFrames > 0:
			self.attackFrames += -1
		if flocking:
			self.flockingAlgorithm(nearbyAllies, nearbyEnemies, values)
			# TODO: Decide Movement vs Attack
			# print(self.unit.isAttackFrame())
			# print(self.getType().groundWeapon().damageCooldown())
			# print(self.unit.getGroundWeaponCooldown())
			# if self.unit.getGroundWeaponCooldown() == 0:
			# print(self.attackFrames)
			# if self.unit.getGroundWeaponCooldown() == 0:
			# print(self.getType().groundWeapon().maxRange())
			# print(self.attackFrames)
			if self.attackFrames == 0:
				target = self.decideAttackTarget(nearbyEnemies)
				# print(self.unit.getDistance(target.getUnit()))
				# if self.unit.getDistance(enemy.getUnit()) < self.getType().groundWeapon().maxRange() + 30:
				self.unit.rightClick(target.getUnit())
				target.addAttacker()
				self.targetLocation = target
				self.attackFrames = self.attackCoooldown
				return
			
			elif self.attackFrames < self.attackCoooldown/2:
				pos = self.unit.getPosition()
				move = cybw.Position(pos.getX() + self.moveDirection[0], pos.getY() + self.moveDirection[1])
				self.unit.rightClick(move)
				self.targetLocation = move #[pos.getX() + self.moveDirection[0], pos.getY() + self.moveDirection[1]]


		else: # Run A*
			if self.generalTarget != cybw.Position(0,0):
				self.unit.rightClick(self.generalTarget)


class EnemyProxy(LearningBoid):

	def __init__(self, unit):
		super(EnemyProxy, self).__init__(unit)
		self.attackers = 0

	def addAttacker(self):
		self.attackers +=1

	def resetAttackers(self):
		self.attackers = 0

	def getAttackers(self):
		return self.attackers