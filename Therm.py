# The Thermocycler class acts as a wrapper for William Dickenson's TC3625 API found on bit bucket:
# https://bitbucket.org/willdickson/tc3625/src/1301d8015f88e3e131d89264d033906987882ed2/tc3625/tc3625.py?at=default&fileviewer=file-view-default
# The Thermocycler class allows users to interact with the TC3625 board at a high level to specify thermocycling protocols
# The class specifies the standard TC3625 parameters for the user, to protect the hardware from user error.

import tc3625
import time
from threading import Lock

class Thermocycler:
    def __init__(self, _port):

        # initialize arrays to log time and temperature throughout script protocol
        self.timeLog = []
        self.tempLog = []
        self.setpointLog = []
        self.outCurrLog = []
        self.setpt = 'undefined'
        self.currentTemp = None
        self.tc3625Lock = Lock()

        #open tc3625 object, coded at caltech to talk to the device.
        try:
            self.ctlr = tc3625.TC3625(port=_port, max_attempt=1)
            self.ctlr.open()
        except(IOError):
            raise IOError("Could not connect to "+_port+".")

        #set control Temp Type to computer controlled set point
        self.ctlr.set_setpt_type('computer')

        #Set temp high range to 105 C
        self.ctlr.set_high_external_set_range(105)

        #Set temp low range to 0 C
        self.ctlr.set_low_external_set_range(0)

        #Set control type to PID control
        self.ctlr.set_control_type('PID')

        # Set Control mode to WP2 + and WP1 -
        self.ctlr.set_output_polarity('heat wp1+ wp2-')

        # Set alarm type to fixed value alarms
        self.ctlr.set_alarm_type('fixed')

        # Set POWER SHUTDOWN IF ALARM to MAINOUT SHUTDOWN IF ALARM
        self.ctlr.set_shutdown_if_alarm('off')

        # Set high alarm setting to 100 C. If the temperate of the plate surpasses this, the system will shut off.
        self.ctlr.set_high_alarm(105)

        # Set low alarm setting to 0 C. If the temperature of the plate gets bellow this, the system will shut off.
        self.ctlr.set_low_alarm(0)

        # Set Alarm Deadband to 10 C
        self.ctlr.set_alarm_deadband(5)

        # Set alarm latch to alarm latch on
        self.ctlr.set_alarm_latch('on')

        # Set sensor type to TS-67, TS132 15K
        #self.ctlr.set_sensor_type('TS67 TS136 15K') #Default thermistor with orange wires
        self.ctlr.set_sensor_type('TS103 50K') #This is the MP-3022 for use with Nick's water cooled thermocycler

        # Set Sensor for alarm to CONTROL SENSOR
        self.ctlr.set_alarm_sensor('input1')

        # Set temperature scale to Celsius
        self.ctlr.set_working_units('C')

        # Set overcurrent level to 15 A
        self.ctlr.set_over_current_compare(30)

        # Set overcurrent level restart attempts to continuous
        self.ctlr.set_over_current_restart_type('continuous')


        # PID settings, P = 1
        self.ctlr.set_proportional_bandwidth(3)
        self.ctlr.set_integral_gain(1)
        self.ctlr.set_derivative_gain(0)


        #PID control settings
        self.ctlr.set_heat_multiplier(1)
        self.ctlr.set_cool_multiplier(1)

    def setPowerOn(self):
        self.tc3625Lock.acquire()
        self.ctlr.set_power_state('on')
        self.tc3625Lock.release()
        
    def setPowerOff(self):
        self.tc3625Lock.acquire()
        self.ctlr.set_power_state('off')
        self.tc3625Lock.release()

    def getTemp(self):
        self.tc3625Lock.acquire()
        self.currentTemp = self.ctlr.get_input1()
        self.tc3625Lock.release()
        return self.currentTemp


    def getOutCurr(self):
        self.tc3625Lock.acquire()
        curr =  self.ctlr.get_output_current()
        self.tc3625Lock.release()
        return curr

    def setPoint(self, temp):
        if type(temp) != int:
            raise TypeError('set point must be an integer')
        if temp < 0 or temp > 100:
            raise ValueError('This thermocycler operates between 0 C and 100C. Please enter a set point in that range.')
        print("Set point to " + str(temp))
        self.tc3625Lock.acquire()
        self.ctlr.set_setpt(temp)
        self.tc3625Lock.release()
        self.setpt = temp
        self.log()

    #We will say the PID controller is equilibrated if the last 20 temp logs have been within 0.1 C of each other.
    def checkEquil(self):
        for i in self.tempLog[-20]:
            if i -self.tempLog[-1] > 0.1 or i - self.setpt > 0.3:
                #if any are more than 0.1 away from the current temp,
                return False
        #otherwise,
        return True

    def waitEquil(self):
        equil = False
        while not equil:
            time.sleep(1)
            self.log()
            equil = self.checkEquil()


    def setIntegralGain(self,gain):
        if (type(gain) != int) and (type(gain) != float):
            raise TypeError("The integral gain must be either an integer or a float.")
        self.tc3625Lock.acquire()
        self.ctlr.set_integral_gain(gain)
        self.tc3625Lock.release()

    def setDerivativeGain(self,gain):
        if (type(gain) != int) and (type(gain) != float):
            raise TypeError("The derivative gain must be either an integer or a float.")
        self.tc3625Lock.acquire()
        self.ctlr.set_derivative_gain(gain)
        self.tc3625Lock.release()

    #specify the number of seconds to pause.
    def pause(self,pause):
        if type(pause) != int and type(pause) != float:
            raise TypeError("Error: Pause time must be a float or an int.")
        if pause < 0:
            raise ValueError("Error: Pause time must be positive.")

        time.sleep(pause)


    def log(self):
        self.tempLog.append(float(self.getTemp()))
        #self.timeLog.append(float(time.clock()))
        #self.setpointLog.append(self.setpt)
        #self.outCurrLog.append(self.getOutCurr())

    def destroy(self):
        print("Shutting Down...")
        self.setPowerOff()

