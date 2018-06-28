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

Purpose: high level python API for RS232 communication with the
TC-36-25 thermoelectric cooler temperature controllers.

The high level API provides a wrapper around the low level serial
interface provided by the TC3625_Serial class. The high level API
provides human pneumonics for the various controller settings, and
enables set-point values, limits, gains etc to be set directly in deg
F or deg C.

Classes:
  TC3625
  Method
  Get_Type
  Get_Mask
  Get_Num
  Set_type
  Set_Num
  Set_NoArg
  
Functions:
  int2dec
  dec2int
  amp2cnt
  cnt2amp


Note: some functions may require special case treatment such as: 
get_alarm_status.

Author: Will Dickson

-------------------------------------------------------------------
"""
from tc3625_serial import TC3625_Serial

# Default port settings
DFLT_PORT='/dev/ttyS0'
DFLT_TIMEOUT=2.0
DFLT_BAUDRATE=9600
DFLT_MAX_ATTEMPT=10

AMPS_PER_COUNT=2.5

# Types and values
ALARM_VALUES={
    'high': 0,
    'low': 1,
    'computer controlled': 2,
    'current':3,
    'open input1':4,
    'open input2':5,
    'driver low voltage':6,
    }
ALARM_TYPES={
    'none':0,
    'tracking':1,
    'fixed':2,
    'computer':3,
    }
ALARM_SENSOR_TYPES={
    'input1':0,
    'input2':1,
    }
SETPT_TYPES={
    'computer':0,
    'potentiometer':1,
    'voltage':2,
    'current':3,
    'differential':4,
    'MP2986': 5
    }
SENSOR_TYPES = {
    'TS141 5K':0,
    'TS67 TS136 15K':1,
    'TS91 10K':2,
    'TS165 230K':3,
    'TS103 50K':4,
    'YSI H TP53 10K':5,
    }
CONTROL_TYPES = {
    'deadband':0,
    'PID':1,
    'computer':2,
    }
TEMP_TYPES = {
    'F':0,
    'C':1,
    }
RESTART_TYPES = {
    'max attempt':0,
    'continuous':1,
    }
OUTPUT_POLARITY_TYPES = {
    'heat wp1+ wp2-':0,
    'heat wp2+ wp1-':1,
}
ON_OFF_TYPES = {
    'on':1,
    'off':0,
    }

# Range intervals  
PROPORTIONAL_BANDWIDTH_RANGE=(0,1000) # !!!!! JUST MADE THIS UP !!!!!!
INTEGRAL_GAIN_RANGE = (0,10)
DERIVATIVE_GAIN_RANGE=(0,10)
MULTIPLIER_RANGE=(0.0,2.0)
OVER_CURRENT_RANGE=(0,40)
POWER_RANGE=(-5.11,5.11)
RESTART_ATTEMPT_RANGE=(0,30000)

# Method documentation strings
GET_INPUT1_DOC="""\
Reads the temperature of the primary thermister temperature
sensor. Returned as either deg F or deg C value depending on
working units. \
"""
GET_INPUT2_DOC="""\
Reads the temperature of the secondary thermister temperature
sensor. Returned as either deg F or deg C value depending on
working units.\
"""
GET_CONTROL_VALUE_DOC="""\
This command returns the set value determined by input2 or as
a temprature value set by communications. \
"""
GET_POWER_OUTPUT_DOC="""\
Reads power output as percentage.\
"""
GET_ALARM_STATUS_DOC="""\
Returns a tuple consisting of an alarm flag and a list of of
all active alarms. The alarm flag will be False and the list
empty if there are no active alarms. \
"""
GET_OUTPUT_CURRENT_DOC="""\
Returns output current in Amps.\
"""
GET_ALARM_TYPE_DOC="""\
Returns current alarm type setting. Allowed values are 'none', 
'tracking', 'fixed', and 'computer'. See the TC-36-25  operation 
manual for details.\
"""
SET_ALARM_TYPE_DOC="""\ 
Set the alarm type. Allowed values are 'none', 'tracking', 'fixed', 
and computer. See the TC-36-25 operation manual for details.\
"""
GET_SETPT_TYPE_DOC="""\
Returns the current set-point type. Allowed values are 
  'computer' - computer communicated value 
  'potentiometer' - potentiometer input
  'voltage' - 0 to 5V input
  'current' - 0 to 20mA input 
  'differential' - differential set (desired control value = temp2+computer set)
  'MP2986' - value from optional MP-2986 display
See the TC-36-25 operation manual for details.\
"""
SET_SETPT_TYPE_DOC="""\
Set the set-point type. Allowed values are
  'computer' - computer communicated value 
  'potentiometer' - potentiometer input
  'voltage' - 0 to 5V input
  'current' - 0 to 20mA input 
  'differential' - differential set (desired control value = temp2+computer set)
  'MP2986' - value from optional MP-2986 display

