"""
-----------------------------------------------------------------------
tc3625
Copyright (C) William Dickson, 2008.
  
wbd@caltech.edu
www.willdickson.com

Released under the LGPL Licence, Version 3

This file is part of tc3625.

tc3625 is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
    
tc3625 is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with tc3625.  If not, see
<http://www.gnu.org/licenses/>.

------------------------------------------------------------------------
 
Purpose: Implementation of the low level serial protocol for the model
TC-36-25 thermoelectric cooler temperature controller. The low level
interface implements the basic serial protocol as outlined in the
TC-36-25 Operation Manual.

The low level protocol packs the given write/read command into an
appropriate send string bounded by (stx) and (etx) characters. All
write values (integers) are converted to twos complement. A send and
recieve is performed for each write/read command and a checksum is
computed for each send and receive.

Note, for a write command, no checking is performed to verify that the
given integer value is within the ranges allowed by the controller.

Classes:
  TC3625_Serial

Function:
  get_checksum
  from_twoscomp
  to_twoscomp
  
Usage:

  # Initialization
  dev = TC3625_Serial()
    
  # Open serial connection to device
  dev.open() 

  # Write value to contorller, value should be integer value as specified in 
  # the operations manual. 
  val = dev.write(cmd_str,val) 
  
  # Read value from controller
  val = dev.read(cmd_str)

  # Close serial connection
  dev.close() 

  # List allowed command strings + read/write 
  dev.print_cmds()

  # Print additional help on a particular command string
  dev.print_help(cmd)

  # Print help on all command strings
  dev.print_help_all()
  

Author: Will Dickson  
----------------------------------------------------------------------------
"""
import struct
import serial

# Defualt Serial Port settings
DFLT_PORT='/dev/ttyS0'
DFLT_TIMEOUT=2.0
DFLT_BAUDRATE=9600

# Seial protocol constants
ADDRESS='00'
STX=chr(0x2a)
ETX=chr(0x0d)
ACK=chr(0x5e)

SEND_SIZE_WRITE=16
SEND_SIZE_READ=8
RETURN_SIZE=12

# Low level serial command description strings - these come directly from 
# the TC3625 serial protocol
INPUT1_DESCR_STR ="""\
 Reads the temperature of the primary thermister. Divide returned fixed
 point temperature by 100.0 and convert to deg F / deg C value.\
"""

DESIRED_CONTROL_VALUE_DESCR_STR="""\
 This command returns the set value determined by input2 or as a fixed
 value set by communications.\
"""

POWER_OUTPUT_DESCR_STR="""\
 Gets power output setting. -511 represents -100% output, 0 represensts
 0% output, and 511 reprsesnts 100% output.\
"""

ALARM_STATUS_DESCR_STR="""\
 bit 0 means high alarm
 bit 1 means low alarm
 bit 2 means computer controlled alarm
 bit 3 means over current detected
 bit 4 means open input1
 bit 5 means open input2 
 bit 6 mean driver low input voltage 
"""

INPUT2_DESCR_STR="""\
 Reads the secondary thermister temperature sensor. Divide returned
 fixed point temperature by 100.0 and convert to deg F / deg C value.\
"""

OUTPUT_CURRENT_COUNTS_DESCR_STR="""\
 Output current detection in A/D counts\
"""

ALARM_TYPE_DESCR_STR="""\
 0 sent or returned means no alarms 
 1 sent or returned means Tracking Alarm Mode 
 2 sent or returned means Fixed Alarm Mode 
 3 sent or returned means Computer Controlled Alarm Mode (see write command
 'alarm latch enable')\
"""

SET_TYPE_DEFINE_DESCR_STR="""
 Tells the controller how the set-point temperature will be communicated.
 0 sent or returned means computer communicated set value
 1 sent or returned means Potentiometer Input
 2 sent or returned means 0 to 5V Input
 3 sent or returned means 0 to 20mA Input
 4 sent or returned means 'differential set': Desired Control Value = 
 Temp2 + Computer Set\
"""

SENSOR_TYPE_DESCR_STR="""\
 Set/return the sensor type
 0 TS141 5K
 1 TS67 or TS136 15K
 2 TS91 10K
 3 TS165 230K
 4 TS104 50K
 5 YSI H TP53 10K\
"""

