 # File Name         : RunRaspberry.py
  # Description      : Control the tank movement and camera position
  # Author:            : Eduardo, Lean, Daniela
  # Date:               : 2021-04-06				 


#Import libraries 

import RPi.GPIO as gpio
from picamera import PiCamera
import sys
import termios
import select
import tty
import PWM
import RobotTank
import subprocess
import time
import json
import socket
import os
from ast import literal_eval
from math import sqrt


#do some cleanup to avoid errors
subprocess.call('pkill raspivid', shell=True)

# Create a server socket
serverSocket = socket.socket()
# Associate the server socket with the IP and Port
ip='0.0.0.0'
port=3050
serverSocket.bind((ip, port))

# Make the server listen for incoming connections
serverSocket.listen(1)


#define the PWM values for the center position
dutyTilt = 7.5 #tilt
dutyPan = 6.2 #pan

#camere servo frequency Hz
Freq=50

#JSON package length. It is a fixed value
packageLength = 91

#setup the PWM for the camera
pwmTilt = PWM.PWM(0)
pwmPan = PWM.PWM(1)

pwmTilt.Start(Freq)
pwmPan.Start(Freq)

pwmTilt.Duty(dutyTilt)
pwmPan.Duty(dutyPan)

Robot = RobotTank.RobotTank()

#start the raspivid to stream the video
proc = subprocess.Popen('raspivid -a 12 -t 0 -fl -w 800 -h 600 -rot 180 -ih -fps 15 -l -o tcp://0.0.0.0:5000', shell=True)

#enable the server to receive the joystick and keyboard commands
(clientConnection, clientAddress) = serverSocket.accept()



deltaTime=time.time()
try:		   # To handle the exceptions
    while True:
        
        #verify if the raspivid is running
        if (proc.poll()  != None):
            #The raspivid will close when the connection ends or it can stop due to any error. In those cases, start it again
            proc = subprocess.Popen('raspivid -a 12 -t 0 -fl -w 800 -h 600 -rot 180 -ih -fps 15 -l -o tcp://0.0.0.0:5000', shell=True)

        #receive the JSON data from the client
        clientConnection.settimeout(1.0)
        data = clientConnection.recv(packageLength)
        
        
        try:
            #verify if the package is not empty
            if(data!=b''):
                #retreive the information
                msg=literal_eval(data.decode('utf8'))
                #the json python function does not recognize the + simbol, the I need to remove it here
                msg=msg.replace('+','')
                #parser the JSON package
                jmsg = json.loads(msg)
                
            else:
                #if the package is empty, something went wrong 
                Robot.stop()
                #get the next package
                continue
        except:
                #the package has an error, thow it away
                
                print("JSON package error")
                print(data)
                #resync the package
                while  clientConnection.recv(1) != b'}':
                    pass
                #thow away the last character
                clientConnection.recv(1)
                continue
        
        #get the pressed key
        direct = jmsg['key']
        
        #exit the program        
        if  direct=='q':
             break
    
        #Control the caterpillar using the joystick
        move = -jmsg['LeftY']
        turn = jmsg['LeftX']               
        Robot.DutyV2((move+turn)*100 , (move - turn)*100)
        
           
        #control the camera using the joystick
        dutyPan=dutyPan  -  jmsg['RightX']
        dutyTilt=dutyTilt + jmsg['RightY'] 
        
        #---------------------------------------------------------------------------------------------------------------------------------
         #Control the caterpillar using the keyboard             
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


        #Camera control using the keyboard   
        if direct=='i':
            dutyTilt=dutyTilt+0.1
        elif direct=='k':
            dutyTilt=dutyTilt- 0.1
        elif direct=='j':	
            dutyPan=dutyPan+0.1
        elif direct=='l':
            dutyPan=dutyPan- 0.1
        elif direct=='o': #center position
            dutyTilt = 7.5 #tilt
            dutyPan = 6.2 #pan
        elif direct=='p':#print the actual pan and tilt values
            print("Duty A " + str(dutyTilt))    
            print("Duty B " + str(dutyPan))    
        
        #define the camera servo limits. This is import because if the servor goes beyond its limits, it can get stucked or make a 180 degree rotation.
        if(dutyTilt < 5):
            dutyTilt = 5
        
        if(dutyTilt > 12):
            dutyTilt = 12
            
        if(dutyPan < 3):
            dutyPan = 3
        
        if(dutyPan > 11):
            dutyPan = 11
            
        #update the camera position    
        pwmTilt.Duty(dutyTilt)
        pwmPan.Duty(dutyPan)
        


except KeyboardInterrupt:
    pass
    
serverSocket.close()    
pwmTilt.Stop()
pwmPan.Stop()
Robot.ShutDown()
proc.terminate()
#os.system('kill -9 %s'%proc.pid)
while (proc.poll()  != None):
    time.sleep(.5)
    proc.kill()
    
#Exiting the program
sys.exit(0)

