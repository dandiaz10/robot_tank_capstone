
import time
import os 

#https://www.raspberrypi.org/app/uploads/2012/02/BCM2835-ARM-Peripherals.pdf
#https://jumpnowtek.com/rpi/Using-the-Raspberry-Pi-Hardware-PWM-timers.html
#page 140
#PW0 -> GPIO18 (Using Alt Function 5), pin 12
#PW1 -> GPIO19 (Using Alt Function 5), pin 35


class PWM:

    #Both duty_cycle and period expect values in nanoseconds
    timeBase = 1e9    
    period= None
    dutySaved = None
    _Channel = None
    frequency=None
    
    def __init__(self, Channel):
        self._Channel=Channel

    def freq(self,Value):
        
        self.frequency=Value
        self.period = self.timeBase/Value
        os.system("echo " + str(int(self.period))+ " > /sys/class/pwm/pwmchip0/pwm"+str(self._Channel)+"/period")


    def Start(self,Freq):
        
        
        #https://jumpnowtek.com/rpi/Using-the-Raspberry-Pi-Hardware-PWM-timers.html
        #enable the PWM1
        os.system("echo "+str(self._Channel)+" > /sys/class/pwm/pwmchip0/export") 
        #wait for hardware initialization
        time.sleep(1)   
        #setup the PWM frequency 1Khz
        self.frequency=Freq        
        self.period = self.timeBase/self.frequency
        os.system("echo " + str(int(self.period))+ " > /sys/class/pwm/pwmchip0/pwm"+str(self._Channel)+"/period") 
        #Set the initial duty cycle
        if(self.dutySaved !=None):
            self.Duty(self.dutySaved)
        #enable the hardware
        os.system("echo 1 > /sys/class/pwm/pwmchip0/pwm"+str(self._Channel)+"/enable") 
        
    def Stop(self):
        os.system("echo 0 > /sys/class/pwm/pwmchip0/pwm"+str(self._Channel)+"/enable")
        os.system("echo "+str(self._Channel)+" > /sys/class/pwm/pwmchip0/unexport") 


    def Duty(self,Value):
        

        self.dutySaved = Value
        
        if (self.period ==None):
            print("PWM not initialized")
            return
        
        if (Value > 100.0) or (Value < 0):
            print("Duty must be between 0.0 and 100.0")
            return
            
        os.system("echo "+ str(int(  self.period*(Value/100.0)  )) +" > /sys/class/pwm/pwmchip0/pwm"+str(self._Channel)+"/duty_cycle") 
