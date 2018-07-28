#! python
import time                 #allows for wait commands to be used
import serial               #allows for communication with motor. (pyvisa technically allows for it, but this is much easier to use imo)
import datetime

pname='COM3'

def query(instring):
    inst.write(instring + '\n')
    return inst.readline()

def setTemp(temperature, loop): 
       temperature=float(temperature)
       inst.write('SETP '+ str(loop) + ', ' + "%.3f"%(temperature)+'\n')	
		#loop specifies control loop to modify. temperature is desired temperature. 
		#NOTE: read 6.10 in L340 manual. While units for setpoint default to Kelvin, the units may change.

def askheat():							
	rstr = query('HTR? 1')
	return rstr.strip(';')
		#returns heater output in percentage.

def askheat2():							
    rstr = query('HTR? 2')
    return rstr.strip(';')
	    #returns heater output in percentage.

def set_alarm(value_channel,on_off,units,value_high,value_low):
        sep = ', '         
        inst.write('ALARM '+ value_channel + sep + on_off + sep + str(units) +sep + value_high + sep+ value_low + '0,0,0,0' + '\n')
		#Refer to p125 of L340 Manual. Value channel is channel designator ('A' or 'B' here). on_off should be set to 'on' or 'off, and will turn alarm on or off.
		#	value_high is maximum value. value_low is minimum values. Values outside of range (min,max) will trigger the alarm.
		#     'units' should be set to '1' so input will be in Kelvin


def set_heater_range(value_range):
	inst.write('RANGE 1,'+ value_range +'\n')
		#See 6.12.1 of manual. Value_range must be 0,1,2,3,4, or 5.
		#0 is off. 1 is 2.5mW. 2 is 25mW. 3 is 250mW. 4 is 2.5W. 5 is 25W.

def set_heater_range2(value_range):
        inst.write('RANGE 2,'+ value_range +'\n')
                #See 6.12.1 of manual. Value_range must be 0,1,2,3,4, or 5.
                #0 is off. 1 is 2.5mW. 2 is 25mW. 3 is 250mW. 4 is 2.5W. 5 is 25W.

#inst is the name of the serial port. You need to define certain features of it for this to work.
inst=serial.Serial(port=pname, baudrate=57600, parity='O', bytesize=7, timeout=1)

#First we're going to get the state of the controller: query is just a function to send something and read the reply
AlarmA=query('ALARM? A')
time.sleep(0.1)
AlarmB=query('ALARM? B')
time.sleep(0.1)
setpoint=query('SETP? 1')
time.sleep(0.1)
setpoint2=query('SETP? 2')
time.sleep(0.1)
htrrange=query('RANGE? 1')
time.sleep(0.1)
htrrange2=query('RANGE? 2')
time.sleep(0.1)

#Since the reply for the alarm settings is long, we'll break it into a list
listA=AlarmA.rsplit(',')
listB=AlarmB.rsplit(',')

#we'll name each component according to its function
on_offA=listA[0]
sourceA=listA[1]
highA=listA[2]
lowA=listA[3]

on_offB=listB[0]
sourceB=listB[1]
highB=listB[2]
lowB=listB[3]

#We'll trim extra characters off so its just a number
highA=highA[1:(len(highA)-2)]
lowA=lowA[1:(len(lowA)-2)]
highB=highB[1:(len(highB)-3)]
lowB=lowB[1:(len(lowB)-3)]
setpoint=setpoint[1:(len(setpoint)-5)]
setpoint2=setpoint2[1:(len(setpoint2)-4)]
htrrange=htrrange[0:(len(htrrange)-1)]
htrrange2=htrrange2[0:(len(htrrange2)-1)]

ftemp=open('tempinput.txt', 'w')                             #open file holding the position data
writestring=('Target Temperature Loop 1 in Kelvin (do not include units):\n'+setpoint + '\n' +
             'Target Temperature Loop 2 in Kelvin (do not include units):\n'+ setpoint2
            +'\n'+ 'Heater Range #1 (0-5). Set to 0 to turn off  (0 is off. 1 is 2.5mW. 2 is 25mW. 3 is 250mW. 4 is 2.5W. 5 is 25W.):\n' +
            htrrange + '\n' + 'Heater Range #2 (0-5). Set to 0 to turn off  (0 is off. 1 is 2.5mW. 2 is 25mW. 3 is 250mW. 4 is 2.5W. 5 is 25W.):\n' +
            htrrange2 + '\n\n' + 'Min Temperature in Kelvin (B) (do not include units):\n'
            + lowB + '\n' + 'Max Temperature in Kelvin (B) (do not include units):\n' +
            highB + '\n' + 'Alarm On/Off (B) (set to 1 to turn on. Set to 0 to turn off):\n' +
            on_offB + '\n\n' +  'Min Temperature in Kelvin (A) (do not include units):\n'
            + lowA + '\n' + 'Max Temperature in Kelvin (A) (do not include units):\n' +
            highA + '\n' + 'Alarm On/Off (A) (set to 1 to turn on. Set to 0 to turn off):\n' +
            on_offA + '\n\n')
