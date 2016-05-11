from Starbot import Starbot
import time
# class EvoChamber():
# 	def __init__(self, numbots):
# 		self.numbots = numbots

# 	def runOnce(self):

b1 = Starbot()
b2 = Starbot()

b1.start()
print("b1 started")

b2.start()
print("b2 started")

while True:
	time.sleep(1)
	print(b2.getScore())