See the TC-36-25 operation manual for details.\
"""
GET_SENSOR_TYPE_DOC="""\
Returns current sensor type setting. Allowed values are 'TS141 5K', 
'TS67 TS136 15K', 'TS91 10K', 'TS165 230K', 'TS104 50K', 'YSI H TP53 10K' 

See the TC-36-25 operation manual for details.\
"""
SET_SENSOR_TYPE_DOC="""\
Sets the sensor type. Allowed values are 'TS141 5K', 
'TS67 TS136 15K', 'TS91 10K', 'TS165 230K', 'TS104 50K', 'YSI H TP53 10K' 

See the TC-36-25 operation manual for details.\
"""
GET_CONTROL_TYPE_DOC="""\
Returns the current control type setting. Allowed values are
'deadband', 'PID', and 'computer' \
"""
SET_CONTROL_TYPE_DOC="""\
Set the control type. Allowed values are 'deadband', 'PID', and 'computer' \
"""
GET_OUTPUT_POLARITY_DOC="""\
Returns the current control output polarity setting. Allowed values are 
'heat wp1+ wp2-' and 'heat wp2+ wp1-'.\
"""
SET_OUTPUT_POLARITY_DOC="""
Set the control output polarity. Allowed values are  'heat wp1+ wp2-' 
and 'heat wp2+ wp1-'. \
"""
GET_POWER_STATE_DOC="""\
Returns the current state of the system power output.  Allowed
values 'on' or 'off'
"""
SET_POWER_STATE_DOC="""\
Set the power state of the system. Allowed values 'on or 'off'.\
"""
GET_SHUTDOWN_IF_ALARM_DOC="""\
Return the current value of the 'output shutdown if alarm' setting 
of the controller. 
"""
SET_SHUTDOWN_IF_ALARM_DOC="""\
Set the 'output shutdown if alarm' setting of the controller. 
Allowed values 'on' or 'off'\
"""
GET_FIXED_CONTROL_SETTING_DOC="""\
Return the fixed desired control setting. 
        
When control type is 'deadband' or 'PID' this corresponds to the 
set-point temperature in either deg F or deg C depeding on the 
working units.
        
When control type is 'computer' this corresponds
with the output power setting and should be in the range
[-5.11, 5.11]\
"""
SET_FIXED_CONTROL_SETTING_DOC="""\
Sets the fixed desired control setting. 
        
When control type is 'deadband' or 'PID' this corresponds 
to the set-point temperature in either deg F or deg C depeding 
on the working units.
        
When control type is 'computer' this corresponds
with the output power setting and should be in the range
[-5.11, 5.11]\
"""
GET_SETPT_DOC="""\
Return the current set-point. (Note this command is just an
alias for get_fixed_control_setting.)

When control type is 'deadband' or 'PID' this corresponds to the 
set-point temperature in either deg F or deg C depeding on the 
working units.
        
When control type is 'computer' this corresponds
with the output power setting and should be in the range
[-5.11, 5.11]\
"""
SET_SETPT_DOC="""\
Sets the control set-point.(Note this command is just an
alias for set_fixed_control_setting.)

When control type is 'deadband' or 'PID' this corresponds to the 
set-point temperature in either deg F or deg C depeding on the 
working units.
        
When control type is 'computer' this corresponds
with the output power setting and should be in the range
[-5.11, 5.11]\
"""
GET_PROPORTIONAL_BANDWIDTH_DOC="""\
Return the controller's proportional bandwidth setting. This is
the temperature range, in deg F or C, over which the output
power is proportioned from -100% to 100%. The bandwidth is
cenetered about the set-point value. The controller ouput
power is 100% at the end of the bandwidth range above the
set-point, it decreases to 0% as it reaches the set-point, and
is -100% at the end of the bandwidth range below the
set-point.

If the bandwidth is too narrow the temperature will oscillate
around the set-point. If it is too wide the controller will be
slow to respond.\
"""
SET_PROPORTIONAL_BANDWIDTH_DOC="""\
Set the controller's proportional bandwidth. This is the
temperature range, in deg F or C, over which the output power
is proportioned from -100% to 100%. The bandwidth is cenetered
about the set-point value. The controller ouput power is 100%
at the end of the bandwidth range above the set-point, it
decreases to 0% as it reaches the set-point, and is -100% at
the end of the bandwidth range below the set-point.

If the bandwidth is too narrow the temperature will oscillate
around the set-point. If it is too wide the controller will be
slow to respond.\
"""
GET_INTEGRAL_GAIN_DOC="""\
Return the controller's integral gain setting in repeats/min. 
This value should be in with the interval INTEGRAL_GAIN_RANGE.
        
If the integral gain is too high, the temperature will
oscillate. If it is too low it will take a long time to reach
steady state value.\
"""
SET_INTEGRAL_GAIN_DOC="""\
Set the controller's integral gain in repeats/min. This value
should be in with the interval INTEGRAL_GAIN_RANGE.
        
If the integral gain is too high, the temperature will
oscillate. If it is too low it will take a long time to reach
steady state value.\
"""
GET_DERIVATIVE_GAIN_DOC="""\
Return the controller's derivative gain setting in cycles per
minute. The derivative gain senses the rate of change of
temperature and allows the controller to anticipate the power
need for rapid changes in system loading. Usually this term is
only used for very sluggish systems or when a very quick
response is needed. This value should be with in the interval
DERIVATIVE_GAIN_RANGE.\
"""
SET_DERIVATIVE_GAIN_DOC="""\
Set the controller's derivative gain setting in cycles per
minute. The derivative gain senses the rate of change of
temperature and allows the controller to anticipate the power
need for rapid changes in system loading. Usually this term is
only used for very sluggish systems or when a very quick
response is needed. This value should be with in the interval
DERIVATIVE_GAIN_RANGE.\
"""
GET_LOW_EXTERNAL_SET_RANGE_DOC="""\
Returns the low external set range of the controller. When the
set-point type is determined by remote input, set-point type 
'volatge' or 'current'. The high and low external set range values 
are used to linearly scale the temperature range (or fixed % of 
output power) to the full range of the external input. \ 
"""
SET_LOW_EXTERNAL_SET_RANGE_DOC="""\
Sets the low external set range of the controller. When the
set-point type is determined by remote input, set-point type
'volatge' or 'current'. The high and low external set range values 
are used to linearly scale the temperature range (or fixed % of 
output power) to the full range of the external input.  
"""
GET_HIGH_EXTERNAL_SET_RANGE_DOC="""\
Returns the high external set range of the controller. When the
set-point type is determined by remote input, set-point type 
'volatge' or 'current'. The high and low external set range values 
are used to linearly scale the temperature range (or fixed % of 
output power) to the full range of the external input. \ 
"""
SET_HIGH_EXTERNAL_SET_RANGE_DOC="""\
Sets the low external set range of the controller. When the
set-point type is determined by remote input, set-point type
'volatge' or 'current'. The high and low external set range values 
are used to linearly scale the temperature range (or fixed % of 
output power) to the full range of the external input.  
"""
GET_ALARM_DEADBAND_DOC="""\
Return the controllers alarm deadband setting. The alarm
deadband is the value that input1 must move (from set-point)
in order to toggle alarm output\
"""
SET_ALARM_DEADBAND_DOC="""\
Set the controllers alarm deadband. The alarm deadband is the
value that input1 must move (from set-point) in order to
toggle alarm output
"""
GET_HIGH_ALARM_DOC="""\
Return the controllers high alarm setting. The high alarm
setting is the temperature to compare against input1 for high
alarm output.\
"""
SET_HIGH_ALARM_DOC="""\
Set the controllers high alarm setting. The high alarm
setting is the temperature to compare against input1 for high
alarm output.\
"""
GET_LOW_ALARM_DOC="""\
Return the controllers low alarm setting. The low alarm
setting is the temperature to compare against input1 for low
alarm output.\
"""
SET_LOW_ALARM_DOC="""\
Set the controllers low alarm setting. The low alarm
setting is the temperature to compare against input1 for low
alarm output.\
"""
GET_CONTROL_DEADBAND_DOC="""\
Returns the control deadband setting. This is the temperature
or count span that input1 must move in order to toggle the
control output.\
"""
SET_CONTROL_DEADBAND_DOC="""\
Set the control deadband. This is the temperature or count span that 
input1 must move in order to toggle the control output. \
"""
GET_INPUT1_OFFSET_DOC="""\
Return input1 offset. This value is used to offset input1 in order 
to calibrate external sensor.\
"""
SET_INPUT1_OFFSET_DOC="""\
Set input1 offset. This value is used to offset input1 in order to 
calibrate external sensor.\
"""
GET_INPUT2_OFFSET_DOC="""\
Return input2 offset. This value is used to offset input2 in order 
to calibrate external sensor.
"""
SET_INPUT2_OFFSET_DOC="""\
Set input2 offset. This value is used to offset input2 in order to 
calibrate external sensor.
"""
GET_HEAT_MULTIPLIER_DOC="""\
Return the controller's heat side multiplier. Numerical
multiplier used to compensate for the nonsymmetrial response,
between heat and cool modes, of the thermoelectric cooler.

Values must be within interval MULTIPLIER_RANGE.\
"""
SET_HEAT_MULTIPLIER_DOC="""\
Set the controller's heat side multiplier. Numerical
multiplier used to compensate for the nonsymmetrial response,
between heat and cool modes, of the thermoelectric cooler.

Values must be within interval MULTIPLIER_RANGE.        
"""
GET_COOL_MULTIPLIER_DOC="""\
Return the controller's cool side multiplier. Numerical
multiplier used to compensate for the nonsymmetrial response,
between heat and cool modes, of the thermoelectric cooler.

Values must be within interval MULTIPLIER_RANGE.\
"""
SET_COOL_MULTIPLIER_DOC="""\
Set the controller's cool side multiplier. Numerical
multiplier used to compensate for the nonsymmetrial response,
between heat and cool modes, of the thermoelectric cooler.

Values must be within interval MULTIPLIER_RANGE.        
"""
GET_OVER_CURRENT_COMPARE_DOC="""\
Return the controller's over current compare value in
Amps. This is the value which determines an over-current
condition - the level at which over current protection for the
device shuts the output off. \
"""
SET_OVER_CURRENT_COMPARE_DOC="""\
Set the controller's over current compare value in
Amps. This is the value which determines an over-current
condition - the level at which over current protection for the
device shuts the output off.  \      
"""
GET_ALARM_LATCH_DOC="""\
Return alarm latch setting. Allowed values 'on' or 'off'.\
"""
SET_ALARM_LATCH_DOC="""\
Set the alarm latch. Allowed values 'on' or 'off'.\
"""
SET_ALARM_LATCH_RESET_DOC="""\
Reset the controllers alarm latches
"""
GET_ALARM_SENSOR_DOC="""\
Return the current alarm sensor setting. Allowed values 'input1' and 
'input2'\
"""
SET_ALARM_SENSOR_DOC="""\
Set the controller's alarm sensor setting. Allowed values 'input1' and 
'input2'\
"""
GET_WORKING_UNITS_DOC="""\
Return the controller's current working units. Allowed values 'F' or 'C'.\
"""
SET_WORKING_UNITS_DOC="""\
Return the controller's current working. Allowed values 'F' or 'C'.\
"""
GET_EEPROM_WRITE_DOC="""\
Return the controller's eeprom write setting. Allowed values 'on' 
or 'off'.

If the eeprom write setting is 'on' then all write will be stored to 
both ram and eeprom.\ 
"""
SET_EEPROM_WRITE_DOC="""\
Return the controller's eeprom write setting. Allowed values 'on' 
or 'off'.

If the eeprom write setting is 'on' then all write will be stored to 
both ram and eeprom.\ 
"""
GET_OVER_CURRENT_RESTART_TYPE_DOC="""\
Return the controller's over current restart setting. Allowed values
'continuous' an 'max attempt'.
"""
SET_OVER_CURRENT_RESTART_TYPE_DOC="""\
Return the controller's over current restart setting. Allowed values
'continuous' an 'max attempt'.
"""
GET_OVER_CURRENT_RESTART_NUM_DOC="""\
Return the controller's over current restart attempt number. This the 
number of times the controller will atempt to restart the output after 
an  over current condiiton. Values should within the intereval 
RESTART_ATTEMPT_RANGE \
"""
SET_OVER_CURRENT_RESTART_NUM_DOC="""\
Set the controller's over current restart attempt number. This the 
number of times the controller will atempt to restart the output after 
an  over current condiiton. Values should within the intereval 
RESTART_ATTEMPT_RANGE \
"""
GET_JP3_DISPLAY_DOC="""\
Return the controller's JP3 display enable setting. Allowed values
'on' or 'off'\
"""
SET_JP3_DISPLAY_DOC="""\
Set the controller's JP3 display enable setting. Allowed values
'on' or 'off'\
"""

