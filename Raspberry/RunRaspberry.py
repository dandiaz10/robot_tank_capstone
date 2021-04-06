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
import json
import socket
from ast import literal_eval
from math import sqrt


#import pydevd
#pydevd.settrace("192.168.0.163", port=5678,suspend=True)


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


#do some cleanup to avoid errors
subprocess.call('pkill raspivid', shell=True)

# Create a server socket
serverSocket = socket.socket()
# Associate the server socket with the IP and Port
ip='0.0.0.0'
port=3050
serverSocket.bind((ip, port))

# Make the server listen for incoming connections
serverSocket.listen()


dutyTilt = 7.5 #tilt
dutyPan = 6.2 #pan

#camere servo frequency Hz
Freq=50

#setup the PWM for the camera
pwmTilt = Lib.PWM(0)
pwmPan = Lib.PWM(1)

pwmTilt.Start(Freq)
pwmPan.Start(Freq)

pwmTilt.Duty(dutyTilt)
pwmPan.Duty(dutyPan)

Robot = RobotTank.RobotTank()
proc = subprocess.Popen('raspivid -a 12 -t 0 -fl -w 800 -h 600 -rot 180 -ih -fps 30 -l -o tcp://0.0.0.0:5000', shell=True)
#proc = subprocess.Popen('raspivid -t 0 -stm -b 25000000 -fps 30 -w 800 -h 600 -fl -rot 180 -l -o tcp://0.0.0.0:5000', shell=True)

(clientConnection, clientAddress) = serverSocket.accept()



deltaTime=time.time()
try:		   # To handle the exceptions
    while True:
        
        if (proc.poll()  != None):
            proc = subprocess.Popen('raspivid -a 12 -t 0 -fl -w 800 -h 600 -rot 180 -ih -fps 30 -l -o tcp://0.0.0.0:5000', shell=True)

        #receive the data from the client
        data = clientConnection.recv(91)
        
        #verify if the package is not empty
        if(data!=b''):
            #retreive the information
            msg=literal_eval(data.decode('utf8'))
            msg=msg.replace('+','')
            jmsg = json.loads(msg)
        else:
            #if the package is empty, get the next package
            continue
        
        #get the pressed key
        direct = jmsg['key']
        
        #exit the program        
        if  direct=='q':
             break
    
        #Control the caterpillar
        move = -jmsg['LeftY']
        turn = jmsg['LeftX']               
        Robot.DutyV2((move+turn)*100 , (move - turn)*100)
        
           
        #control the camera
        dutyPan=dutyPan  -  jmsg['RightX']
        dutyTilt=dutyTilt + jmsg['RightY'] 
        
        #---------------------------------------------------------------------------------------------------------------------------------
            
        if direct=='s':	#getting the backward commands from the ASCI keyboard word 's'
            Robot.backward()
        if direct=='w':	#getting the forward commands from the ASCI keyboard word 'w'
            Robot.forward()
        elif direct=='a':	#getting the counter clockwise turn commands from the ASCI keyboard word 'a'
            Robot.CCW()
        elif direct=='d':	#getting the clockwise trun commands from the ASCI keyboard word 'd'
            Robot.CW()
        elif direct=='x':
            Robot.stop()


        #Camera control
        if direct=='i':
            dutyTilt=dutyTilt+0.1
        elif direct=='k':
            dutyTilt=dutyTilt- 0.1
        elif direct=='j':	
            dutyPan=dutyPan+0.1
        elif direct=='l':
            dutyPan=dutyPan- 0.1
        elif direct=='o':
            dutyTilt = 7.5 #tilt
            dutyPan = 6.2 #pan
        elif direct=='p':
            print("Duty A " + str(dutyTilt))    
            print("Duty B " + str(dutyPan))    
        
        #define the PWM limits
        if(dutyTilt < 5):
            dutyTilt = 5
        
        if(dutyTilt > 12):
            dutyTilt = 12
            
        if(dutyPan < 3):
            dutyPan = 3
        
        if(dutyPan > 11):
            dutyPan = 11
            
            
        pwmTilt.Duty(dutyTilt)
        pwmPan.Duty(dutyPan)
        

            

except KeyboardInterrupt:		#if any other ASCI character press it interrupts the command
    pass
    
    
print("Duty A " + str(dutyTilt))    
print("Duty B " + str(dutyPan))    
pwmTilt.Stop()
pwmPan.Stop()
proc.terminate()

    
Robot.ShutDown()