CONTROL_TYPE_DESCR_STR="""\
 Set/return the control type setting
 0 is deadband control
 1 is PID control
 2 is computer control. With this setting the output power sent to the cooler is
 determined by sending a write command to input1. The range of values then becomes
 -511 for -100% output power and 511 for 100% output power.\
"""

CONTROL_OUTPUT_POLARITY_DESCR_STR="""\
 Set/return the output polarity.
 0 is heat WP1+ and WP2-
 1 is heat WP2+ and WP1-\
"""

POWER_ONOFF_DESCR_STR="""\
 0 is off
 1 is on\
"""

OUTPUT_SHUTDOWN_IF_ALARM_DESCR_STR="""\
 Set/return output shutdown if alarm setting.
 0 is no shutdown upon alarm
 1 is to shutdown main output drive upon alarm
"""

FIXED_DESIRED_CONTROL_SETTING_DESCR_STR="""\
 Set/return desired control setting
 When writing, multiply the desired control temperature by 100 and convert to hex. This 
 becomes the send value. 
 When reading, convert the return value to decimal and divide by 100 to convert to deg F 
 or deg C.\
"""

PROPORTIONAL_BANDWIDTH_DESCR_STR="""\
 Fixed-point temperature bandwidth in deg F or deg C.\
"""

INTEGRAL_GAIN_DESCR_STR="""\
 Fixed-point integral gain in repeats/min. Multiply desired integral gain by 100.
 0.01 rep/min. would be decimal 1
 1.00 rep/min would be 100 decimal\
"""

DERIVATIVE_GAIN_DESCR_STR="""\
 Fixed point derivative gain in minutes. Multiply the desired derivative gain by 100.
 0.01 min. would be decimal 1
 1.00 min would be decimal 100\
"""

LOW_EXTERNAL_SET_RANGE_DCSR_STR="""\
 Value mapped to zero volatge of input2\
"""

HIGH_EXTERNAL_SET_RANGE_DSCR_STR="""\
 Value mapped to 5 volt or maximum voltage of input2\
"""

ALARM_DEADBAND_DSCR_STR="""\
 Temperature input1 must moveto toggle alarm output.\
"""

HIGH_ALARM_SETTING_DSCR_STR="""\
 Temperature reference to compare against input1 for high alarm output.\
"""

LOW_ALARM_SETTING_DSCR_STR="""\
 Temperature reference to compare against input1 for low alarm output.\
"""

CONTROL_DEADBAND_SETTING_DSCR_STR="""\
 Temperature or count span input1 must move to toggle control output.\
"""
INPUT1_OFFSET_DSCR_STR="""\
 Value to offset input1 by in order to calibrate external sensor if desired.\
"""

INPUT2_OFFSET_DSCR_STR="""\
 Value to offset input1 by in order to calibrate external sensor if desired.\
"""

HEAT_MULTIPLIER_DSCR_STR="""\
 Mutliplies the heater percentage power to offset its effectiveness.
 100 is a multiplier of 1.0
 1 is a multiplier of 0.01\
"""

COOL_MULTIPLIER_DSCR_STR="""\
 Mutliplies the cooling percentage power to offset its effectiveness.
 100 is a multiplier of 1.0
 1 is a multiplier of 0.01\
"""

OVER_CURRENT_COUNT_COMPARE_VALUE_DSCR_STR="""\
 This is the count compare value which determines an over-current condition. 
 The current is approximately 2.5 per count\
"""

ALARM_LATCH_ENABLE_DSCR_STR="""\
 Set/return alarm latch enable. 
 1 is latching enabled
 0 is latching disabled
 If 'alarm type' is 3 then
 1 is computer alarm on
 0 is computer alarm off\
"""

ALARM_LATCH_REQUEST_DSCR_STR="""\
 Resets the alarm latches\
"""

CHOOSE_SENSOR_FOR_ALARM_FUNCTION_DSCR_STR="""\
 0 is for the control sensor input
 1 is for the input2 secondary input\
"""

TEMPERATURE_WORKING_UNITS_DSCR_STR="""\
 0 is for F
 1 is for C\
"""

