#Version 1.3 last updated 19-Jul-18

import serial
import time

pname = 'COM3'
ser = serial.Serial(port=pname,baudrate=57600,parity='O',bytesize=7,timeout=1)
sleeptime = 10

def query(string):
    '''
    Asks for data then returns the response
    '''
    if model == 'MODEL330':
        ser.write(string + '\n')
        time.sleep(0.5)
        read = ser.readline()
        while ser.inWaiting() != 0:
            ser.readline()
        return read
    if model == 'MODEL336':
        ser.write(string + '\n')
        return ser.readline()

def query_model():
    '''
    Returns the model number, nnn controller will return 'MODELnnn'. 
    Command works the same for all models.
    '''
    ser.write('*IDN?\n')
    rstr = ser.readline()
    while ser.inWaiting() != 0:
        ser.readline()
    if rstr == '' or rstr == None:
        print 'Temperature Controller not connected. Check the connection and try again'
        time.sleep(5)
        return
    rlist = rstr.split(',')
    model = rlist[1]
    return model

def set_setpoint(temperature, loop='1'):
    '''
    Gives the controller the desired temperature
    330: INPUT: SETP[set point]
    340: INPUT: SETP <loop>,<value>
    336: INPUT: SETP <output>,<value>
    Loop and output are the same thing: the temperature
    '''
    if model == 'MODEL330':
        temperature = round(float(temperature),2)
        ser.write('SETP' + str(temperature) + '\n')
    if model == 'MODEL340' or model == 'MODEL336':
        temperature = round(float(temperature),3)
        ser.write('SETP ' + str(loop) + ', ' + str(temperature) + '\n')

def query_setpoint(loop='1'):
    '''
    Returns the previous desired temperature
    330: INPUT: SETP?
         RETURN: <value>
    340: INPUT SETP? <loop>
         RETURN: <value>
    336: INPUT SETP? <output>
         RETURN: <value>
    Loop and output are the same thing
    '''
    if model == 'MODEL330':
        rstr = query('SETP? ')
        rstr = rstr[0:len(rstr)-2]
        return rstr
    elif model == 'MODEL340' or model == 'MODEL336':
        rstr = query('SETP? ' + str(loop))
        rstr = rstr[0:len(rstr)-2]
        return rstr

def query_heat(output='1'):
    '''
    Returns a heater output in percentage.
    330: INPUT: HEAT?
         RETURN: <heater value> #increments of 5%
    340: INPUT: HTR?
         RETURN: <heater value>
    336: INPUT:HTR? <output>
         RETURN: <heater value>
    '''
    if model == 'MODEL330':
        rstr = query('HEAT? ')
        rstr = rstr[0:len(rstr)-2]
        return rstr
    elif model == 'MODEL340' or model == 'MODEL336':
        rstr = query('HTR? ' + output)
        rstr = rstr[0:len(rstr)-2]
        return rstr

def set_heater_range(value_range, output='1'):
    '''
    Sets the range of the heater
    Value_range must be 0,1,2,3, or 5.
    330: INPUT: RANGE[heater range]
    0 is off, 1 is low, 2 is medium, 3 is high
    340: INPUT: RANGE <range>
    0 is off; 1 is 2.5mW; 2 is 25mW; 3 is 250mW; 4 is 2.5W; 5 is 25W
    336: INPUT: RANGE <output>,<range>
    For output 1: 0 is off; 1 is 0.1W; 2 is 10W; 3 is 100W
    For output 2: 0 is off; 1 is 0.5W; 2 is 5W; 3 is 50W
    '''
    if model == 'MODEL330':
        ser.write('RANG' + value_range + '\n')
    elif model == 'MODEL340' or model == 'MODEL336':
        ser.write('RANGE ' + output + ',' + value_range + '\n')

def query_heater_range(output='1'):
    '''
    Returns the heater range.
    330: INPUT: RANG?
         RETURN: <range>
    340: INPUT: RANGE?
         RETURN: <range>
    336: INPUT: RANGE? <output>
         RETURN: <range>
    '''
    if model == 'MODEL330':
        rstr = query('RANG?')
        rstr = rstr[0:len(rstr)-2]
        return rstr
    elif model == 'MODEL340' or model == 'MODEL336':
        rstr = query('RANGE? ' + output)
        rstr = rstr[0:len(rstr)-2]
        return rstr