ftemp.write(writestring)
ftemp.close()                                               #close the file (errors might occur if not closed)

starttime=time.time()

'''
##if logswitch!=0:
##    logname= datetime.datetime.now().strftime("%m-%d-%Y_%H-%M") +'.txt'
##    logpath=os.path.join('../logfiles',logname)
##    flog=open(logpath, 'w')
##    flog.write('Time     ElapsedTime(s)    TempA(K)    TempB(K)     Heater      Motor(degrees)\n')
##    flog.close()
'''

while True:							#loop continuously (maybe make a break condition?)
    if (query('*IDN?')==''):
        print "Temperature Controller not connected. Check the connection and try again"
        time.sleep(2)
        break
    f=open('tempinput.txt', 'r')				#open file with temperature controller specs

		#File should be formatted with 1 line between each input to allow for directions.
		#Input commands should go like the following:

    f.readline()						#read line 1, but don't save
    targettemp=f.readline()					#save second line (put target number on 2nd line in units of Kelvin)
    if (not targettemp[0:-1].replace('.','',1).isdigit()):
        print "Error in 'tempinput.txt'"
        print "Error: Target Temperature Loop 1 input is not in the correct format."
        time.sleep(2)
        break

    f.readline()						#read line 1, but don't save
    targettemp2=f.readline()					#save second line (put target number on 2nd line in units of Kelvin)
    if (not targettemp2[0:-1].replace('.','',1).isdigit()):
        print targettemp2
        print "Error in 'tempinput.txt'"
        print "Error: Target Temperature Loop 2 input is not in the correct format."
        time.sleep(2)
        break
		#Where the line with the directions is thrown out and the second one with the data is kept. This allows for instruction in the input files

    f.readline()						#format input file so 1 line header.
    heatrange=f.readline()[0:-2]					#save second line (put heater range in (0-5 only))
    if (heatrange!='0' and heatrange!='1' and heatrange!='2' and 
        heatrange!='3' and heatrange!='4' and heatrange!='5'):
        print heatrange[0:-2]
        print "Error in 'tempinput.txt'"
        print "Error: The heater range 1 input is not in the correct format."
        time.sleep(2)
        break
    
    f.readline()						#format input file so 1 line header.
    heatrange2=f.readline()[0:-2]					#save second line (put heater range in (0-5 only))
    if (heatrange2!='0' and heatrange2!='1' and heatrange2!='2' and 
        heatrange2!='3' and heatrange2!='4' and heatrange2!='5'):
        print heatrange2[0:-2]
        print "Error in 'tempinput.txt'"
        print "Error: The heater range 2 input is not in the correct format."
        time.sleep(2)
        break

    f.readline()                                  #an extra space to pad alarm A settings
    f.readline()						#format input file so 1 line header.
    alarmminB=f.readline()[0:-1]					#save second line (put minimum temperature in Kelvin)
    if (not alarmminB.replace('.','',1).isdigit()):
        print "Error in 'tempinput.txt'"
        print "Error: alarm B min input is not in the correct format."
        time.sleep(2)
        break

    f.readline()						#format input file so 1 line header.
    alarmmaxB=f.readline()[0:-1]					#save second line (put maximum temperature in Kelvin)
    if (not alarmmaxB.replace('.','',1).isdigit()):
        print "Error in 'tempinput.txt'"
        print "Error: alarm B max input is not in the correct format."
        time.sleep(2)
        break

    f.readline()						#format input file so 1 line header.
    alarmonB=f.readline()[0:-1]					#save second line (alarm status)
    if (alarmonB!='1' and alarmonB!='0'):
        print "Error in 'tempinput.txt'"
        print "Error: alarm B on/off input is not in the correct format."
        time.sleep(2)
        break

    f.readline()                                  #an extra space to pad alarm A settings
    f.readline()						#format input file so 1 line header.
    alarmminA=f.readline()[0:-1]					#save second line (put minimum temperature in Kelvin)
    if (not alarmminA.replace('.','',1).isdigit()):
        print "Error in 'tempinput.txt'"
        print "Error: alarm A min input is not in the correct format."
        time.sleep(2)
        break

    f.readline()						#format input file so 1 line header.
    alarmmaxA=f.readline()[0:-1]					#save second line (put maximum temperature in Kelvin)
    if (not alarmmaxA.replace('.','',1).isdigit()):
        print "Error in 'tempinput.txt'"
        print "Error: alarm A max input is not in the correct format."
        time.sleep(2)
        break

    f.readline()						#format input file so 1 line header.
    alarmonA=f.readline()[0:-1]					#save second line (alarm status)
    if (alarmonA!='1' and alarmonA!='0'):
        print "Error in 'tempinput.txt'"
        print "Error: alarm A on/off input is not in the correct format."
        time.sleep(2)
        break
    
    f.close()						#close file. (allow for user input to change)
    
    sleeptime=10
    

    
    tempchanA = query('KRDG? A')			#read temperature on sensor A
    tempchanB = query('KRDG? B')			#read temperature on sensor B

    actualtemp = (float(tempchanA)+float(tempchanB))/2	#average temperature from L340

    set_alarm('B',alarmonB,1,alarmmaxB,alarmminB)   #setalarmB (see function/manual)
 
    set_alarm('A',alarmonA,1,alarmmaxA,alarmminA)   #setalarmA (see function/manual)

    heatpercent = askheat()                         #get heater output in percentage (see function/manual)

    heatpercent2 = askheat2()
    
    set_heater_range(heatrange)

    set_heater_range2(heatrange2)

    setTemp(targettemp, 1)

    setTemp(targettemp2, 2)

    #printing stuff
    heatrange=eval(heatrange)
    if heatrange==0:
        htstr='Heater 1 is off'
    elif heatrange==1:
        htstr='Heater 1: Maximum heater output is 2.5mW.'
    elif heatrange==2:
        htstr='Heater 1: Maximum heater output is 25mW'
    elif heatrange==3:
        htstr='Heater 1: Maximum heater output is 0.25W'
    elif heatrange==4:
        htstr='Heater 1: Maximum heater output is 2.5W'
    elif heatrange==5:
        htstr='Heater 1: Maximum heater output is 25W'

    heatrange2=eval(heatrange2)
    if heatrange2==0:
        htstr2='Heater 2 is off'
    elif heatrange2==1:
        htstr2='Heater 2: Maximum heater output is 2.5mW.'
    elif heatrange2==2:
        htstr2='Heater 2: Maximum heater output is 25mW'
    elif heatrange2==3:
        htstr2='Heater 2: Maximum heater output is 0.25W'
    elif heatrange2==4:
        htstr2='Heater 2: Maximum heater output is 2.5W'
    elif heatrange2==5:
        htstr2='Heater 2: Maximum heater output is 25W'

    alarma=query('ALARMST? A') 
    alarmb=query('ALARMST? B')
    if eval(alarmonA)==0:
        astr="Alarm A not on         "
    elif alarma[0]=='1':
        astr="A: Alarming High       "
    elif alarma[2]=='1':
        astr="A: Alarming Low        "
    else:
        astr="Alarm A not triggered  "
    if eval(alarmonB)==0:
        bstr="Alarm B not on"
    elif alarmb[0]=='1':
        bstr="B: Alarming High"
    elif alarmb[2]=='1':
        bstr="B: Alarming Low"
    else:
        bstr="Alarm B not triggered"
    

    s1 = 'Channel A Temperature = ' + repr(tempchanA)[2:-5] +' K' 
    s2 = 'Channel B Temperature = ' + repr(tempchanB)[2:-5] +' K'
    pstring=s1 + "; " + s2
    heater = 'Heater 1 output at ' + heatpercent.rstrip() + '%' #make string to show heater output
    heater2 = 'Heater 2 output at ' + heatpercent2.rstrip() + '%' #make string to show heater output
    print 'Current date and time: ' , datetime.datetime.now().strftime('%m-%d-%Y at %H:%M:%S')
    print('\n'+pstring + '\n')                      #print the string showing temps+avg
    print(astr + '          ; ' + bstr)
    print('A High: ' + alarmmaxA + ' K              ; B High: ' +alarmmaxB + ' K')
    print('A Low : ' + alarmminA + ' K              ; B Low : ' +alarmminB + ' K')
    print 'Target temperature Loop 1 is ' + str(targettemp)[0:-1] + ' K'
    print 'Target temperature Loop 2 is ' + str(targettemp2)[0:-2] + ' K'
    print(heater)                                           #show string to user
    print(heater2)
    print(htstr)
    print(htstr2+'\n\n')
    

    print ('Program will go to sleep for ' + str(sleeptime) + ' seconds\n\n')
    print ('-----------------------------------------------------------\n')
    time.sleep(sleeptime)						#wait x seconds before starting loop again
