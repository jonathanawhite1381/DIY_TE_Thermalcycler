# The Thermocycler class acts as a wrapper for William Dickenson's TC3625 API found on bit bucket:
# https://bitbucket.org/willdickson/tc3625/src/1301d8015f88e3e131d89264d033906987882ed2/tc3625/tc3625.py?at=default&fileviewer=file-view-default
# The Thermocycler class allows users to interact with the TC3625 board at a high level to specify thermocycling protocols
# The class specifies the standard TC3625 parameters for the user, to protect the hardware from user error.

import tc3625
import time
import csv
from matplotlib import pyplot as plt

class Thermocycler:
    def __init__(self, _port):
        if type(_port) != str:
            raise Exception("Error: Please enter port name as a string.")

        # initialize arrays to log time and temperature throughout script protocol
        self.timeLog = ["Times"]
        self.tempLog = ["Temperature"]
        self.setpointLog = ["Set_Point"]
        self.setPoint = 'undefined'

        #open port
        #self.ser = serial.Serial(port)

        #set TC3625 control to a computer determined set point
        #message = "(stx)002900000000(ext)"
        self.ctlr = tc3625.TC3625(port=_port)

        self.ctlr.open()

        #set control Temp Type to to computer controlled set point
        self.ctlr.set_setpt_type('computer')

        #Set temp high range to 100 C
        self.ctlr.set_high_external_set_range(100)

        #Set temp low range to 0 C
        self.ctlr.set_low_external_set_range(0)

        #Set control type to PID control
        self.ctlr.set_control_type('PID')

        # Set Control mode to WP2 + and WP1 -
        self.ctlr.set_output_polarity('heat wp2+ wp1-')

        # Set alarm type to fixed value alarms
        self.ctlr.set_alarm_type('fixed')

        # Set POWER SHUTDOWN IF ALARM to MAINOUT SHUTDOWN IF ALARM
        self.ctlr.set_shutdown_if_alarm('on')

        # Set high alarm setting to 100 C. If the temperate of the plate surpasses this, the system will shut off.
        self.ctlr.set_high_alarm('100')

        # Set low alarm setting to 0 C. If the temperature of the plate gets bellow this, the system will shut off.
        self.ctlr.set_low_alarm('0')

        # Set Alarm Deadband to 10 C
        self.ctlr.set_alarm_deadband(10)

        # Set alarm latch to alarm latch on
        self.ctlr.set_alarm_latch('on')

        # Set sensor type to TS-67, TS132 15K
        self.ctlr.set_sensor_type('TS67 TS136 15K') #! double check the serial on this, it looks like bill put a 6 where there should be a 2

        # Set Sensor for alarm to CONTROL SENSOR
        self.ctlr.set_alarm_sensor('input1')

        # Set temperature scale to Celsius
        self.ctlr.set_working_units('C')

        # Set overcurrent level to 15 A
        self.ctlr.set_over_current_compare(15)

        # Set overcurrent level restart attempts to continuous
        self.ctlr.set_overcurrent_restart_type('continuous')

        # Set output to on
        self.ctlr.power_on('on')

        #PID control settings

        self.ctlr.set_heat_multiplier(1)
        self.ctlr.set_cool_multiplier(1)



    def getTemp(self):
        return self.ctlr._get_value('input1')


    def setPoint(self, temp):
        if type(temp) != int:
            raise TypeError('set point must be an integer')
        if temp <= 0 or temp >= 100:
            raise ValueError('This thermocycler operates between 0 C and 100C. Please enter a set point in that range.')
        self.ctlr.set_setpt(temp)
        self.setPoint = temp
        self.log()

    def setIntegralGain(self,gain):
        if (type(gain) != int) and (type(gain) != float):
            raise TypeError("The integral gain must be either an integer or a float.")
        self.ctlr.set_integral_gain(gain)

    def setDerivativeGain(self,gain):
        if (type(gain) != int) and (type(gain) != float):
            raise TypeError("The derivative gain must be either an integer or a float.")
        self.ctlr.set_derivative_gain(gain)

    #specify the number of seconds to pause. Will log a temperature measurement and time every second during the pause.
    def pauseLog(self,pause):
        start = time.clock()
        while(True):
            time.sleep(1)
            self.log()
            if self.timeLog[-1] - start > pause:
                break

    def log(self):
            self.tempLog.append(self.getTemp)
            self.timeLog.append(time.clock())
            self.setpointLog.append(self.setPoint)

    def writeLogs(self,name):

        timestamp = time.ctime().split()[1:]
        nameerror = False
        if type(name) == str:
            name = 'Log'
            nameerror = True
        for s in timestamp:
            name += "_%s"%(s)

        #save plot of temperature vs set point
        plt.plot(self.timeLog, self.setpointLog, label='Set Point')
        plt.plot(self.timeLog, self.tempLog, label='Temperature')
        plt.savefig(name + '.png')
        name += ".csv"
        name.replace(":","")

        #save csv file of temperatures and set point series.
        writelist = zip(self.timeLog, self.setpointLog, self.tempLog )
        with open(name, 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(writelist)
        if nameerror: # raise this after saving so user can't lose all their data with a simple error.
            raise ValueError("Filename must be string. Logs files named by time stamp.")




















