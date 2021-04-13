import RobotTankTest 


Robot= RobotTankTest.RobotTankTest()

try:
	Robot.run()
	Robot.CameraTest()
except:
	print("Something went wrong")
	Robot.ShutDown()
finally:
	print("Nothing went wrong")	
	Robot.ShutDown()
