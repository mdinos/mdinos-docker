from flask import Flask, jsonify, make_response, request
import logging
import boto3
import botocore
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
log = logging.getLogger('rs_api')
log.setLevel(logging.DEBUG)

s3c = boto3.client('s3')
s3r = boto3.resource('s3')

bucket_name = 'rs-tracker-lambda'

@app.route('/ping', methods=['GET'])
def ping():
	response = make_response(jsonify({'ok': True}), 200)
	log.debug('STATUS:200, ACTION: {}'.format('HEALTHCHECK'))
	return response

@app.route('/file', methods=['GET'])
def file_name():
	try:
		user = request.args.get('user')
		date = request.args.get('date')
		username_length = len(user)
		date_length = len(date)
	except Exception as e:
		return bad_request('Invalid input, `user` of type string and `date` in format YYYY-MM-DD')
	
	if not user \
		or not date \
		or username_length > 12 \
		or username_length < 1 \
		or date_length != 10:
		return bad_request('Invalid input, `user` of type string and `date` in format YYYY-MM-DD')

	try:
		file_list = s3c.list_objects_v2(Bucket = bucket_name)
		file_list = [file for file in file_list['Contents']
			if date in file['Key']
			and file['Key'][0:username_length] == user 
			and file['Key'][username_length:username_length+1] == '/']
		if len(file_list) > 1:
			return not_found('Ambiguous files found - you may have provided an incorrect date format YYYY-MM-DD')
		elif len(file_list) < 1:
			return not_found('No files found - there may be no data to retrieve. Please check your date format YYYY-MM-DD and username.')
		else:
			log.debug('STATUS:200, FILENAME: {}'.format(file_list[0]['Key']))
			return make_response(jsonify(file_list[0]['Key']), 200)
	except Exception as e:
		return not_found(e)

@app.route('/data', methods=['GET'])
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
	log.debug('STATUS:200, FILE_CONTENTS: {}'.format(stats_file))
	return make_response(jsonify(stats_file), 200)

@app.errorhandler(404)
def not_found(error='Something went wrong - we didn\'t find what we were expecting.'):
	log.debug('STATUS:404, ERROR: {}'.format(str(error)))
	return make_response(jsonify({'error': error}), 404)

@app.errorhandler(400)
def bad_request(error='Something went wrong - bad request.'):
	log.debug('STATUS:400, ERROR: {}'.format(str(error)))
	return make_response(jsonify({'error': error}), 400)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=3000)
