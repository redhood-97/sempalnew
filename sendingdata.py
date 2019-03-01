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

app = Flask(__name__)
cors = CORS(app)
api = Api(app)
app.config['CORS_HEADERS'] = 'Content-Type'

voltage_a = 0
current_a = 0
freq_a = 0
def send_data():
		while True:
				voltage_a = random.randint(1,10)
				current_a = random.randint(1,10)
				freq_a = random.randint(1,10)
				data = {
						"voltage_reading" : voltage_a,
						"current_reading" : current_a,
						"frequency_reading" : freq_a
				}		
				print (data)
				return data

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