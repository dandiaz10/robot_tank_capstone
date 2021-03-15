 # File Name          : servoCamera.py
  # Description        : Movement of the camera on the servo-mount and video streaming  
  # Author:            : Group F
  # Date:              : 2019-05-28				 

#Import libraries 

import RPi.GPIO as gpio
from picamera import PiCamera
import sys
import termios
import select
import tty
import Lib
import RobotTank
import subprocess
import time

duttyA = 7.5 #tilt
duttyB = 6.2 #pan

Freq=50

pwmA = Lib.PWM(0)
pwmB = Lib.PWM(1)

pwmA.Duty(duttyA)
pwmB.Duty(duttyB)

pwmA.Start(Freq)
pwmB.Start(Freq)

Robot = RobotTank.RobotTank()

proc = subprocess.Popen('raspivid -t 0 -b 25000000 -fps 30 -w 800 -h 600 -fl -rot 180 -l -o tcp://0.0.0.0:8080', shell=True)



def getch(timeout=None):
    """Return a single char from console input.
    The optional timeout argument specifies a time-out as a floating point
    number in seconds. When the timeout argument is omitted or None (the
    default) the function blocks until a char has been read. If the timeout is
    exceeded before a char can be read, the function returns None. A time-out
    value of zero specifies a poll and never blocks.
    """
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)

        rlist, _, _ = select.select([fd], [], [], timeout)
        if fd in rlist:
            return sys.stdin.read(1)

        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

deltaTime=time.time()

try:		   # To handle the exceptions
    while True:
        direct=getch(0.1)		#getting the commands from the ASCI keyboard
        
        if (proc.poll()  != None):
            proc = subprocess.Popen('raspivid -t 0 -b 25000000 -fps 30 -w 800 -h 600 -fl -rot 180 -l -o tcp://0.0.0.0:8080', shell=True)
        
        if(direct == None):
            if (time.time() - deltaTime> .5):
                Robot.stop()
                continue
        else:
            deltaTime=time.time()
            
            

        #caterpillar control
        if direct=='w':		#getting the forward commands from the ASCI keyboard word 'w'
            Robot.forward()
        elif direct=='s':	#getting the backward commands from the ASCI keyboard word 's'
            Robot.backward()
        elif direct=='a':	#getting the left commands from the ASCI keyboard word 'a'
            Robot.left()
        elif direct=='d':	#getting the right commands from the ASCI keyboard word 'd'
            Robot.right()
        elif direct=='x':
            Robot.stop()


        #Camera control
        if direct=='i':
            duttyA=duttyA+0.1
        elif direct=='k':
            duttyA=duttyA- 0.1
        elif direct=='j':	
            duttyB=duttyB+0.1
        elif direct=='l':
            duttyB=duttyB- 0.1
        elif direct=='o':
            duttyA = 7.5 #tilt
            duttyB = 6.2 #pan
        elif direct=='q':
            # gpio.cleanup()
             break
        elif direct=='p':
            print("Duty A " + str(duttyA))    
            print("Duty B " + str(duttyB))    
        
        #define the PWM limits
        if(duttyA < 5):
            duttyA = 5
        
        if(duttyA > 12):
            duttyA = 12
            
        if(duttyB < 3):
            duttyB = 3
        
        if(duttyB > 11):
            duttyB = 11
            
            
        pwmA.Duty(duttyA)
        pwmB.Duty(duttyB)
        

            

except KeyboardInterrupt:		#if any other ASCI character press it interrupts the command
    gpio.cleanup()
    
    
print("Duty A " + str(duttyA))    
print("Duty B " + str(duttyB))    
pwmA.Stop()
pwmB.Stop()
Robot.ShutDown()
proc.terminate()
