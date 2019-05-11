from flask import Flask, jsonify, make_response, request
import logging
import boto3
import botocore
import json

app = Flask(__name__)
log = logging.getLogger('rs_api')
log.setLevel(logging.DEBUG)

s3c = boto3.client('s3')
s3r = boto3.resource('s3')
bucket_name = 'rs-tracker-lambda'

@app.route('/api/healthcheck', methods=['GET'])
def healthcheck():
	response = make_response(jsonify({'ok': True}), 200)
	log.debug(response)
	return response

@app.route('/api/file', methods=['GET'])
def file_name():
	user = request.args.get('user')
	log.debug('Username: ' + user)
	date = request.args.get('date')
	log.debug('Date: ' + date)
	if user and date and len(user) <= 12:
		log.debug('User and date both provided successfully.')
		try:
			log.debug('Trying to list s3 objects in bucket.')
			file_list = s3c.list_objects_v2(Bucket = bucket_name)
			log.debug('Got list of s3 objects: ' + str(file_list))
			file_list = file_list['Contents']
			file_list = [file for file in file_list
				if date in file['Key']]
			log.debug('Filtered for dates: ' + str(file_list))
			log.debug(file_list[0]['Key'][0:len(user)])
			file_list = [file for file in file_list
				if file['Key'][0:len(user)] == user and file['Key'][len(user):len(user)+1] == '/']
			log.debug('Filtered for usernames: ' + str(file_list))
			if len(file_list) > 1:
				log.debug('Ambiguous files found: ' + str(list_list))
				return not_found('Ambiguous files found - please inform the administrator.')
			elif len(file_list) < 1:
				log.debug('No files found.')
				return not_found('No files found - please check your date format YYYY-MM-DD and username.')
			else:
				return make_response(jsonify(file_list[0]['Key']), 200)
		except Exception as e:
			log.debug('Exception caught:')
			log.debug(e)
			return not_found()
	else:
		return not_found()

@app.route('/api/data', methods=['GET'])
def get_data():
	file_key = request.args.get('filekey')
	s3r.meta.client.download_file(bucket_name, file_key, '/tmp/current.json')
	with open('/tmp/current.json', 'r') as stats:
		stats_file = json.load(stats)
	return make_response(json.dumps(stats_file), 200)

@app.errorhandler(404)
def not_found(error='Something went wrong.'):
	return make_response(jsonify({'error': error}), 404)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5000)
