import rs_tracker_api
import unittest


class MyTestCase(unittest.TestCase):

    def setUp(self):
        rs_tracker_api.app.testing = True
        self.app = rs_tracker_api.app.test_client()

    def test_home(self):
        result = self.app.get('/')
        
