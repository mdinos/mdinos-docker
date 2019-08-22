#!/usr/bin/env python

import logging
import boto3
import botocore
import json
import os
from flask import Flask, jsonify, make_response, request
from requests import get
from flask_cors import CORS
from helpers import sanitise_user_input

app = Flask(__name__)
CORS(app)
app.logger.setLevel('DEBUG')

s3c = boto3.client('s3')
s3r = boto3.resource('s3')

bucket_name = 'rs-tracker-lambda'
runescape_hiscores_endpoint = 'https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player='

@app.route('/api', methods=['GET'])
def root():
	return not_found()

@app.route('/api/ping', methods=['GET'])
def ping():
	response = make_response(jsonify({'ok': True}), 200)
	app.logger.debug('STATUS:200, ACTION: {}'.format('ping'))
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
		except:
			return not_found('Your file was not found - please check your file name.')
	else:
		return bad_request('Invalid or no input. Please check your filename is valid.')
	with open('/tmp/current.json', 'r') as stats:
		stats_file = json.load(stats)
	app.logger.debug('STATUS:200, FILE_CONTENTS: {}'.format(stats_file))
	return make_response(jsonify(stats_file), 200)

@app.route('/api/newtrackingrequest', methods=['PUT'])
def new_user_to_track():
	user = request.args.get('username')
	app.logger.info('Tracking request recieved for {}'.format(user))
	if not user:
		return bad_request('Invalid input, query parameters `username` (string).')

	is_valid, reason = sanitise_user_input(username=user)
	if not is_valid:
		return bad_request(reason)

	rs_api_response = get(runescape_hiscores_endpoint + user, timeout=10)
	if rs_api_response.status_code != 200:
		return bad_request('Bad request: User not found on RS hiscores.')

	try:
		s3r.Object(bucket_name, 'users.json').download_file('/tmp/users.json')
		with open('/tmp/users.json', 'r') as users_json:
			ux = json.loads(users_json.read())
		app.logger.debug('imported {}'.format(ux))
	except Exception as e:
		app.logger.debug('[500] Internal server error: ')
		app.logger.debug(e)
		return internal_error()

	if user not in ux['users']:
		ux['users'].append(user)
	else:
		app.logger.debug('Returning user {} exists'.format(user))
		return bad_request('User {} already exists in the database.'.format(user))

	try:
		with open('/tmp/users.json', 'w') as users_file:
			users_file.write(json.dumps(ux, indent=4))
		s3r.Object(bucket_name, 'users.json').upload_file('/tmp/users.json')
		os.remove('/tmp/users.json')
	except Exception as e:
		app.logger.error('[500] Error: ')
		app.logger.error(e)
		return internal_error('[500] Something went wrong updating remote users file.') 

	app.logger.info('Added user {} to tracking list.'.format(user))
	return make_response(jsonify(dict(username=user, message='User added to database')), 200)

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
	app.run(debug=True, host='0.0.0.0', port=3000)