# Utility functions 
def int2dec(x):
    """
    Convert tc3625 fixed temperature number to decimal number
    """
    return x/100.0

def dec2int(x):
    """
    Convert decimal number to tc3625 fixed temperature number
    """
    return int(100*x)

def int2perc(x):
    """
    Convert tc3625 integer value to percentage - used for power
    functions.
    """
    power_max_int = dec2int(POWER_RANGE[1])
    return 100.0*x/float(power_max_int)

def amp2cnt(x):
    """
    Convert amps to counts
    """
    return x/AMPS_PER_COUNT
    

def cnt2amp(x):
    """
    Convert counts to amps
    """
    return x*AMPS_PER_COUNT


# Classes implementing get and set methods for tc3625 device interface
class Get_Type:
    def __init__(self,type,doc_str=None,warning=None):
        self.type=type
        self.itype=dict([[v,k] for k,v in type.items()])
        self.__doc__=doc_str
        self.warning=warning
        self.cmd=None
        self.call_name=None
        self.parent=None

    def __call__(self):
        if self.warning != None:
            print self.warning
        val =self.parent._get_value(self.cmd)
        try:
            val_str = self.itype[val]
        except KeyError:
            raise IOError, 'unknown type %d from %s'%(val, self.call_name,)       
        return val_str

