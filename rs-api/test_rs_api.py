import rs_api
from unittest import TestCase
from mock import patch, MagicMock
import json
import requests

class HealthCheck(TestCase):
    def setUp(self):
        rs_api.app.testing = True
        self.app = rs_api.app.test_client()

    def test_api_functional(self):
        with self.app:
            result = self.app.get('/api/healthcheck')
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.data, b'{\"ok\":true}\n')

class FileNameEndpoint(TestCase):
    def setUp(self):
        rs_api.app.testing = True
        self.app = rs_api.app.test_client()
        rs_api.s3c = MagicMock()
        self.test_input = {
            'Contents': [
                {'Key': 'woofythedog/woofythedog_2019-04-14T00:22:47_stats.json'},
                {'Key': 'woofythedog/woofythedog_2019-04-24T00:22:48_stats.json'},
                {'Key': 'other crap'},
                {'Key': 'woofothedog/woofothedog_2019-04-24T00:22:48_stats.json'}
            ]
        }
        rs_api.s3c.list_objects_v2 = MagicMock(return_value=self.test_input)
        

    def test_with_good_input(self):
        result = self.app.get('/api/file', query_string=dict(user='woofythedog', date='2019-04-24'))
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.get_json(), 'woofythedog/woofythedog_2019-04-24T00:22:48_stats.json')
        rs_api.s3c.list_objects_v2.assert_called_with(Bucket='rs-tracker-lambda')
        
    def test_with_partially_matching_user_name(self):
        result = self.app.get('/api/file', query_string=dict(user='woofythedo', date='2019-04-24'))
        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.get_json(), {'error': 'No files found - please check your date format YYYY-MM-DD and username.'})

    def test_with_too_long_username(self):
        result = self.app.get('/api/file', query_string=dict(user='woofythedog/', date='2019-04-24'))
        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.get_json(), {'error': 'No files found - please check your date format YYYY-MM-DD and username.'})
        
        