import time
import sys
print('QQQ')
blah = input()
# blah = blah[:-2]
nums = blah.split(" ")
tot = 0
for num in nums:
	tot+= int(num)
print("received blah!: " + str(tot))
sys.stdout.flush()
time.sleep(0.1)