def set_alarm(value_channel, on_off, value_high, value_low):
    '''
    Configures the alarm. If the temperature measured goes
    out of the high/low range, an alarm will be triggered. 
    Possible Value Channels are 'A' or 'B'.
    330: N/A
    340: INPUT: ALARM <input>, <off/on>, <source>, <high value>, <low value>, <latch enable>, <relay>
    336: INPUT: ALARM <input>,<off/on>,<high value>,<low value>,<deadband>,<latch enable>,<audible>,<visible>
    '''
    if model == 'MODEL340':
        ser.write('ALARM ' + value_channel.upper() + ', ' + on_off + ', 1, ' + 
                  value_high + ', ' + value_low + '0,0\n')
    elif model == 'MODEL336':
        ser.write('ALARM ' + value_channel.upper() + ',' + on_off + ',' + 
                  value_high + ',' + value_low + ',0,0,0,1\n')
    
def query_alarm(value_channel):
    '''
    Returns a list of the alarm configeration
    Options of value channels are A/B
    330: N/A
    340: INPUT: ALARM? <input>
         RETURN: <off/on>, <source>, <high value>, <low value>, <latch enable>, <relay enable>
    336: INPUT: ALARM? <input>
         RETURN: <off/on>,<high value>,<low value>,<deadband>,<latch enable>,<audible>,<visible>
    '''
    if model == 'MODEL340':
        rstr = query('ALARM? ' + value_channel)
        rlisttemp = rstr.split(',')
        rlisttemp[2] = rlisttemp[2][1:(len(rlisttemp[2])-2)]
        rlisttemp[3] = rlisttemp[3][1:(len(rlisttemp[3])-2)]
        #item 0 is off/on; 1 is source; 2 is high value; 3 is low value; 
        #4 is latch enable; 5 is relay enable.
        #Create new list that has the parameters in the same 
        #order as the 336 list
        rlist = [rlisttemp[0],rlisttemp[2],rlisttemp[3]]
        return rlist
    elif model == 'MODEL336':
        rstr = query('ALARM? ' + value_channel)
        rlist = rstr.split(',')
        rlist[-1] = rlist[-1][0:len(rlist[-1])-2]
        #item 0 is off/on; 1 is high value, 2 is low value; 3 is deadband; 
        #4 is latch anable; 5 is audible; 6 is visible        
        return rlist

def query_alarm_status(value_channel):
    '''
    Queries the status of the alarm.
    330: N/A
    340: INPUT: ALARMST? <input>
         RETURN: <high status>,<low status>
    336: INPUT: ALARMST? <value_channel>
         RETURN: <high state>,<low state>
    0 = off, 1 = on
    '''
    if (model == 'MODEL340' or model == 'MODEL336'):
        rstr = query('ALARMST? ' + value_channel)
        rlist = rstr.split(',')
        rlist[-1] = rlist[-1][0:len(rlist[-1])-2]
        #item 0 is high state; 1 is low state
        return rlist

def query_temp(sensor):
    '''
    Reads the current temperature in Kelvin
    330: INPUT: CDAT? OR SDAT?
         RETURN: <temperature>
    340: INPUT: KRDG? <input>
         RETURN: <temperature>
    336: INPUT: KRDG? <sensor (A/B)>
         RETURN: <temperature>
    '''
    if model == 'MODEL330':
        if sensor == 'A':
            rstr = query('SDAT? ')
        if sensor == 'B':
            rstr = query('CDAT? ')
        rstr = rstr[0:len(rstr)-2]
        return rstr
    elif model == 'MODEL340' or model == 'MODEL336':
        rstr = query('KRDG? ' + sensor)
        rstr = rstr[0:len(rstr)-2]
        return rstr

#Drain the serial incase there is anything there from the previous time program was run
while ser.inWaiting() != 0:
    ser.readline()

#Determine model so the right commands are used
model = query_model()
time.sleep(0.5)

if model == 'MODEL330':
    inputfile = 'textinput330.txt'
elif model == 'MODEL340':
    inputfile = 'textinput340.txt'
elif model == 'MODEL336':
    inputfile = 'textinput336.txt'

