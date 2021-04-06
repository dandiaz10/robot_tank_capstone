import RPi.GPIO as gpio
import time
import sys
import signal

class RobotTank(object):
    def __init__(self):

        signal.signal(signal.SIGINT, self.cleanup)
        #turn off the gpio warning
        gpio.setwarnings(False) 
        #force a cleanup to guaratee the correct startup
        #gpio.cleanup()

        # L298 Direction Pins. Left and Right are the tank caterpillars
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


        #using soft PWM for the motors
        self.pwmLeft = gpio.PWM(self.GPIO_PIN_ENA, 100)   # Initialize PWM on pwmPin 100Hz frequency
        self.pwmRight = gpio.PWM(self.GPIO_PIN_ENB, 100)   # Initialize PWM on pwmPin 100Hz 
        self.pwmLeft.start(0) #left thread
        self.pwmRight.start(0) #right thread


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
        
    def Duty(self,dutypwmLeft,dutypwmRight):
        
        if (dutypwmLeft < 0):
            dutypwmLeft = 0;
            
        if (dutypwmRight < 0):
            dutypwmRight = 0;
            
        if (dutypwmLeft > 100):
            dutypwmLeft = 100;
            
        if (dutypwmRight > 100):
            dutypwmRight = 100;
    
        self.pwmLeft.ChangeDutyCycle(dutypwmLeft)
        self.pwmRight.ChangeDutyCycle(dutypwmRight)
        
    def DutyV2(self,dutypwmLeft,dutypwmRight):
        
        minimalPWM=40
        
        #Assesing the values to avoid values larger than premited
        if (dutypwmLeft < -100):
            dutypwmLeft = -100;
            
        if (dutypwmRight < -100):
            dutypwmRight = -100;
            
        if (dutypwmLeft > 100):
            dutypwmLeft = 100;
            
        if (dutypwmRight > 100):
            dutypwmRight = 100;
            
        #Set the caterpillar direction    
        
        #left cartepillar control
        if ( dutypwmLeft > minimalPWM ): #move forward
            gpio.output(self.GPIO_PIN_LEFT_SW_1,1 )
            gpio.output(self.GPIO_PIN_LEFT_SW_2,0 )
            
        elif ( dutypwmLeft < -minimalPWM ):#move barckward
            gpio.output(self.GPIO_PIN_LEFT_SW_1,0 )
            gpio.output(self.GPIO_PIN_LEFT_SW_2,1 )
            
        else:   #do nothing
            gpio.output(self.GPIO_PIN_LEFT_SW_1,0 )
            gpio.output(self.GPIO_PIN_LEFT_SW_2,0 )
                
                
        #right cartepillar control
        if(dutypwmRight > minimalPWM):    #move forward
            gpio.output(self.GPIO_PIN_RIGHT_SW_1,1)
            gpio.output(self.GPIO_PIN_RIGHT_SW_2,0)
            
        elif(dutypwmRight < -minimalPWM):   #move barckward
            gpio.output(self.GPIO_PIN_RIGHT_SW_1,0)
            gpio.output(self.GPIO_PIN_RIGHT_SW_2,1)
            
        else: #do nothing
            gpio.output(self.GPIO_PIN_RIGHT_SW_1,0)
            gpio.output(self.GPIO_PIN_RIGHT_SW_2,0)
            
            
        #Remove the direction information from the PWM signal
        if (dutypwmLeft < 0):
            dutypwmLeft = -dutypwmLeft;
            
        if (dutypwmRight < 0):
            dutypwmRight = -dutypwmRight;
            
    
        #setup the PWM duty cycle . Values between  0 and 100
        self.pwmLeft.ChangeDutyCycle(dutypwmLeft)
        self.pwmRight.ChangeDutyCycle(dutypwmRight)

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

    # FUNCTION      :	 Diagnose
    # DESCRIPTION   :	Basic Diagnose function to verify if the tank is propely working 
    # PARAMETERS    :	Nothing
    # RETURNS       :	Nothing	

    def Diagnose(self):

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

        #move the caterpillar thread foward
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,1)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,1 )
        time.sleep(duration*10);
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,0)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,0 )

        #move the caterpillar thread backward
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,1)
        gpio.output(self.GPIO_PIN_LEFT_SW_2,1 )
        time.sleep(duration*10);
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,0)
        gpio.output(self.GPIO_PIN_LEFT_SW_2,0 )
        

    # FUNCTION      :	 Stop the tank
    # DESCRIPTION   :	Stop the tank and turn of the PWM to save battery
    # PARAMETERS    :	Nothing
    # RETURNS       :	Nothing		

    def stop(self):
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,0)
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,0)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,0 )
        gpio.output(self.GPIO_PIN_LEFT_SW_2,0 )
        #print("stop")
        self.Duty(0,0)

    # FUNCTION      :	forward
    # DESCRIPTION   :	The forward servo motors start rotating
    # PARAMETERS    :	Nothing
    # RETURNS       :	Nothing		

    def forward(self):
        #caterpillar thread foward
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,1)
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,0)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,1 )
        gpio.output(self.GPIO_PIN_LEFT_SW_2,0 )
        #print("forward")
        self.Duty(100,100)


    # FUNCTION      :	backward
    # DESCRIPTION   :	The backward servo motors start rotating
    # PARAMETERS    :	Nothing
    # RETURNS       :	Nothing		

    def backward(self):
        #caterpillar thread foward
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,0)
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,1)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,0 )
        gpio.output(self.GPIO_PIN_LEFT_SW_2,1 )
        #print("backward")
        self.Duty(100,100)


    # FUNCTION      :	  Counter ClockWise turn
    # DESCRIPTION   :	Make the tank turns into the Counter ClockWise direction
    # PARAMETERS    :	Nothing
    # RETURNS       :	Nothing		

    def CCW(self):
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,1)
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,0)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,0 )
        gpio.output(self.GPIO_PIN_LEFT_SW_2,1 )
        #print("right")
        self.Duty(100,100)


    # FUNCTION      :	  ClockWise turn
    # DESCRIPTION   :	Make the tank turns into the ClockWise direction
    # PARAMETERS    :	Nothing
    # RETURNS       :	Nothing	

    def CW(self):
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,0)
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,1)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,1 )
        gpio.output(self.GPIO_PIN_LEFT_SW_2,0 )
        #print("left")
        self.Duty(100,100)