class Get_Mask:
    def __init__(self,maskdict,doc_str=None,warning=None):
        self.maskdict=maskdict
        self.__doc__=doc_str
        self.warning=warning
        self.cmd=None
        self.call_name=None
        self.parent=None
        
    def __call__(self):
        if self.warning != None:
            print self.warning
        val =self.parent._get_value(self.cmd)
        flag, val_list = False, []
        for k in self.maskdict:
            bit = self.maskdict[k]
            if (1<<bit)&val != 0:
                flag=True
                val_list.append(k)
        return flag,val_list
            
class Get_Num:
    def __init__(self,convert=None,range=None,doc_str=None,warning=None):
        self.convert=convert
        self.range=range
        self.__doc=doc_str
        self.warning=warning
        self.cmd=None
        self.call_name=None
        self.parent=None

    def __call__(self):
        if self.warning != None:
            print self.warning
        val =self.parent._get_value(self.cmd)
        if self.convert != None:
            val = self.convert(val)
        if self.range!=None:
            minval, maxval = self.range
            if val < minval or val > maxval:
                raise IOError, 'value %s out of range from %s'%(str(val),self.call_name,)
        return val
              
class Set_Type:
    def __init__(self,type,doc_str=None,warning=None):
        self.type=type
        self.__doc__=doc_str
        self.warning=warning
        self.cmd=None
        self.call_name=None
        self.parent=None

    def __call__(self,val):
        if self.warning != None:
            print self.warning

        try:
            val_int = self.type[val]
        except KeyError:
            raise ValueError, 'unknown type %s for %s'%(str(val), self.call_name,)
        
        self.parent._set_value(self.cmd,val_int)