if model == 'MODEL330':
    delaytime = 0.5
    #Query the current state and create variables
    rsetpoint = query_setpoint()
    time.sleep(delaytime)
    rheater_range = query_heater_range()
    time.sleep(delaytime)
    #Set the units to kelvin
    ser.write('CUNI K\n')
    time.sleep(delaytime)
    ser.write('SUNY K\n')
    time.sleep(delaytime)
    #Create a file including the read data
    ftemp = open(inputfile, 'w')
    writestring=(
        'Target Temperature in Kelvin (do not include units):\n' +
        rsetpoint + 
        '\nHeater Range 1 (0-5). (0 is off. 1 is LOW. 2 is MED. 3 is HIGH:\n' +
        rheater_range
        )
    ftemp.write(writestring)
    ftemp.close()
elif model == 'MODEL340' or model == 'MODEL336':
    delaytime = 0.1
    #Query the current state and create variables
    ralarm_A_list = query_alarm('A')
    roff_on_A = ralarm_A_list[0]
    rhigh_value_A = ralarm_A_list[1]
    rlow_value_A = ralarm_A_list[2]
    time.sleep(delaytime)
    ralarm_B_list = query_alarm('B')
    roff_on_B = ralarm_B_list[0]
    rhigh_value_B = ralarm_B_list[1]
    rlow_value_B = ralarm_B_list[2]
    time.sleep(delaytime)
    rsetpoint = query_setpoint('1')
    time.sleep(delaytime)
    rsetpoint2 = query_setpoint('2')
    time.sleep(delaytime)
    rheater_range = query_heater_range('1')
    time.sleep(delaytime)
    rheater_range2 = query_heater_range('2')
    time.sleep(delaytime)
    #Create a file including the read data
    ftemp = open(inputfile, 'w')
    if model == 'MODEL340':    
        writestring = (
            'Target Temperature Loop 1 in Kelvin (do not include units):\n' +
            rsetpoint +
            '\nTarget Temperature Loop 2 in Kelvin (do not include units):\n' +
            rsetpoint2 +
            '\nHeater Range #1 (0-5) (0 is off. 1 is 2.5mW. 2 is 25mW. 3 is 250mW. 4 is 2.5W. 5 is 25W.):\n' +
            rheater_range +
            '\nHeater Range #2 (0-5) (0 is off. 1 is 2.5mW. 2 is 25mW. 3 is 250mW. 4 is 2.5W. 5 is 25W.):\n' +
            rheater_range2 +
            '\n\nMin Temperature in Kelvin (A) (do not include units):\n' +
            rlow_value_A +
            '\nMax Temperature in Kelvin (A) (do not include units):\n' +
            rhigh_value_A +
            '\nAlarm On/Off (A) (set to 1 to turn on. Set to 0 to turn off):\n' +
            roff_on_A +
            '\n\nMin Temperature in Kelvin (B) (do not include units):\n' +
            rlow_value_B +
            '\nMax Temperature in Kelvin (B) (do not include units):\n' +
            rhigh_value_B +
            '\nAlarm On/Off (B) (set to 1 to turn on. Set to 0 to turn off):\n' +
            roff_on_B
            )
    if model == 'MODEL336':
        writestring = (
            'Target Temperature Loop 1 in Kelvin (do not include units):\n' +
            rsetpoint +
            '\nTarget Temperature Loop 2 in Kelvin (do not include units):\n' +
            rsetpoint2 +
            '\nHeater Range #1 (0-3) (0 is off. 1 is 1W. 2 is 10W. 3 is 100W.):\n' +
            rheater_range +
            '\nHeater Range #2 (0-3) (0 is off. 1 is 0.5W. 2 is 5W. 3 is 50.):\n' +
            rheater_range2 +
            '\n\nMin Temperature in Kelvin (A) (do not include units):\n' +
            rlow_value_A +
            '\nMax Temperature in Kelvin (A) (do not include units):\n' +
            rhigh_value_A +
            '\nAlarm On/Off (A) (set to 1 to turn on. Set to 0 to turn off):\n' +
            roff_on_A +
            '\n\nMin Temperature in Kelvin (B) (do not include units):\n' +
            rlow_value_B +
            '\nMax Temperature in Kelvin (B) (do not include units):\n' +
            rhigh_value_B +
            '\nAlarm On/Off (B) (set to 1 to turn on. Set to 0 to turn off):\n' +
            roff_on_B
            )
    ftemp.write(writestring)
    ftemp.close()

