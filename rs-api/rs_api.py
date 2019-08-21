#!/usr/bin/env python

from flask import Flask, jsonify, make_response, request
import logging
import boto3
import botocore
import json
from flask_cors import CORS

from helpers import sanitise_user_input

app = Flask(__name__)
CORS(app)
app.logger.setLevel('DEBUG')

s3c = boto3.client('s3')
s3r = boto3.resource('s3')

bucket_name = 'rs-tracker-lambda'

@app.route('/api', methods=['GET'])
def root():
	return not_found()

@app.route('/api/ping', methods=['GET'])
def ping():
	response = make_response(jsonify({'ok': True}), 200)
	app.logger.debug('STATUS:200, ACTION: {}'.format('HEALTHCHECK'))
	return response

@app.route('/api/file', methods=['GET'])
def file_name():
	user = request.args.get('user')
	date = request.args.get('date')
	if not user or not date:
		return bad_request('Either user or date not provided; `user` of type string and `date` in format YYYY-MM-DD')

	is_valid, reason = sanitise_user_input(username=user, date_string=date)
	if not is_valid:
		return bad_request(reason)

	username_length = len(user)
	
	try:
		file_list = s3c.list_objects_v2(Bucket = bucket_name)

		try:
			file_list = file_list['Contents']
		except:
			return not_found('No files found, please check your username and date range')
		
		file_list = [file for file in file_list
			if date in file['Key']
			and file['Key'][0:username_length] == user 
			and file['Key'][username_length:username_length+1] == '/']

		
		if len(file_list) > 1:
			return not_found('Ambiguous files found - you may have provided an incorrect date format YYYY-MM-DD')
		elif len(file_list) < 1:
			return not_found('No files found matching - there may be no data to retrieve. Please check your date format YYYY-MM-DD and username.')
		else:
			app.logger.debug('STATUS:200, FILENAME: {}'.format(file_list[0]['Key']))
			return make_response(jsonify(file_list[0]['Key']), 200)
	except Exception as e:
		app.logger.debug(e)
		return not_found('Not found for an unknown reason')

@app.route('/api/data', methods=['GET'])
def get_data():
	file_key = request.args.get('filekey')
	if file_key != None:
		try:
			s3r.meta.client.download_file(bucket_name, file_key, '/tmp/current.json')
		except Exception as e:
			return not_found('Your file was not found - please check your file name.')
	else:
		return bad_request('Invalid or no input. Please check your filename is valid.')
	with open('/tmp/current.json', 'r') as stats:
		stats_file = json.load(stats)
	app.logger.debug('STATUS:200, FILE_CONTENTS: {}'.format(stats_file))
	return make_response(jsonify(stats_file), 200)

@app.route('/api/newtrackingrequest', methods=['PUT'])
def new_user_to_track():
	print('recieved request')
	user = request.args.get('username')
	if not user:
		return bad_request('Invalid input, query parameters `username` (string).')

	is_valid, reason = sanitise_user_input(username=user)
	if not is_valid:
		return bad_request(reason)

	try:
		s3r.meta.client.download_file(bucket_name, 'users.py', 'users.py')
		from users import users as ux
	except:
		return internal_error()

	if user not in ux['track_rs_users']:
		ux['track_rs_users'].append(user)
	else:
		return make_response(jsonify(dict(username=user, message='User already exists in database.')), 200)

	print(ux)

	return make_response(jsonify(dict(username=user, message='User added to database')), 200)

@app.errorhandler(500)
def internal_error(error='[500] Internal server error.'):
	app.logger.error('STATUS:500, ERROR:' + error)
	return make_response(jsonify({'error': error}), 500)

@app.errorhandler(404)
def not_found(error='[404] Something went wrong - we didn\'t find what we were expecting.'):
	if len(str(error)) >= 100:
		error = '[404] Something went wrong - we didn\'t find what we were expecting.'
	app.logger.debug('STATUS:404, ERROR: "Document not found"')
	return make_response(jsonify({'error': error}), 404)

@app.errorhandler(400)
def bad_request(error='[400] Something went wrong - bad request.'):
	app.logger.debug('STATUS:400, ERROR: {}'.format(str(error)))
	return make_response(jsonify({'error': error}), 400)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=3000)