class Set_Num:
    def __init__(self,convert=None,range=None,doc_str=None,warning=None):
        self.convert=convert
        self.range=range
        self.__doc__=doc_str
        self.warning=warning
        self.cmd=None
        self.call_name=None
        self.parent=None

    def __call__(self,val):
         if self.warning != None:
            print self.warning
         if self.range!=None:
             minval, maxval = self.range
             if val < minval or val > maxval:
                 raise IOError, 'value %s out of range from %s'%(str(val),self.call_name,)
         if self.convert!=None:
             val = self.convert(val)
         self.parent._set_value(self.cmd,val)

class Set_NoArg:
    def __init__(self,doc_str=None,warning=None):
        self.__doc__=doc_str
        self.warning=warning
        self.cmd=None
        self.call_name=None
        self.parent=None

    def __call__(self):
        if self.warning != None:
            print self.warning
        self.parent._set_value(self.cmd,0)
        
       
METHOD_DICT = {
    'input1':{
        'get':Get_Num(
            convert=int2dec,
            doc_str=GET_INPUT1_DOC
            ),
        'cmd': 'input1',
        }, 
    'input2':{
        'get':Get_Num(
            convert=int2dec,
            doc_str=GET_INPUT1_DOC
            ),
        'cmd': 'input2',
        },
    'control value':{
         'get':Get_Num(
            convert=int2dec,
            doc_str=GET_CONTROL_VALUE_DOC
            ),
         'cmd':'desired control value',
        },
    'power output':{
        'get':Get_Num(
            convert=int2perc,
            doc_str=GET_POWER_OUTPUT_DOC
            ),
        'cmd':'power output',
        },
    'alarm status':{
        'get':Get_Mask(
            ALARM_VALUES,
            doc_str=GET_ALARM_STATUS_DOC
            ),
        'cmd':'alarm status',
        },
    'output current':{
        'get':Get_Num(
            convert=cnt2amp,
            doc_str=GET_OUTPUT_CURRENT_DOC
            ),
        'cmd':'output current counts',
        },
    'alarm type':{
        'get':Get_Type(
            ALARM_TYPES,
            doc_str=GET_ALARM_TYPE_DOC
            ),
        'set':Set_Type(
            ALARM_TYPES,
            doc_str=SET_ALARM_TYPE_DOC
            ),
        'cmd':'alarm type',
        },
    'setpt type':{
        'get':Get_Type(
            SETPT_TYPES,
            doc_str=GET_SETPT_TYPE_DOC
            ),
        'set':Set_Type(
            SETPT_TYPES,
            doc_str=SET_SETPT_TYPE_DOC
            ),
        'cmd':'set type define',
        },
    'sensor type':{
        'get':Get_Type(
            SENSOR_TYPES,
            doc_str=GET_SENSOR_TYPE_DOC
            ),
        'set':Set_Type(
            SENSOR_TYPES,
            doc_str=SET_SENSOR_TYPE_DOC
            ),
        'cmd':'sensor type',
        },
    'control type':{
        'get':Get_Type(
            CONTROL_TYPES,
            doc_str=GET_CONTROL_TYPE_DOC
            ),
        'set':Set_Type(
            type=CONTROL_TYPES,
            doc_str=SET_CONTROL_TYPE_DOC
            ),
        'cmd':'control type',
        },
    'output polarity':{
        'get':Get_Type(
            OUTPUT_POLARITY_TYPES,
            doc_str=GET_OUTPUT_POLARITY_DOC
            ),
        'set':Set_Type(
            OUTPUT_POLARITY_TYPES,
            doc_str=SET_OUTPUT_POLARITY_DOC
            ),
        'cmd':'control output polarity',
        },
    'power state': {
        'get':Get_Type(
            ON_OFF_TYPES,
            doc_str=GET_POWER_STATE_DOC
            ),
        'set':Set_Type(
            ON_OFF_TYPES,
            doc_str=SET_POWER_STATE_DOC
            ),
        'cmd':'power on/off',
        },
    'shutdown if alarm': {
        'get':Get_Type(
            ON_OFF_TYPES,
            doc_str=GET_SHUTDOWN_IF_ALARM_DOC
            ),
        'set':Set_Type(
            ON_OFF_TYPES,
            doc_str=SET_SHUTDOWN_IF_ALARM_DOC
            ),
        'cmd':'output shutdown if alarm',
        },
    'fixed control setting':{
        'get':Get_Num(
            convert=int2dec,
            doc_str=GET_FIXED_CONTROL_SETTING_DOC
            ),
        'set':Set_Num(
            convert=dec2int,
            doc_str=SET_FIXED_CONTROL_SETTING_DOC
            ),
        'cmd':'fixed desired control setting',
        },
    'setpt':{
        'get':Get_Num(
            convert=int2dec,
            doc_str=GET_SETPT_DOC
            ),
        'set':Set_Num(
            convert=dec2int,
            doc_str=SET_SETPT_DOC
            ),
        'cmd':'fixed desired control setting',
        },
    'proportional bandwidth':{
        'get':Get_Num(
            convert=int2dec,
            range=PROPORTIONAL_BANDWIDTH_RANGE,
            doc_str=GET_PROPORTIONAL_BANDWIDTH_DOC
            ),
        'set':Set_Num(
            convert=dec2int,
            range=PROPORTIONAL_BANDWIDTH_RANGE,
            doc_str=SET_PROPORTIONAL_BANDWIDTH_DOC
            ),
        'cmd':'proportional bandwidth',
        },
    'integral gain':{
        'get':Get_Num(
            convert=int2dec,
            range=INTEGRAL_GAIN_RANGE,
            doc_str=GET_INTEGRAL_GAIN_DOC
            ),
        'set':Set_Num(
            convert=dec2int,
            range=INTEGRAL_GAIN_RANGE,
            doc_str=SET_INTEGRAL_GAIN_DOC
            ),
        'cmd':'integral gain',
        },
    'derivative gain':{
        'get':Get_Num(
            convert=int2dec,
            range=DERIVATIVE_GAIN_RANGE,
            doc_str=GET_DERIVATIVE_GAIN_DOC
            ),
        'set':Set_Num(
            convert=dec2int,
            range=DERIVATIVE_GAIN_RANGE,
            doc_str=GET_DERIVATIVE_GAIN_DOC
            ),
        'cmd':'derivative gain',
        },
    'low external set range':{
        'get':Get_Num(
            convert=int2dec,
            doc_str=GET_LOW_EXTERNAL_SET_RANGE_DOC
            ),
        'set':Set_Num(
            convert=dec2int,
            doc_str=SET_LOW_EXTERNAL_SET_RANGE_DOC
            ),
        'cmd':'low external set range',
        },
    'high external set range':{
        'get':Get_Num(
            convert=int2dec,
            doc_str=GET_HIGH_EXTERNAL_SET_RANGE_DOC
            ),
        'set':Set_Num(
            convert=dec2int,
            doc_str=SET_HIGH_EXTERNAL_SET_RANGE_DOC
            ),
        'cmd':'high external set range',
        },
    'alarm deadband':{
        'get':Get_Num(
            convert=int2dec,
            doc_str=GET_ALARM_DEADBAND_DOC
            ),
        'set':Set_Num(
            convert=dec2int,
            doc_str=SET_ALARM_DEADBAND_DOC
            ),
        'cmd':'alarm deadband',
        },
    'high alarm':{
        'get':Get_Num(
            convert=int2dec,
            doc_str=GET_HIGH_ALARM_DOC,
            ),
        'set':Set_Num(
            convert=dec2int,
            doc_str=SET_HIGH_ALARM_DOC
            ),
        'cmd':'high alarm setting',
        },
    'low alarm':{
        'get':Get_Num(
            convert=int2dec,
            doc_str=GET_LOW_ALARM_DOC,
            ),
        'set':Set_Num(
            convert=dec2int,
            doc_str=SET_LOW_ALARM_DOC,
            ),
        'cmd':'low alarm setting',
        },
    'control deadband':{
        'get':Get_Num(
            convert=int2dec,
            doc_str=GET_CONTROL_DEADBAND_DOC,
            ),
        'set':Set_Num(
            convert=dec2int,
            doc_str=SET_CONTROL_DEADBAND_DOC,
            ),
        'cmd':'control deadband setting',
        },
    'input1 offset':{
        'get':Get_Num(
            convert=int2dec,
            doc_str=GET_INPUT1_OFFSET_DOC,
            ),
        'set':Set_Num(
            convert=dec2int,
            doc_str=SET_INPUT1_OFFSET_DOC,
            ),
        'cmd':'input1 offset',
        },
    'input2 offset':{
        'get':Get_Num(
            convert=int2dec,
            doc_str=GET_INPUT2_OFFSET_DOC,
            ),
        'set':Set_Num(
            convert=dec2int,
            doc_str=SET_INPUT2_OFFSET_DOC,
            ),
        'cmd':'input2 offset',
        },
    'heat multiplier':{
        'get':Get_Num(
            convert=int2dec,
            range=MULTIPLIER_RANGE,
            doc_str=GET_HEAT_MULTIPLIER_DOC,
            ),
        'set':Set_Num(
            convert=dec2int,
            range=MULTIPLIER_RANGE,
            doc_str=SET_HEAT_MULTIPLIER_DOC,
            ),
        'cmd':'heat multiplier',
        },
    'cool multiplier':{
        'get':Get_Num(
            convert=int2dec,
            range=MULTIPLIER_RANGE,
            doc_str=GET_COOL_MULTIPLIER_DOC,
            ),
        'set':Set_Num(
            convert=dec2int,
            range=MULTIPLIER_RANGE,
            doc_str=SET_COOL_MULTIPLIER_DOC,
            ),
        'cmd':'cool multiplier',
        },
    'over current compare':{
        'get':Get_Num(
            convert=cnt2amp,
            range=OVER_CURRENT_RANGE,
            doc_str=GET_OVER_CURRENT_COMPARE_DOC,
            ),
        'set':Set_Num(
            convert=amp2cnt,
            range=OVER_CURRENT_RANGE,
            doc_str=SET_OVER_CURRENT_COMPARE_DOC,
            ),
        'cmd':'over current count compare value',
        },
    'alarm latch':{
        'get':Get_Type(
            ON_OFF_TYPES,
            doc_str=GET_ALARM_LATCH_DOC,
            ),
        'set':Set_Type(
            ON_OFF_TYPES,
            doc_str=SET_ALARM_LATCH_DOC,
            ),
        'cmd':'alarm latch enable',
        },
    'alarm latch reset':{
        'set':Set_NoArg(
            warning='(alarm latch reset) warning - not sure if this is correct',
            doc_str=SET_ALARM_LATCH_RESET_DOC,
            ),
        'cmd':'alarm latch request',
        },
    'alarm sensor':{
        'get':Get_Type(
            ALARM_SENSOR_TYPES,
            doc_str=GET_ALARM_SENSOR_DOC,
            ),
        'set':Set_Type(
            ALARM_SENSOR_TYPES,
            doc_str=SET_ALARM_SENSOR_DOC,
            ),
        'cmd':'choose sensor for alarm function',
        },
    'working units':{
        'get':Get_Type(
            TEMP_TYPES,
            doc_str=GET_WORKING_UNITS_DOC,
            ),
        'set':Set_Type(
            TEMP_TYPES,
            doc_str=SET_WORKING_UNITS_DOC,
            ),
        'cmd':'temperature working units',
        },
    'eeprom write':{
        'get':Get_Type(
            ON_OFF_TYPES,
            doc_str=GET_EEPROM_WRITE_DOC,
            ),
        'set':Set_Type(
            ON_OFF_TYPES,
            doc_str=SET_EEPROM_WRITE_DOC,
            ),
        'cmd':'eeprom write enable',
        },
    'over current restart type':{
        'get':Get_Type(
            RESTART_TYPES,
            doc_str=GET_OVER_CURRENT_RESTART_TYPE_DOC,
            ),
        'set':Set_Type(
            RESTART_TYPES,
            doc_str=SET_OVER_CURRENT_RESTART_TYPE_DOC,
            ),
        'cmd':'over current continuous',
        },
    'over current restart num':{
        'get':Get_Num(
            convert=int2dec,
            range=RESTART_ATTEMPT_RANGE,
            doc_str=GET_OVER_CURRENT_RESTART_NUM_DOC,
            ),
        'set':Set_Num(
            convert=dec2int,
            range=RESTART_ATTEMPT_RANGE,
            doc_str=SET_OVER_CURRENT_RESTART_NUM_DOC,
            ),
        'cmd':'over current restart attempts',
        },
    'JP3 display':{
        'get':Get_Type(
            ON_OFF_TYPES,
            doc_str=GET_JP3_DISPLAY_DOC,
            ),
        'set':Set_Type(
            ON_OFF_TYPES,
            doc_str=SET_JP3_DISPLAY_DOC,
            ),
        'cmd':'JP3 display enable',
        },    
}

