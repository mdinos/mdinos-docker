import logging
import json
import os
from flask import Flask, jsonify, make_response, request
from requests import get
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.logger.setLevel('DEBUG')

@app.route('/api/ping', methods=['GET'])
def ping():
	response = make_response(jsonify({'ok': True}), 200)
	app.logger.debug('STATUS:200, ACTION: {}'.format('ping'))
	return response

@app.route('/api/fail', methods=['GET'])
def ohfuck():
	return internal_error()

@app.errorhandler(500)
def internal_error(error='[500] Internal server error.'):
	app.logger.error('STATUS:500, ERROR:' + error)
	return make_response(jsonify({'error': error}), 500)

@app.errorhandler(404)
def not_found(error='[404] Something went wrong - we didn\'t find what we were expecting.'):
	if len(str(error)) >= 120:
		error = '[404] Something went wrong - we didn\'t find what we were expecting.'
	app.logger.debug('STATUS:404, ERROR: "Document not found"')
	return make_response(jsonify({'error': str(error)}), 404)

@app.errorhandler(400)
def bad_request(error='[400] Something went wrong - bad request.'):
	app.logger.debug('STATUS:400, ERROR: {}'.format(str(error)))
	return make_response(jsonify({'error': error}), 400)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=80)
