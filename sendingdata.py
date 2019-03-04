import time
import json

import flask
from flask import Flask, render_template, request
from flask import jsonify
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
import requests
import random

import numpy as np
import math

#################################################################

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

#################################################################

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

#################################################################

app = Flask(__name__)
cors = CORS(app)
api = Api(app)
app.config['CORS_HEADERS'] = 'Content-Type'

voltage_a = 0
current_a = 0
freq_a = 0

##################################################################



#################################################################

def send_data():
		while True:
				voltage_a = random.randint(187,220)
				current_a = random.randint(1,10)
				freq_a = 50
				data = {
						"voltage_reading" : '%.2f'%voltage_a,
						"current_reading" : '%.2f'%current_a,
						"frequency_reading" : '%.2f'%freq_a,
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
    elif(f<49.1 or v<0.91):
        change_state(bpi_sorted[2])#third least imp load
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
        app.run(host='0.0.0.0', port=8080, debug=True)