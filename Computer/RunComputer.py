import os
import sys
import subprocess
import pygame
import socket
import json
import time
import multiprocessing


# Enable in Windows to use directx renderer instead of windib
#os.environ["SDL_VIDEODRIVER"] = "directx"

# host = '192.168.16.7'
#host = '192.168.43.161'
try: 
    host = '192.168.0.201'
    port = 3050
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
except:
    print("Fail to connect, verify if the server are running and the IP address")
    exit()

#initialize the python game
pygame.init()
#verify if the Joystick is connected
try:
    joy = pygame.joystick.Joystick(0)
    joy.init()
    joystickFlag =1
except:
    joystickFlag =0

#open the screen
screen = pygame.display.set_mode((800,600),pygame.RESIZABLE)
# pygame.display.get_wm_info()

print ("Using %s renderer" % pygame.display.get_driver())

#Pass pygame window id to mplayer player, so it can render its contents in python Game
win_id = pygame.display.get_wm_info()['window']

#player.set_xwindow(win_id)
print(win_id)

#to reduce the lantecy I am using fps here 2x the fps on the raspberry. I dont know why, but it only works fine when I did that
p=subprocess.Popen("python3 cam.py - | mplayer -nocache -fps 60 -nosound -vc ffh264 -noidx -mc 0 -wid "+ str(win_id) +" -", shell=True,executable='/bin/bash')

#using a character to infor tha none of key was pressed
key=64 # ASCII code for the @
try:

    while True:
        
        if(key == 120): # if the last character sent is x to stop the tank, send the @ to allow the use of joysitck
            key=64  # ASCII code for the @
        
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.KEYDOWN:
                key = event.key
            if event.type == pygame.KEYUP:
                key = 120  # ASCII code for the @. the character s to stop the tank
            if event.type == pygame.MOUSEBUTTONDOWN:
                print ("we got a mouse button down!")
        
        #convert the key to a valid character
        if (key <64):
            key=64 # Avoiding sending special characters. It can break the JSON package
        
        #remove invalid characters
        if key >= 122:
            key = 64
        
        #verify if the joysitck is connected 
        if (joystickFlag ==1):        
            #we have a joystick connected
            #It is very import that the package has always the same size. Therefore, it was included the axis + signal to guarantee the same size when the negative value is sent
            
            data = bytearray(json.dumps("{\"LeftX\":" + "{:+1.4f}".format(joy.get_axis(0)) + ",\"LeftY\":" + "{:+1.4f}".format(joy.get_axis(1)) +  ",\"RightX\":" + "{:+1.4f}".format(joy.get_axis(3))+  ",\"RightY\":" + "{:+1.4f}".format(joy.get_axis(4))+ ",\"key\":\""+ chr(key)+ "\"}"),'utf-8')
        else:
            #we dont have a joystick. In this case, we just send zeros
            data = bytearray(json.dumps("{\"LeftX\":" + "+0.0000" + ",\"LeftY\":" + "+0.0000" +  ",\"RightX\":" + "+0.0000"+  ",\"RightY\":" + "+0.0000"+ ",\"key\":\""+ chr(key)+ "\"}"),'utf-8')
        
        #send the data to the tank 
        sock.sendall(data)
        
        #give a small time gap to avoid overload the tank with more command that it can process
        time.sleep(.1)
        
        if (key == 113): #SCII code for the q
            break
        
except KeyboardInterrupt:
    pass
      
socket.close()
#finish the mplayer
proc.terminate()
time.sleep(.5)
while (proc.poll()  != None):
    proc.kill()
    time.sleep(.5)

#Exiting the program
sys.exit(0)
