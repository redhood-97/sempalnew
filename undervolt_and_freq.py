#communication info
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import time
import RPi.GPIO as GPIO

v_base=240 #standard single phase voltage rms value
SERVER_HOST = "169.254.0.12"
SERVER_PORT = 502 #this has to be 502 for tcp/ip modbus
SERVER_UNIT_ID = 100 #slave id is 100 for schneider powerlogic ion 7650

#default value for ionmeter
#subnet mask= 255.240.0.0
#gateway= 0.0.0.0

#Required Registers to be read :-
#Va= 40166  2 registers  ie. c.read_input_registers(40166,2)
#power kw a = 40198  2 registers
#kVAR a= 40208 2 registers
#kVA a= 40218 2 registers
#frequency = 40159  1 register 
#Ia= 40150 1 register

#relay interface code begins--------------------------------------------------------------------------------------------
#enter pin number here 
l0=29
l1=31
l2=33
l3=35
#setting up the pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(l0, GPIO.OUT)
GPIO.setup(l1, GPIO.OUT)
GPIO.setup(l2, GPIO.OUT)
GPIO.setup(l3, GPIO.OUT)
#initializing the pin
GPIO.output(l0, False)
GPIO.output(l1, False)
GPIO.output(l2, False)
GPIO.output(l3, False)
#relay interface code ends ---------------------------------------------------------------------------------------------

#decision code begins --------------------------------------------------------------------------------------------------
#to read the real and reactive power demands of each bus
P=[50,40,30,20]
Q=[50,40,30,20]
UBR=[4,3,2,1]
V=[220,220,220,220]
S=[]
state_val=[1,1,1,1]
bpi=[0,0,0,0]

def read_data():
	for i in [0,1,2,3]:
		P[i]=float(input("Enter real power demand for Bus "+str(i)+":"))
		Q[i]=float(input("Enter reactive power demand for Bus "+str(i)+":"))
		V[i]=float(input("Enter required voltage for Bus "+str(i)+":"))
		X[i]=float(input("Enter line reactance for Bus "+str(i)+":"))
		UBR[i]=float(input("Enter User Baded Ranking for Bus "+str(i)+":"))


def interface_relay():
    GPIO.output(l0,True) if state_val[0]==1 else GPIO.output(l0,False)
    GPIO.output(l1,True) if state_val[1]==1 else GPIO.output(l1,False)
    GPIO.output(l2,True) if state_val[2]==1 else GPIO.output(l2,False)
    GPIO.output(l3,True) if state_val[3]==1 else GPIO.output(l3,False)

def set_priority():
	for i in [0,1,2,3]:
		S[i]=sqrt(pow(P[i],2)+pow(Q[i],2))
		bpi[i]=(P[i]*UBR[i]*(2*Q[i]*X[i]-V[i]))/(2*X[i]*S[i])
	return
 
def change_state(k):
	for i in [0,1,2,3]:
		if(bpi[i]>k):
			state_val[i]=1
		else:
			state_val[i]=0
	return
def decision(v,f):
	set_priority()
	bpi_sorted=bpi
	bpi_sorted.sort()
	v=v/v_base;
	if(f<49.7 or v<0.97)
		change_state(bpi_sorted[0])#least imp load
	else if(f<49.4 or v<0.94)
		change_state(bpi_sorted[1])#second least imp load
	else if(f<49.1 or v<0.91)
		change_state(bpi_sorted[2])#third least imp load
	else if(f<48.8 pt v<0.88)
		change_state(bpi_sorted[3])#third least imp load or most imp load
	else
		state_val=[1,1,1,1] #engage all loads
	inteface_relay()
	return

#Decision code ends-----------------------------------------------------------------------------------------------
#schneider sensor interface code begins---------------------------------------------------------------------------
c = ModbusClient()
c.host(SERVER_HOST)
c.port(SERVER_PORT)
c.unit_id(SERVER_UNIT_ID) #default slave id for schneider is 100

if not c.is_open():
            if not c.open():
                print("cannot connect ....")

if c.is_open():
    #read_holding_registers has an offset of 4000 to begin with
    while True:
        voltage_a=c.read_holding_registers(166,1)#list output for integer take voltage_a[0]
        voltage_a=voltage_a[0]
        current_a=c.read_holding_registers(150,1)
        current_a=current_a[0]
        real_power_a=c.read_holding_registers(198,1)
        real_power_a=real_power_a[0]
        reactive_power_a=c.read_holding_registers(208,1)
        reactive_power_a=reactive_power_a[0]
        apparent_power_a=c.read_holding_registers(218,1)
        apparent_power_a=apparent_power_a[0]
        freq=c.read_holding_registers(159,1)
        freq=freq[0]/10
        decision(voltage_a,freq)
        print(voltage_a)
        print(current_a)
        print(real_power_a)
        print(reactive_power_a)
        print(apparent_power_a)
        print(freq)
#schneider interface code ends-------------------------------------------------------------------------------------       