while True:
    #Read the textfile for information
    ftemp = open(inputfile, 'r')
    ilines = ftemp.readlines()
    ftemp.close()
    
    #Create variables from the textfile for future comparison
    isetpoint = ilines[1].rstrip()
    if not isetpoint.replace('.','',1).replace('+','',1).isdigit():
        print 'Error in text input file'
        print 'Error: Target Temperature in Loop 1 input is not in the correct format.'
        time.sleep(5)
        break
    if model == 'MODEL330':
        isetpoint = str(round(float(isetpoint),2))
    if model == 'MODEL340' or model == 'MODEL336':
        isetpoint = str(round(float(isetpoint),3))
    
    if model == 'MODEL340' or model == 'MODEL336': #MODEL330 only has one setpoint option
        isetpoint2 = ilines[3].rstrip()
        if not isetpoint2.replace('.','',1).replace('+','',1).isdigit():
            print 'Error in text input file'
            print 'Error: Target Temperature in Loop 2 input is not in the correct format.'
            time.sleep(5)
            break
        isetpoint2 = str(round(float(isetpoint2),3))
    
    if model == 'MODEL330':
        iheater_range = ilines[3].rstrip()
        if (iheater_range != '0' and iheater_range != '1' and 
            iheater_range != '2' and iheater_range != '3'):
            print 'Error in text input file'
            print 'Error: Heater Range 1 input is not in the correct format.'
            time.sleep(5)
            break
    elif model == 'MODEL340' or model == 'MODEL336':
        iheater_range = ilines[5].rstrip()
        if (iheater_range != '0' and iheater_range != '1' and 
            iheater_range != '2' and iheater_range != '3' and 
            iheater_range != '5' and iheater_range != '5'):
            print 'Error in text input file'
            print 'Error: Heater Range 1 input is not in the correct format.'
            time.sleep(5)
            break
    elif model == 'MODEL336':
        iheater_range = ilines[5].rstrip()
        if (iheater_range != '0' and iheater_range != '1' and 
            iheater_range != '2' and iheater_range != '3'):
            print 'Error in text input file'
            print 'Error: Heater Range 1 input is not in the correct format.'
            time.sleep(5)
            break
    
    if model == 'MODEL340': #MODEL330 has only one heater range and no alarms
        iheater_range2 = ilines[7].rstrip()
        if (iheater_range2 != '0' and iheater_range2 != '1' and 
            iheater_range2 != '2' and iheater_range2 != '3' and 
            iheater_range2 != '5' and iheater_range2 != '5'):
            print 'Error in text input file'
            print 'Error: Heater Range 2 input is not in the correct format.'
            time.sleep(5)
            break
    elif model == 'MODEL336':
        iheater_range2 = ilines[7].rstrip()
        if (iheater_range2 != '0' and iheater_range2 != '1' and
            iheater_range2 != '2' and iheater_range2 != '3'):
            print 'Error in text input file'
            print 'Error: Heater Range 2 input is not in the correct format.'
            time.sleep(5)
            break
    
        ilow_value_A = ilines[10].rstrip()
        if not ilow_value_A.replace('.','',1).replace('+','',1).isdigit():
            print 'Error in text input file'
            print 'Error: Alarm A min input is not in the correct format.'
            time.sleep(5)
            break
        if model == 'MODEL340':
            ilow_value_A = str(round(float(ilow_value_A),3))
        if model == 'MODEL336':
            ilow_value_A = str(round(float(ilow_value_A),4))
        
        ihigh_value_A = ilines[12].rstrip()
        if not isetpoint2.replace('.','',1).replace('+','',1).isdigit():
            print 'Error in text input file'
            print 'Error: Alarm A max input is not in the correct format.'
            time.sleep(5)
            break
        if model == 'MODEL340':
            ihigh_value_A = str(round(float(ihigh_value_A),3))
        if model == 'MODEL336':
            ihigh_value_A = str(round(float(ihigh_value_A),4))
    
        ioff_on_A = ilines[14].rstrip()
        if (ioff_on_A != '0' and ioff_on_A != '1'):
            print 'Error in text input file'
            print 'Error: Alarm A on/off input is not in the correct format.'
            time.sleep(5)
            break
    
        ilow_value_B = ilines[17].rstrip()
        if not ilow_value_B.replace('.','',1).replace('+','',1).isdigit():
            print 'Error in text input file'
            print 'Error: Alarm B min input is not in the correct format.'
            time.sleep(5)
            break
        if model == 'MODEL340':
            ilow_value_B = str(round(float(ilow_value_B),3))
        if model == 'MODEL336':
            ilow_value_B = str(round(float(ilow_value_B),4))
    
        ihigh_value_B = ilines[19].rstrip()
        if not ihigh_value_B.replace('.','',1).replace('+','',1).isdigit():
            print 'Error in text input file'
            print 'Error: Alarm B max input is not in the correct format.'
            time.sleep(5)
            break
        if model == 'MODEL340':
            ihigh_value_B = str(round(float(ihigh_value_B),3))
        if model == 'MODEL336':
            ihigh_value_B = str(round(float(ihigh_value_B),4))
    
        ioff_on_B = ilines[21].rstrip()
        if (ioff_on_B != '0' and ioff_on_B != '1'):
            print 'Error in text input file'
            print 'Error: Alarm B on/off input is not in the correct format.'
            time.sleep(5)
            break
    
    #Check for differences in the textfile, apply difference if there
    #is, and check that the differences were recieved and reapply if
    #unrecieved (up to twice per cycle to prevent long delays and getting
    #stuck).
    
    if float(isetpoint) != float(rsetpoint):
        set_setpoint(isetpoint, '1')
        time.sleep(delaytime)
        rsetpoint = query_setpoint('1')
        time.sleep(delaytime)
        if float(isetpoint) != float(rsetpoint):
            set_setpoint(isetpoint, '1')
            time.sleep(delaytime)
            rsetpoint = query_setpoint('1')
            time.sleep(delaytime)
            print 'Target Temperature in Loop 1 failed to update. Trying again'
            if isetpoint != rsetpoint:
                print 'Target Temperature in Loop 1 failed to update after 2 attempts. Retrying in 10 seconds.'
            else:
                print 'Successfully updated Target Temperature in Loop 1'
    
    if model == 'MODEL340' or model == 'MODEL336': #MODEL330 only has one setpoint
        if float(isetpoint2) != float(rsetpoint2):
            set_setpoint(isetpoint2, '2')
            time.sleep(delaytime)
            rsetpoint2 = query_setpoint('2')
            time.sleep(delaytime)
            if isetpoint2 != rsetpoint2:
                set_setpoint(isetpoint2, '2')
                time.sleep(delaytime)
                rsetpoint2 = query_setpoint('2')
                time.sleep(delaytime)
                print 'Target Temperature in Loop 2 failed to update. Trying again.'
                if isetpoint2 != rsetpoint2:
                    print 'Target Temperature in Loop 2 failed to update after 2 attempts. Retrying in 10 seconds.'
                else:
                    print 'Successfully updated Target Temperature in Loop 2.'

    if float(iheater_range) != float(rheater_range):
        set_heater_range(iheater_range, '1')
        time.sleep(delaytime)
        rheater_range = query_heater_range('1')
        time.sleep(delaytime)
        if iheater_range != rheater_range:
            set_heater_range(iheater_range, '1')
            time.sleep(delaytime)
            rheater_range = query_heater_range('1')
            time.sleep(delaytime)
            print 'Heater Range 1 failed to update. Trying again.'
            if iheater_range != iheater_range:
                print 'Heater Range 1 failed to update after 2 attempts. Retrying in 10 seconds.'
            else:
                print 'Successfully updated Heater Range 1.'

    if model == 'MODEL340' or model == 'MODEL336':
        if float(iheater_range2) != float(rheater_range2):
            set_heater_range(iheater_range2, '2')
            time.sleep(delaytime)
            rheater_range2 = query_heater_range('2')
            time.sleep(delaytime)
            if iheater_range2 != rheater_range2:
                set_heater_range(iheater_range2, '2')
                time.sleep(delaytime)
                rheater_range2 = query_heater_range('2')
                time.sleep(delaytime)
                print 'Heater Range 2 failed to update. Trying again.'
                if iheater_range2 != iheater_range2:
                    print 'Heater Range 2 failed to update after 2 attempts. Retrying in 10 seconds.'
                else:
                    print 'Successfully updated Heater Range 2.'
    
    if model == 'MODEL340' or model == 'MODEL336': #MODEL330 does not have an alarm
        if (
        float(ilow_value_A) != float(rlow_value_A) or
        float(ihigh_value_A) != float(rhigh_value_A) or
        float(ioff_on_A) != float(roff_on_A)
        ):
            set_alarm('A', ioff_on_A, ihigh_value_A, ilow_value_A)
            time.sleep(delaytime)
            ralarm_A_list = query_alarm('A')
            roff_on_A = ralarm_A_list[0]
            rhigh_value_A = ralarm_A_list[1]
            rlow_value_A = ralarm_A_list[2]
            time.sleep(delaytime)
            if (
            float(ilow_value_A) != float(rlow_value_A) or
            float(ihigh_value_A) != float(rhigh_value_A) or
            float(ioff_on_A) != float(roff_on_A)
            ):
                set_alarm('A', ioff_on_A, ihigh_value_A, ilow_value_A)
                time.sleep(delaytime)
                ralarm_A_list = query_alarm('A')
                roff_on_A = ralarm_A_list[0]
                rhigh_value_A = ralarm_A_list[1]
                rlow_value_A = ralarm_A_list[2]
                time.sleep(delaytime)
                print 'Alarm A failed to update. Trying again.'
                if (
                float(ilow_value_A) != float(rlow_value_A) or
                float(ihigh_value_A) != float(rhigh_value_A) or
                float(ioff_on_A) != float(roff_on_A)
                ):
                    print 'Alarm A failed to update after 2 attempts. Retrying in 10 seconds.'
                else:
                    print 'Successfully updated Alarm A.'
            
        if (
        float(ilow_value_B) != float(rlow_value_B) or
        float(ihigh_value_B) != float(rhigh_value_B) or
        float(ioff_on_B) != float(roff_on_B)
        ):
            set_alarm('B', ioff_on_B, ihigh_value_B, ilow_value_B)
            time.sleep(delaytime)
            ralarm_B_list = query_alarm('B')
            roff_on_B = ralarm_B_list[0]
            rhigh_value_B = ralarm_B_list[1]
            rlow_value_B = ralarm_B_list[2]
            time.sleep(delaytime)
            if (
            float(ilow_value_B) != float(rlow_value_B) or
            float(ihigh_value_B) != float(rhigh_value_B) or
            float(ioff_on_B) != float(roff_on_B)
            ):
                set_alarm('B', ioff_on_B, ihigh_value_B, ilow_value_B)
                time.sleep(delaytime)
                ralarm_B_list = query_alarm('B')
                roff_on_B = ralarm_B_list[0]
                rhigh_value_B = ralarm_B_list[1]
                rlow_value_B = ralarm_B_list[2]
                time.sleep(delaytime)
                print 'Alarm B failed to update. Trying again.'
                if (
                float(ilow_value_B) != float(rlow_value_B) or
                float(ihigh_value_B) != float(rhigh_value_B) or
                float(ioff_on_B) != float(roff_on_B)
                ):
                    print 'Alarm B failed to update after 2 attempts. Retrying in 10 seconds.'
                else:
                    print 'Successfully updated Alarm B.'
    
    #Read the temperature and heater percent
    temp_A = query_temp('A')
    time.sleep(delaytime)
    temp_B = query_temp('B')
    time.sleep(delaytime)    
    heat_percent = query_heat('1')
    time.sleep(delaytime)
    if model == 'MODEL340' or model == 'MODEL336':
        heat_percent2 = query_heat('2')
        time.sleep(delaytime)
    
    #Create a string depending on the value of parameters for the interface
    if model == 'MODEL330':
        if rheater_range == '0':
            hstr = 'Heater is off'
        elif rheater_range == '1':
            hstr = 'Heater: Maximum heater output is LOW'
        elif rheater_range == '2':
            hstr = 'Heater: Maximum heater output is MED'
        elif rheater_range == '3':
            hstr = 'Heater: Maximum heater output is HIGH'
    
    elif model == 'MODEL340':
        if rheater_range == '0':
            hstr = 'Heater 1 is off'
        elif rheater_range == '1':
            hstr = 'Heater 1: Maximum heater output is 2.5mW'
        elif rheater_range == '2':
            hstr = 'Heater 1: Maximum heater output is 25mW'
        elif rheater_range == '3':
            hstr = 'Heater 1: Maximum heater output is 0.25W'
        elif rheater_range == '4':
            hstr = 'Heater 1: Maximum heater output is 2.5W'
        elif rheater_range == '5':
            hstr = 'Heater 1: Maximum heater output is 25W'
        else:
            hstr = 'Heater 1: UNKNOWN'
            
        if rheater_range2 == '0':
            hstr2 = 'Heater 2 is off'
        elif rheater_range2 == '1':
            hstr2 = 'Heater 2: Maximum heater output is 2.5mW'
        elif rheater_range2 == '2':
            hstr2 = 'Heater 2: Maximum heater output is 25mW'
        elif rheater_range2 == '3':
            hstr2 = 'Heater 2: Maximum heater output is 0.25W'
        elif rheater_range2 == '4':
            hstr2 = 'Heater 2: Maximum heater output is 2.5W'
        elif rheater_range2 == '5':
            hstr2 = 'Heater 2: Maximum heater output is 25W'
        else:
            hstr2 = 'Heater 2: UNKNOWN'
    
    elif model == 'MODEL336':
        if rheater_range == '0':
            hstr = 'Heater 1 is off'
        elif rheater_range == '1':
            hstr = 'Heater 1: Maximum heater output is 1W'
        elif rheater_range == '2':
            hstr = 'Heater 1: Maximum heater output is 10W'
        elif rheater_range == '3':
            hstr = 'Heater 1: Maximum heater output is 100W'
        else:
            hstr = 'Heater 1: UNKNOWN'

        if rheater_range2 == '0':
            hstr2 = 'Heater 2 is off'
        elif rheater_range2 == '1':
            hstr2 = 'Heater 2: Maximum heater output is 0.5W'
        elif rheater_range2 == '2':
            hstr2 = 'Heater 2: Maximum heater output is 5W'
        elif rheater_range2 == '3':
            hstr2 = 'Heater 2: Maximum heater output is 50W'
        else:
            hstr2 = 'Heater 2: UNKNOWN'

        ralarm_status_list_A = query_alarm_status('A')
        if roff_on_A == '0':
            alarm_str_A = 'Alarm A not on       '
        elif ralarm_status_list_A[0] == '1':
            alarm_str_A = 'A: Alarming High     '
        elif ralarm_status_list_A[1] == '1':
            alarm_str_A = 'A: Alarming Low      '
        else:
            alarm_str_A = 'Alarm A not triggered'
    
        ralarm_status_list_B = query_alarm_status('B')
        if roff_on_B == '0':
            alarm_str_B = 'Alarm B not on       '
        elif ralarm_status_list_B[0] == '1':
            alarm_str_B = 'B: Alarming High     '
        elif ralarm_status_list_B[1] == '1':
            alarm_str_B = 'B: Alarming Low      '
        else:
            alarm_str_B = 'Alarm B not triggered'
    
    #Print status page
    print '\n\nCurrent date and time: ' + time.strftime('%Y-%m-%d at %H:%M:%S')
    print 'Model: Lakeshore ' + model
    print '\nChannel A Temperature = ' + temp_A + ' K; Channel B Temperature = ' + temp_B + ' K'
    if model == 'MODEL340' or model == 'MODEL336':
        print alarm_str_A + '          ; ' + alarm_str_B
        print 'A High: ' + rhigh_value_A + ' K             ; B High: ' + rhigh_value_B + ' K'
        print 'A Low: ' + rlow_value_A + ' K              ; B Low: ' + rlow_value_B + ' K'
    print 'Target temperature Loop 1 is ' + rsetpoint + ' K'
    if model == 'MODEL340' or model == 'MODEL336':
        print 'Target temperature Loop 2 is ' + rsetpoint2 + ' K'
    print 'Heater 1 output at ' + heat_percent + '%'
    if model == 'MODEL340' or model == 'MODEL336':
        print 'Heater 2 output at ' + heat_percent2 + '%'
    print hstr
    if model == 'MODEL340' or model == 'MODEL336':
        print hstr2
    print 'Program will go to sleep for ' + str(sleeptime) + ' seconds\n\n'
    print '-----------------------------------------------------------------------\n'
    
    time.sleep(sleeptime)