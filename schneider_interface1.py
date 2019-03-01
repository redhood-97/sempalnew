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

print("========================================================================")
print("                                                                        ")
print("        _______                                                __       ")
print("       / _____/  ________   ___   ____   _______   _______    / /       ")
print("      / /____   / ____  /  / _ '.'   /  / ___  /  /____  /   / /        ")
print("     /____  /  / /___/ /  / / / / / /  / /  / /  _____/ /   / /         ")
print("         / /  / ______/  / / / / / /  / /  / /  / ___  /   / /          ")
print("   _____/ /  / /_____   / / / / / /  / /__/ /  / /__/ /_  / /___        ")
print("  /______/  /_______/  /_/ /_/ /_/  / _____/  /________/ /_____/        ")
print("                                   / /                                  ")
print("                                  /_/                                   ")
print("                                                                        ")
print("========================================================================")


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
                #print freq
                        np.array(voltage_a,dtype=float)
                        np.array(current_a,dtype=float)
                        np.array(real_power_a,dtype=float)
                        np.array(reactive_power_a,dtype=float)
                        np.array(apparent_power_a,dtype=float)
                        np.array(freq,dtype=float)
                        data = {
                                    "voltage_reading" : voltage_a,
                                    "current_reading" : current_a,
                                    "real_power_rating" : real_power_a,
                                    "reactive_power_rating" : reactive_power_a,
                                    "apparent_power_rating" : apparent_power_a,
                                    "frequency_reading" : freq
                        }
                        print (data)
                        return data
        #decision(<some parameters>)

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