EEPROM_WRITE_ENABLE_DSCR_STR="""\
 0 is for disable eeprom writes
 1 is for enable eeprom writes
 On power-up or reset condition, the controller performs an initialization
 of all conmmand variables that have write commands by transfering the last 
 values used stored in non-volatile memory (EEPROM) to appropriately referenced 
 static RAM locations. When 'eeprom write enable' is enabled, any changes in the 
 run-time variables are also stored  eeprom as well as in RAM and thus will be 
 recalled on power-up or reset. Wheen 'eeprom write enable' is disabled, run time
 variables are stored only in RAM. Thus you can change run-time values without 
 changing power-up settings. Also max number of eeprom writes is 1,000,000.\  
"""

OVER_CURRENT_CONTINUOUS_DSCR_STR="""\
 1 is continuous retry when over current detected
 0 allows 'restart attempts' variable to be used\
"""

OVER_CURRENT_RESTART_ATTEMPTS_DSCR_STR="""\
 Range of value 0 to 30000
 This is the ammount of time the controller will attempt to restart the output 
 after an over current condition is detected.\
"""

JP3_DISPLAY_ENABLE_DSCR_STR="""\
 1 display function is enabled
 0 display function is disbaled\
"""

# Low level serial commands - from TC3625 serial protocol
SERIAL_CMDS = {
    'input1':{
        'write':None, 
        'read':'01',        
        'description':INPUT1_DESCR_STR,
        }, 
    'desired control value':{
        'write':None,
        'read':'03', 
        'description':DESIRED_CONTROL_VALUE_DESCR_STR,
        }, 
    'power output':{ 
        'write':None, 
        'read':'02', 
        'description':POWER_OUTPUT_DESCR_STR, 
        },
    'alarm status':{
        'write':None, 
        'read':'05', 
        'description':ALARM_STATUS_DESCR_STR,
        },
    'input2':{
        'write':None,
        'read':'06',
        'description':INPUT2_DESCR_STR,
        },
    'output current counts':{
        'write':None, 
        'read':'07',
        'description':OUTPUT_CURRENT_COUNTS_DESCR_STR,
        },
    'alarm type':{
        'write':'28',
        'read':'41',
        'description':ALARM_TYPE_DESCR_STR,
        },
    'set type define':{
        'write':'29', 
        'read':'42',
        'description':SET_TYPE_DEFINE_DESCR_STR,
        },
    'sensor type':{
        'write':'2a',
        'read':'43', 
        'description': SENSOR_TYPE_DESCR_STR,
        },
    'control type':{
        'write':'2b',
        'read':'44',
        'description':CONTROL_TYPE_DESCR_STR,
        },
    'control output polarity':{
        'write':'2c',
        'read':'45',
        'description':CONTROL_OUTPUT_POLARITY_DESCR_STR,
        },
    'power on/off':{
        'write':'2d',
        'read':'46',
        'description':POWER_ONOFF_DESCR_STR,
        },
    'output shutdown if alarm':{
        'write':'2e',
        'read':'47',
        'description':OUTPUT_SHUTDOWN_IF_ALARM_DESCR_STR,
        },
    'fixed desired control setting':{
        'write':'1c',
        'read':'50',
        'description': FIXED_DESIRED_CONTROL_SETTING_DESCR_STR,
        },
    'proportional bandwidth':{
        'write':'1d',
        'read':'51',
        'description':PROPORTIONAL_BANDWIDTH_DESCR_STR,
        },
    'integral gain':{
        'write':'1e',
        'read':'52',
        'description':INTEGRAL_GAIN_DESCR_STR,
        },
    'derivative gain':{
        'write':'1f',
        'read':'53',
        'description':DERIVATIVE_GAIN_DESCR_STR,
        },
    'low external set range':{
        'write':'20',
        'read':'54',
        'description':LOW_EXTERNAL_SET_RANGE_DCSR_STR,
        },
    'high external set range':{
        'write':'21',
        'read':'55',
        'description':HIGH_EXTERNAL_SET_RANGE_DSCR_STR,
        },
    'alarm deadband':{
        'write':'22',
        'read':'56',
        'description':ALARM_DEADBAND_DSCR_STR,
        },
    'high alarm setting':{
        'write':'23',
        'read':'57',
        'description':HIGH_ALARM_SETTING_DSCR_STR,
        },
    'low alarm setting':{
        'write':'24',
        'read':'58',
        'description':LOW_ALARM_SETTING_DSCR_STR,
        },
    'control deadband setting':{
        'write':'25',
        'read':'59',
        'description':CONTROL_DEADBAND_SETTING_DSCR_STR,
        },
    'input1 offset':{
        'write':'26',
        'read':'5a',
        'description':INPUT1_OFFSET_DSCR_STR,
        },
    'input2 offset':{
        'write':'27',
        'read':'5b',
        'description':INPUT2_OFFSET_DSCR_STR,
        },
    'heat multiplier':{
        'write':'0c',
        'read':'5c',
        'description':HEAT_MULTIPLIER_DSCR_STR,
        },
    'cool multiplier':{
        'write':'0d',
        'read':'5d',
        'description':COOL_MULTIPLIER_DSCR_STR,
        },
    'over current count compare value': {
        'write':'0e',
        'read':'5e',
        'description':OVER_CURRENT_COUNT_COMPARE_VALUE_DSCR_STR,
        },
    'alarm latch enable':{
        'write':'2f',
        'read':'48',
        'description':ALARM_LATCH_ENABLE_DSCR_STR,
        },
    'alarm latch request':{
        'write':'33',
        'read':None,
        'description':ALARM_LATCH_REQUEST_DSCR_STR,
        },
    'choose sensor for alarm function':{
        'write':'31',
        'read':'4a',
        'description':CHOOSE_SENSOR_FOR_ALARM_FUNCTION_DSCR_STR,
       },
    'temperature working units': {
        'write':'32',
        'read': '4b',
        'description':TEMPERATURE_WORKING_UNITS_DSCR_STR,
        },
    'eeprom write enable': {
        'write': '34',
        'read': '4c',
        'description':EEPROM_WRITE_ENABLE_DSCR_STR,
        },
    'over current continuous':{
        'write':'35',
        'read':'4d',
        'description':OVER_CURRENT_CONTINUOUS_DSCR_STR,
        },
    'over current restart attempts':{
        'write':'0f',
        'read':'5f',
        'description':OVER_CURRENT_RESTART_ATTEMPTS_DSCR_STR,
        },
    'JP3 display enable':{
        'write':'36',
        'read':'4e',
        'description':JP3_DISPLAY_ENABLE_DSCR_STR,
        },
}

