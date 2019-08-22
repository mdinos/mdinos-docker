import rs_api
from unittest import TestCase
from mock import patch, MagicMock
import json
import requests
import sys


class HealthCheckEndpoint(TestCase):
    def setUp(self):
        rs_api.app.testing = True
        self.app = rs_api.app.test_client()

    def test_api_functional(self):
        with self.app:
            result = self.app.get("/api/ping")
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.data, b'{"ok":true}\n')


class FileNameEndpoint(TestCase):
    def setUp(self):
        rs_api.app.testing = True
        self.app = rs_api.app.test_client()
        test_input = {
            "Contents": [
                {"Key": "woofythedog/woofythedog_2019-04-14T00:22:47_stats.json"},
                {"Key": "woofythedog/woofythedog_2019-04-24T00:22:48_stats.json"},
                {"Key": "other crap"},
                {"Key": "woofothedog/woofothedog_2019-04-24T00:22:48_stats.json"},
            ]
        }
        rs_api.s3c.list_objects_v2 = MagicMock(return_value=test_input)

    def test_with_good_input(self):
        result = self.app.get(
            "/api/file", query_string=dict(user="woofythedog", date="2019-04-24")
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(
            result.get_json(), "woofythedog/woofythedog_2019-04-24T00:22:48_stats.json"
        )
        rs_api.s3c.list_objects_v2.assert_called_with(Bucket="rs-tracker-lambda")

    def test_with_partially_matching_user_name(self):
        result = self.app.get(
            "/api/file", query_string=dict(user="woofythedo", date="2019-04-24")
        )
        self.assertEqual(result.status_code, 404)
        self.assertEqual(
            result.get_json(),
            {
                "error": "No files found matching - there may be no data to retrieve. Please check your date format YYYY-MM-DD and username."
            },
        )

    def test_with_too_long_username(self):
        result = self.app.get(
            "/api/file", query_string=dict(user="woofythedog/", date="2019-04-24")
        )
        self.assertEqual(result.status_code, 400)
        self.assertEqual(
            result.get_json(),
            {
                "error": "Bad input: Invalid username"
            },
        )

    def test_with_no_input(self):
        result = self.app.get("/api/file")
        self.assertEqual(result.status_code, 400)
        self.assertEqual(
            result.get_json(),
            {
                "error": "Either user or date not provided; `user` of type string and `date` in format YYYY-MM-DD"
            },
        )

    def test_with_empty_input(self):
        result = self.app.get("/api/file", query_string=dict(user="", date=""))
        self.assertEqual(result.status_code, 400)
        self.assertEqual(
            result.get_json(),
            {
                "error": "Either user or date not provided; `user` of type string and `date` in format YYYY-MM-DD"
            },
        )

    def test_with_single_letter_from_name(self):
        result = self.app.get(
            "/api/file", query_string=dict(user="o", date="2019-04-24")
        )
        self.assertEqual(result.status_code, 404)
        self.assertEqual(
            result.get_json(),
            {
                "error": "No files found matching - there may be no data to retrieve. Please check your date format YYYY-MM-DD and username."
            },
        )

    def test_with_partial_date(self):
        result = self.app.get(
            "/api/file", query_string=dict(user="woofythedog", date="2019-04")
        )
        self.assertEqual(result.status_code, 400)
        self.assertEqual(
            result.get_json(),
            {
                "error": "Invalid date format; YYYY-MM-DD."
            },
        )


class GetDataEndpoint(TestCase):
    def setUp(self):
        rs_api.app.testing = True
        self.app = rs_api.app.test_client()
        with open("test-data/woofythedog_2019-04-13_stats.json", "r") as d:
            self.test_data = json.load(d)
        with open("/tmp/current.json", "w+") as tmp:
            json.dump(self.test_data, tmp)

    def test_with_good_input(self):
        rs_api.s3r.meta.client.download_file = MagicMock(return_value=self.test_data)
        result = self.app.get(
            "/api/data",
            query_string=dict(
                filekey="woofythedog/woofythedog_2019-04-14T00:22:47_stats.json"
            ),
        )
        rs_api.s3r.meta.client.download_file.assert_called_with(
            "rs-tracker-lambda",
            "woofythedog/woofythedog_2019-04-14T00:22:47_stats.json",
            "/tmp/current.json",
        )
        self.assertEqual(result.get_json(), self.test_data)
        self.assertEqual(result.status_code, 200)

    def test_with_no_input(self):
        result = self.app.get("/api/data")
        self.assertEqual(
            result.get_json(),
            {"error": "Invalid or no input. Please check your filename is valid."},
        )
        self.assertEqual(result.status_code, 400)

    def test_with_bad_input(self):
        result = self.app.get(
            "/api/data",
            query_string=dict(
                filekey="woofythedog/woofythedog_2019-04-14T00:22:47_stats.jso"
            ),
        )
        self.assertEqual(
            result.get_json(),
            {"error": "Your file was not found - please check your file name."},
        )
        self.assertEqual(result.status_code, 404)

    def test_with_empty_input(self):
        result = self.app.get("/api/data", query_string=dict(filekey=""))
        self.assertEqual(
            result.get_json(),
            {"error": "Your file was not found - please check your file name."},
        )
        self.assertEqual(result.status_code, 404)

#class NewTrackingRequestEndpoint(TestCase):
#
#    def setUp(self):
#        rs_api.app.testing = True
#        self.app = rs_api.app.test_client()
#        rs_api.s3r.Object = MagicMock()
#        rs_api.os.remove = MagicMock()
#        rs_api.open = MagicMock(name='this')
#
#    def test_add_existing_user(self):
#        result = self.app.put('/api/newtrackingrequest', query_string=dict(username='woofythedog'))
#        self.assertEqual(result.status_code, 400)
#        self.assertEqual(result.get_json(), 
#            {"error" : "User woofythedog already exists in the database."})