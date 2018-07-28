#! python
import time                 #allows for wait commands to be used
import serial               #allows for communication with motor. (pyvisa technically allows for it, but this is much easier to use imo)
import datetime
import os

pname='COM5'
#sleeptime is the length of rest given to the python script
#the older controller needs more time between commands, so the loop takes longer
sleeptime=5
#Version for Lakeshore 330

def query(instring):
    inst.write(instring + '\n')
    time.sleep(0.5)
    read=inst.readline()
    while(inst.inWaiting()!=0):
        inst.readline()
    return read

def setTemp(temperature, loop): 
       temperature=float(temperature)
       inst.write('SETP' + "%.3f"%(temperature)+'\n')
	
		#loop specifies control loop to modify. temperature is desired temperature. 
		#NOTE: read 6.10 in L340 manual. While units for setpoint default to Kelvin, the units may change.

def askheat():							
	rstr = query('HEAT?')
	return rstr.strip(';')

		#returns heater output in percentage.

def set_heater_range(value_range):
	inst.write('RANG' + value_range +'\n')

		#See 6.12.1 of manual. Value_range must be 0,1,2,3.
		#0 is off. 1 is 2.5mW. 2 is 25mW. 3 is 250mW. 4 is 2.5W. 5 is 25W.


inst=serial.Serial(port=pname, baudrate=9600, parity='O', bytesize=7, timeout=1)

query('++addr 12')
IDN=query('*IDN?')

inst.write('CUNI K')
inst.write('SUNI K')

setpoint=query('SETP?')
time.sleep(0.5)
htrrange=query('RANG?')
time.sleep(0.5)

setpoint=setpoint[1:(len(setpoint)-5)]
htrrange=htrrange[0:(len(htrrange)-1)]

ftemp=open('tempinput_330.txt', 'w')                             #open file holding the position data
writestring=('Target Temperature in Kelvin (do not include units):\n'+setpoint
            +'\n'+ 'Heater Range #1 (0-5). Set to 0 to turn off  (0 is off. 1 is 2.5mW. 2 is 25mW. 3 is 250mW. 4 is 2.5W. 5 is 25W.):\n' +
            htrrange + '\n')
ftemp.write(writestring)
ftemp.close()                                               #close the file (errors might occur if not closed)

starttime=time.time()

while True:							#loop continuously (maybe make a break condition?)
    if (query('*IDN?')==''):
        print "Temperature Controller not connected. Check the connection and try again"
        time.sleep(2)
        break
    f=open('tempinput_330.txt', 'r')				#open file with temperature controller specs

		#File should be formatted with 1 line between each input to allow for directions.
		#Input commands should go like the following:

    f.readline()						#read line 1, but don't save
    targettemp=f.readline()					#save second line (put target number on 2nd line in units of Kelvin)
    if (not targettemp[0:-1].replace('.','',1).isdigit()):
        print "Error in 'tempinput_330.txt'"
        print "Error: Target Temperature input is not in the correct format."
        time.sleep(2)
        break
		#Where the line with the directions is thrown out and the second one with the data is kept. This allows for instruction in the input files

    f.readline()						#format input file so 1 line header.
    heatrange=f.readline().rstrip()					#save second line (put heater range in (0-5 only))
    if (heatrange!='0' and heatrange!='1' and heatrange!='2' and 
        heatrange!='3' and heatrange!='4' and heatrange!='5'):
        print heatrange[0:-2]
        print "Error in 'tempinput_330.txt'"
        print "Error: The heater range input is not in the correct format."
        time.sleep(2)
        break

    
    f.close()						#close file. (allow for user input to change)
    

    
    tempchanB=IDN
    while(tempchanB==IDN or tempchanA==IDN):
        tempchanA = query('SDAT?')			#read temperature on sensor A
        tempchanB = query('CDAT?')			#read temperature on sensor B
    actualtemp = (float(tempchanA)+float(tempchanB))/2	#average temperature from L340

    heatpercent = askheat()                         #get heater output in percentage (see function/manual)
    time.sleep(1)
    set_heater_range(heatrange)
    time.sleep(1)
    setTemp(targettemp, 1)

    #printing stuff
    heatrange=eval(heatrange)
    if heatrange==0:
        htstr='Heater is off'
    elif heatrange==1:
        htstr='Heater: Maximum heater output is LOW'
    elif heatrange==2:
        htstr='Heater: Maximum heater output is MED'
    elif heatrange==3:
        htstr='Heater: Maximum heater output is HIGH'

    

    s1 = 'Channel A Temperature = ' + repr(tempchanA)[2:-5] +' K' 
    s2 = 'Channel B Temperature = ' + repr(tempchanB)[2:-5] +' K'
    pstring=s1 + "; " + s2
    heater = 'Heater output at ' + heatpercent.rstrip() + '%' #make string to show heater output
    print "Current date and time: " , datetime.datetime.now().strftime("%m-%d-%Y at %H:%M:%S")
    print('\n'+pstring + '\n')                      #print the string showing temps+avg
    print 'Target temperature is ' + str(targettemp)[0:-1] + ' K'
    print(heater)                                           #show string to user
    print(htstr)
    print('\n')
    

    print ('Program will go to sleep for ' + str(sleeptime+5) + ' seconds\n\n')
    print ('-----------------------------------------------------------')
    time.sleep(sleeptime)						#wait x seconds before starting loop again