class TC3625_Serial:

    """ 
    Implementation of low level serial protocol for TC3625
    thermoelectric temperature controller.
    """

    def __init__(self,
                 port=DFLT_PORT,
                 timeout=DFLT_TIMEOUT,
                 baud_rate=DFLT_BAUDRATE,
                 ):
        self.port=port
        self.timeout=timeout
        self.baud_rate=baud_rate
        self.address=ADDRESS
        self.serial_cmds = SERIAL_CMDS
        self.stx=STX
        self.etx=ETX
        self.ack=ACK

    def get_rw_str(self, cmd):
        """
        Get the read/write string for a given command
        """
        rw_str = ''
        if self.serial_cmds[cmd]['read'] != None:
            rw_str+='r'
        if self.serial_cmds[cmd]['write'] != None:
            rw_str+='w'
        if len(rw_str) > 0:
            rw_str = '(%s)'%(rw_str,)
        return rw_str

    def print_cmds(self):
        """ list all serial commands """
        cmd_keys = self.serial_cmds.keys()
        cmd_keys.sort()
        for cmd in cmd_keys:
            print '%s %s'%(cmd,self.get_rw_str(cmd),)
            
    def print_help_all(self, rw=False):
        """ Displays a list of all serial commands."""
        cmd_keys = self.serial_cmds.keys()
        cmd_keys.sort()
        for cmd in cmd_keys:
            self.print_help(cmd)
            print 

    def print_help(self, cmd, rw=False):
        """print write/read values and description for a given command."""
        print 'command: %s %s'%(cmd, self.get_rw_str(cmd),)
        if rw==True:
            self.print_rw(cmd)
        print self.serial_cmds[cmd]['description']

    def print_rw(self,cmd):
        """print the read write charatcers for the given commands."""
        print 'write: ', self.serial_cmds[cmd]['write']
        print 'read: ', self.serial_cmds[cmd]['read']
        
    def open(self):
        """ Open serial port """
        self.serial = serial.Serial(
            self.port,
            timeout = self.timeout,
            bytesize=serial.EIGHTBITS,
            baudrate=self.baud_rate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=0,
            rtscts=0,
            )
        return self.serial.isOpen()
    
    def write(self, cmd, val):
        """ 
        Generic write command - used to set values in controller. 

        Allowed command strings 'cmd' are those in the self.serial_cmds
        for which write is not None. 

        Allowed values for a given command string can be found in the
        TC-36-25 operation manual, by using dev.print_help(cmd_str), or
        by looking at the *_DSCR_STR variables. The values should be
        specified as signed integer and not as twos complement as the
        twos complement required for the send string is computed by
        this function. 
        """
        if self.serial_cmds[cmd]['write']==None:
            raise ValueError, 'write unsupported for command %s'%(cmd,)
        # Create serial command
        cc=self.serial_cmds[cmd]['write']
        val = int(val)
        val_2c = to_twoscomp(val)
        cs=get_checksum(self.address+cc+val_2c)
        cmd_list = [self.stx,self.address[0],self.address[1],cc[0],cc[1]]
        for x in val_2c:
            cmd_list.append(x)
        cmd_list.extend([cs[0],cs[1],self.etx])
        cmd = struct.pack('c'*SEND_SIZE_WRITE,*cmd_list)
        # Send serial command and read response
        self.serial.write(cmd)
        self.serial.flush()
        ret = self.serial.read(RETURN_SIZE)
        cs = get_checksum(ret[1:-3])
        cs_ret = ret[-3:-1]
        if cs != cs_ret:
            raise IOError, 'return checksum %s does not match calculated %s'%(cs_ret,cs)
        if ret[1:-3] == 'X'*8:
            raise IOError, 'sent checksum incorrect'
        return from_twoscomp(ret[1:-3])

    def read(self, cmd):
        """ 
        Generic read command - used to read values from controller
        
        Allowed command strings 'cmd' are those in the
        self.serial_cmds for which read is not None. For more detials
        on particular commands see the TC-36-25 operation manual, use
        dev.print_help(cmd), or see the appropriate _DSCR_STR
        variable.
        """
        if self.serial_cmds[cmd]['read']==None:
            raise ValueError, 'read unsupported for command %s'%(cmd,)
        # Create serial command
        cc=self.serial_cmds[cmd]['read'] 
        cs=get_checksum(self.address+cc)
        cmd_tuple = (self.stx,self.address[0],self.address[1],cc[0],cc[1],cs[0],cs[1],self.etx)
        cmd = struct.pack('c'*SEND_SIZE_READ,*cmd_tuple)
        # Send serial command and read response
        self.serial.write(cmd)
        self.serial.flush()
        ret = self.serial.read(RETURN_SIZE)
        cs = get_checksum(ret[1:-3])
        cs_ret = ret[-3:-1]
        if cs != cs_ret:
            raise IOError, 'return checksum %s does not match calculated %s'%(cs_ret,cs)
        if ret[1:-3] == 'X'*8:
            raise IOError, 'sent checksum incorrect'
        return from_twoscomp(ret[1:-3])

    def close(self):
        """ Close serial port"""
        self.serial.close()

# ------------------------------------------------------------------------------------
# Utility functions

def get_checksum(val):
    """
    Calculate the checksum for given string
    """
    cs=0
    for v in val:
        cs+=ord(v)
    cs_hex = '%x'%(cs,)
    return cs_hex[-2:]
    

def to_twoscomp(x):
    """
    Compute two's complement of hex string from an integer. Note the
    hex string is padded with zeros so that it is always 8 characters
    in length.
    """
    if x < 0:
        x2c = int(16**8+x)
    else:
        x2c = int(x)
    return '%08x'%(x2c,)


def from_twoscomp(x):
    """
    Convert 8 charcter hex string given in twos complememt to signed
    integer.
    """
    x2c = int(x,16)
    if x2c >= (16**8)/2:
        y = int(x2c-16**8)
    else:
        y = x2c
    return y



                             