class TC3625:
    """
    High level python API for the TC-36-25 thermoelectric cooler
    temperature contollers.
    """
    def __init__(self, 
                 port=DFLT_PORT, 
                 timeout=DFLT_TIMEOUT,
                 baudrate=DFLT_BAUDRATE,
                 max_attempt=DFLT_MAX_ATTEMPT,
                 open=True,
                 eeprom='off',
                 ):
        self.port=port
        self.timeout=timeout
        self.baudrate=baudrate
        self.max_attempt=max_attempt 
        # Open serial connection
        if open==True:
            flag = self.open()
            if flag==False:
                raise IOError, 'unable to open device'
      
        # Generate methods
        self.method_dict=METHOD_DICT
        for meth_str in self.method_dict:
            meth_stub = ''
            for s in meth_str.split():
                meth_stub += '_%s'%(s,)
            cmd = self.method_dict[meth_str]['cmd']
            get_str = 'get' + meth_stub
            set_str = 'set' + meth_stub 
            try:
                get_method = self.method_dict[meth_str]['get']
                get_method.cmd = cmd
                get_method.call_name = get_str
                get_method.parent = self
                setattr(self,get_str,get_method)
            except:
                pass
            try: 
                set_method = self.method_dict[meth_str]['set']
                set_method.cmd = cmd
                set_method.parent = self
                set_method.call_name = set_str
                setattr(self,set_str,set_method)
            except:
                pass

        if eeprom=='off':
            self.set_eeprom_write('off')

    def set_by_dict(self,prop_new):
        """
        Set deivce properties using dictionary
        """
        method_keys = self.method_dict.keys()
        for k in prop_new.keys():
            if not k in method_keys:
                raise ValueError, 'unknown property %s'%(k,)
            self.set(k,prop_new[k])

    def set(self,prop_str,val):
        """
        Set device property by name value pair
        """
        if not prop_str in self.method_dict.keys():
            raise ValueError, 'unknown property %s'%(str(prop_str),)
        try:
            set_method = self.method_dict[prop_str]['set']
        except KeyError:
            raise ValueError, 'unsettable property %s'%(str(prop_str,))
        set_method(val)
            
    def get_all(self):
        """
        Get all device properties
        """
        prop={}
        for k in self.method_dict:
            try:
                get_method = self.method_dict[k]['get']
            except:
                continue
            prop[k]=get_method()
        return prop

    def print_all(self):
        """
        Print all device properties
        """
        prop = self.get_all()
        prop_keys = prop.keys()
        prop_keys.sort()
        for k in prop_keys:
            print '%s: %s'%(k, prop[k])

    def open(self):
        """ 
        Open serial connection to device. Note, by defualt the serial
        connection to the device is automatically open on
        initialization.
        """
        self.dev = TC3625_Serial(port=self.port)
        flag = self.dev.open()
        return flag
        
    def close(self):
        """ Close serial conection to device """
        self.dev.close()


    def _get_value(self,cmd): 
        """ 
        Generic get commmand - tries max_attempt times to read value
        from device using low level serial protocol.
        """
        cnt=0
        while cnt < self.max_attempt:
            try:
                val = self.dev.read(cmd)
                break
            except IOError:
                print '** warning IOError on read'
                pass
            cnt+=1
        if cnt==self.max_attempt:
            raise IOError, 'max attempts reached for read'
        return val
                
    def _set_value(self,cmd,val):
        """
        Generic set command - tries max_attempt times to set device
        value using low level serial protocol.
        """
        cnt=0
        while cnt < self.max_attempt:
            try:
                val = self.dev.write(cmd,val)
                break
            except IOError:
                print '** warning IOError on write'
                pass
            cnt+=1
        if cnt==self.max_attempt:
            raise IOError, 'max attempts reached for write'
        return val

# --------------------------------------------------------------------



