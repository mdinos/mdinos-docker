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
	date = request.args.get('date')
	if user and date:
		try:
			file_list = s3c.list_objects_v2(Bucket = bucket_name)
			file_list = file_list['Contents']
			file = [file for file in file_list
				if user and date in file['Key']]
			return make_response(jsonify(file[0]['Key']), 200)
		except:
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
	app.run(debug=True, host='0.0.0.0', port=80)
