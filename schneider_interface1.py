import pyModbusTCP
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import time
import json

import flask
from flask import Flask, render_template
from flask import jsonify
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api

import numpy as np
import RPi.GPIO as GPIO
import math

print("====================================================================")
print("                                                                    ")
print("        _______                                     __              ")
print("       / _____/________ ___   ___________ _______  / / ______       ")
print("      / /____ / ____  // _ '.'   / ___  //____  / / / / ____/       ")
print("     /____  // /___/ // / / / / / /  / /_____/ / / / / /___         ")
print("         / // ______// / / / / / /  / // ___  / / / /___  /         ")
print("   _____/ // /______/ / / / / / /__/ // /__/ /_/ /_____/ /          ")
print("  /______//__________/ /_/ /_/ _____//____________/_____/           ")
print("                            / /                                     ")
print("                           /_/                                      ")
print("                                                                    ")
print("====================================================================")

#####################################################################################
################   GPIO pin initializations   #######################################
#####################################################################################

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

#####################################################################################
####################################################################################
P=[50,40,30,20]
Q=[50,40,30,20]
UBR=[4,3,2,1]
X=[1,1,1,1]
V=[220,220,220,220]
S=[1,1,1,1]
state_val=[1,1,1,1]
bpi=[4,3,2,1]
v_base=220

'''
def read_data():
    for i in [0,1,2,3]:
        P[i]=float(input("Enter real power demand for Bus "+str(i)+":"))
        Q[i]=float(input("Enter reactive power demand for Bus "+str(i)+":"))
        V[i]=float(input("Enter required voltage for Bus "+str(i)+":"))
        X[i]=float(input("Enter line reactance for Bus "+str(i)+":"))
        UBR[i]=float(input("Enter User Baded Ranking for Bus "+str(i)+":"))


def set_priority():
    for i in [0,1,2,3]:
        S[i]=math.sqrt(pow(P[i],2)+pow(Q[i],2))
        bpi[i]=(P[i]*UBR[i]*(2*Q[i]*X[i]-V[i]))/(2*X[i]*S[i])
    return 
'''

def print_priority():
    for i in [0,1,2,3]:
        print("Priority for load "+str(i)+": "+str(bpi[i]))
    return

#read_data()
#set_priority()
print_priority()


##################################################################################

app = Flask(__name__)
cors = CORS(app)
api = Api(app)
app.config['CORS_HEADERS'] = 'Content-Type'
@app.route('/page')
def index():
    return render_template('index1.html')

def send_data():
        SERVER_HOST = "169.254.0.12"
        SERVER_PORT = 502        #this has to be 502 for tcp/ip modbus
        SERVER_UNIT_ID = 100     #slave id is 100 for schneider powerlogic ion 7650

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

#this function reads the float value for address and number of bits (not required)
#def read_float( address, number=1):
#   reg_l = c.read_holding_registers(address, number ) #can change to read_input_registers just to check
#   if reg_l:
#       return [utils.decode_ieee(f) for f in utils.word_list_to_long(reg_l)]
#   else:
#       return None

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
        		#voltage_a=voltage_a[0]
                #print voltage_a
                        current_a=c.read_holding_registers(150,1)
        		#current_a=current_a[0]
                #print current_a
                        real_power_a=c.read_holding_registers(208,1)
        		#real_power_a=real_power_a[0]
                #print real_power_a
                        reactive_power_a=c.read_holding_registers(218,1)
        		#reactive_power_a=reactive_power_a[0]
                #print reactive_power_a
                        apparent_power_a=c.read_holding_registers(218,1)
        		#apparent_power_a=apparent_power_a[0]
                #print apparent_power_a
                        freq=c.read_holding_registers(159,1)
                        freq=freq[0]/10
                #move this part to decision in case of load scheduling
                        #set_priority()
                        #print_priority()
                #print freq
                        np.array(voltage_a,dtype=float)
                        np.array(current_a,dtype=float)
                        np.array(real_power_a,dtype=float)
                        np.array(reactive_power_a,dtype=float)
                        np.array(apparent_power_a,dtype=float)
                        np.array(freq,dtype=float)
                        data = {
                                    "voltage_reading" : '%.2f'%voltage_a,
                                    "current_reading" : '%.2f'%current_a,
                                    "real_power_rating" : '%.2f'%real_power_a,
                                    "reactive_power_rating" : '%.2f'%reactive_power_a,
                                    "apparent_power_rating" : '%.2f'%apparent_power_a,
                                    "frequency_reading" : '%.2f'%freq,
                                    "load_0_status": "ON" if state_val[0]==1 else "OFF",
                                    "load_1_status": "ON" if state_val[1]==1 else "OFF",
                                    "load_2_status": "ON" if state_val[2]==1 else "OFF",
                                    "load_3_status": "ON" if state_val[3]==1 else "OFF",
                                    "bpi_0": '%.2f'%bpi[0],
                                    "bpi_1": '%.2f'%bpi[1],
                                    "bpi_2": '%.2f'%bpi[2],
                                    "bpi_3": '%.2f'%bpi[3]
                        }
                        print (data)
                        decision(data)
                        return data
        #decision(<some parameters>)

def change_state(k):
    for i in [0,1,2,3]:
        if(bpi[i]>k):
            state_val[i]=1
        else:
            state_val[i]=0
    return

def interface_relay():
    GPIO.output(l0,True) if state_val[0]==1 else GPIO.output(l0,False)
    GPIO.output(l1,True) if state_val[1]==1 else GPIO.output(l1,False)
    GPIO.output(l2,True) if state_val[2]==1 else GPIO.output(l2,False)
    GPIO.output(l3,True) if state_val[3]==1 else GPIO.output(l3,False)
    return

def decision(mydata):
    v=float(mydata["voltage_reading"])
    f=float(mydata["frequency_reading"])
    bpi_sorted=bpi
    bpi_sorted.sort()
    v=v/220.00;
    print("Voltage(pu): "+str(v))
    if(f<48.8 or v<0.88):
        change_state(bpi_sorted[3])#third least imp load or most imp load
        print("Stage IV")
    elif(f<49.1 or v<0.91):
        change_state(bpi_sorted[2])#third least imp load
        print("Stage III")
    elif(f<49.4 or v<0.94):
        change_state(bpi_sorted[1])#second least imp load
        print("Stage II")
    elif(f<49.7 or v<0.97):
        change_state(bpi_sorted[0])#least imp load
        print("Stage I")
    else:
        state_val=[1,1,1,1] #engage all loads
    inteface_relay()
    return

##################################################
##################################################

@app.route('/watch')
@cross_origin()
def watch():
        while True:
                data = send_data()
                response = app.response_class(
                        response=json.dumps(data),
                        status=200,
                        mimetype='application/json'
                )
                return response

if __name__ == "__main__":
        app.run(host='192.168.43.249', port=8080, debug=True)





