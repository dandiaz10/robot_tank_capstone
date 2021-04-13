import RPi.GPIO as gpio
import time
import sys
import signal
import Lib

class RobotTankTest(object):
    def __init__(self):

        signal.signal(signal.SIGINT, self.cleanup)
        #turn off the gpio warning
        #gpio.setwarnings(False) 
        #force a cleanup to guaratee the correct startup
        gpio.cleanup()

        # L298 Direction Pins
        self.GPIO_PIN_RIGHT_SW_1 = 18     # IN4
        self.GPIO_PIN_RIGHT_SW_2 = 16     # IN3
        self.GPIO_PIN_LEFT_SW_1 = 13       # IN2
        self.GPIO_PIN_LEFT_SW_2 = 11       # IN1


        #enable pins for L298N
        self.GPIO_PIN_ENA = 15 # left caterpillar
        self.GPIO_PIN_ENB = 22 #right caterpillar
        

        self.gpioinit()
        
        print("Tank Initialized")
        
    def gpioinit(self):
        print("gpio.BOARD " + str(gpio.BOARD))
        print("gpio.OUT " + str(gpio.OUT))
        gpio.setmode(gpio.BOARD)
        
        #setup the PWM pins
        gpio.setup(self.GPIO_PIN_ENA,gpio.OUT)          #EN1
        gpio.setup(self.GPIO_PIN_ENB,gpio.OUT)          #EN2
        
        
        self.pwmLeft = gpio.PWM(self.GPIO_PIN_ENA, 100)   # Initialize PWM on pwmPin 100Hz frequency
        self.pwmRight = gpio.PWM(self.GPIO_PIN_ENB, 100)   # Initialize PWM on pwmPin 100Hz 
        self.pwmLeft.start(80) #left thread
        self.pwmRight.start(100) #right thread
        
        #setting the diretion pins
        gpio.setup(self.GPIO_PIN_RIGHT_SW_1, gpio.OUT)
        gpio.setup(self.GPIO_PIN_RIGHT_SW_2, gpio.OUT)
        gpio.setup(self.GPIO_PIN_LEFT_SW_1, gpio.OUT)
        gpio.setup(self.GPIO_PIN_LEFT_SW_2, gpio.OUT)
        
        #set the initial values
        gpio.output(self.GPIO_PIN_RIGHT_SW_1, 0)
        gpio.output(self.GPIO_PIN_RIGHT_SW_2, 0)
        gpio.output(self.GPIO_PIN_LEFT_SW_1, 0)
        gpio.output(self.GPIO_PIN_LEFT_SW_2, 0)
        
    def ShutDown(self):
        gpio.output(self.GPIO_PIN_ENA, 0)
        gpio.output(self.GPIO_PIN_ENB, 0)
        gpio.output(self.GPIO_PIN_RIGHT_SW_1, 0)
        gpio.output(self.GPIO_PIN_RIGHT_SW_2, 0)
        gpio.output(self.GPIO_PIN_LEFT_SW_1, 0)
        gpio.output(self.GPIO_PIN_LEFT_SW_2, 0)
        gpio.cleanup()
        self.done = True
        
    def cleanup(self, signum, frame):
        sys.stdout.write("Caught signal %s. Shutting down.\n" % (str(signum)))
        self.ShutDown()

        
    def run(self):
        
        #duration in seconds
        duration = .5
        
        #left caterpillar thread foward
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,1)
        time.sleep(duration);
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,0)
        
        #left caterpillar thread reverse
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,1)
        time.sleep(duration);
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,0)
        
        #righ caterpillar thread foward
        gpio.output(self.GPIO_PIN_LEFT_SW_1,1 )
        time.sleep(duration);
        gpio.output(self.GPIO_PIN_LEFT_SW_1,0 )
        
        #right caterpillar thread foward
        gpio.output(self.GPIO_PIN_LEFT_SW_2,1 )
        time.sleep(duration);
        gpio.output(self.GPIO_PIN_LEFT_SW_2,0 )
        
        
        #caterpillar thread foward
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,1)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,1 )
        time.sleep(duration*2);
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,0)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,0 )
        
        #caterpillar thread re
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,1)
        gpio.output(self.GPIO_PIN_LEFT_SW_2,1 )
        time.sleep(duration*2);
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,0)
        gpio.output(self.GPIO_PIN_LEFT_SW_2,0 )
        
            
    def CameraTest(self):
    
       #center position
        duttyA = 7.5 #tilt
        duttyB = 6.2 #pan

        Freq=50

        pwmLeft = Lib.PWM(0)
        pwmRight = Lib.PWM(1)

        pwmLeft.Start(Freq)
        pwmRight.Start(Freq)
        
        pwmLeft.Duty(duttyA)
        pwmRight.Duty(duttyB)
        
        
        #tilt test
        for num in range(75,110):
            pwmLeft.Duty(num/10)
            time.sleep(.05)
            
        for num in range(110,50,-1):
            pwmLeft.Duty(num/10)
            time.sleep(.05)
            
        for num in range(50,75):
            pwmLeft.Duty(num/10)
            time.sleep(.05)
            
            
        #pan test
        for num in range(62,110):
            pwmRight.Duty(num/10)
            time.sleep(.05)
            
        for num in range(110,20,-1):
            pwmRight.Duty(num/10)
            time.sleep(.05)
            
        for num in range(20,62):
            pwmRight.Duty(num/10)
            time.sleep(.05)
        
        pwmLeft.Stop()
        pwmRight.Stop()

