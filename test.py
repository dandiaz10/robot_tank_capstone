import RobotTankTest 


R= RobotTankTest.RobotTankTest()

try:
	R.run()
except:
	print("Something went wrong")
	R.ShutDown()
finally:
	print("Nothing went wrong")	
	R.ShutDown()
