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

        # L298 Direction Pins
        self.GPIO_PIN_RIGHT_SW_1 = 13     # IN2
        self.GPIO_PIN_RIGHT_SW_2 = 11     # IN1
        self.GPIO_PIN_LEFT_SW_1 = 18       # IN4
        self.GPIO_PIN_LEFT_SW_2 = 16       # IN3

        #enable pins for L298N
        self.GPIO_PIN_ENA = 15
        self.GPIO_PIN_ENB = 22


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
        self.pwmA = gpio.PWM(self.GPIO_PIN_ENA, 50)   # Initialize PWM on pwmPin 100Hz frequency
        self.pwmB = gpio.PWM(self.GPIO_PIN_ENB, 50)   # Initialize PWM on pwmPin 100Hz 
        self.pwmA.start(90) #left thread
        self.pwmB.start(90) #right thread
        #gpio.output(self.GPIO_PIN_ENA, 1)
        #gpio.output(self.GPIO_PIN_ENB, 1)



        #pwmA.ChangeDutyCycle(100)
        #pwmB.ChangeDutyCycle(100)

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


    def Diagnose(self):

        #duration in seconds
        duration = .5

        #left caterpilar thread foward
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,1)		
        time.sleep(duration);
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,0)

        #left caterpilar thread reverse
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,1)
        time.sleep(duration);
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,0)

        #righ caterpilar thread foward
        gpio.output(self.GPIO_PIN_LEFT_SW_1,1 )
        time.sleep(duration);
        gpio.output(self.GPIO_PIN_LEFT_SW_1,0 )

        #right caterpilar thread foward
        gpio.output(self.GPIO_PIN_LEFT_SW_2,1 )
        time.sleep(duration);
        gpio.output(self.GPIO_PIN_LEFT_SW_2,0 )


        #caterpilar thread foward
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,1)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,1 )
        time.sleep(duration*10);
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,0)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,0 )

        #caterpilar thread re
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,1)
        gpio.output(self.GPIO_PIN_LEFT_SW_2,1 )
        time.sleep(duration*10);
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,0)
        gpio.output(self.GPIO_PIN_LEFT_SW_2,0 )
        


    def stop(self):
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,0)
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,0)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,0 )
        gpio.output(self.GPIO_PIN_LEFT_SW_2,0 )
        #print("stop")

    # FUNCTION      :	forward
    # DESCRIPTION   :	The forward servo motors start rotating
    # PARAMETERS    :	Integer type value that raise the the signal to hight for rotating servo motor
    # RETURNS       :	Nothing		

    def forward(self):
        #caterpilar thread foward
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,1)
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,0)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,1 )
        gpio.output(self.GPIO_PIN_LEFT_SW_2,0 )
        print("forward")


    # FUNCTION      :	backward
    # DESCRIPTION   :	The backward servo motors start rotating
    # PARAMETERS    :	Integer type value that raise the the signal to hight for rotating servo motor
    # RETURNS       :	Nothing		

    def backward(self):
        #caterpilar thread foward
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,0)
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,1)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,0 )
        gpio.output(self.GPIO_PIN_LEFT_SW_2,1 )
        print("backward")


    # FUNCTION      :	right
    # DESCRIPTION   :	The right side of servo motors start rotating
    # PARAMETERS    :	Integer type value that raise the the signal to hight for rotating servo motor
    # RETURNS       :	Nothing		

    def right(self):
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,1)
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,0)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,0 )
        gpio.output(self.GPIO_PIN_LEFT_SW_2,1 )
        print("right")


    # FUNCTION      :	left
    # DESCRIPTION   :	The left side of servo motors start rotating
    # PARAMETERS    :	Integer type value that raise the the signal to hight for rotating servo motor
    # RETURNS       :	Nothing	

    def left(self):
        gpio.output(self.GPIO_PIN_RIGHT_SW_1,0)
        gpio.output(self.GPIO_PIN_RIGHT_SW_2,1)
        gpio.output(self.GPIO_PIN_LEFT_SW_1,1 )
        gpio.output(self.GPIO_PIN_LEFT_SW_2,0 )
        print("left")


