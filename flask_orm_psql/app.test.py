from sqlalchemy import create_engine
import unittest

from init import create_app
from models import db


class AppTest(unittest.TestCase):
    """This class represents the app's test case"""

    def setUp(self):
        """Initialize the app with
           - test DB
           - setting up a web client
        """
        self.app = create_app("test")

        self.app.app_context().push()

        db.init_app(self.app)
        db.create_all()

        self.client = self.app.test_client


    def tearDown(self):
        """Reset logic:
           - reset DB after each test is run
        """
        engine = create_engine("postgresql://fl_user:fl_user@localhost:5432/todos_test")
        connection = engine.raw_connection()
        cursor = connection.cursor()
        command = "DROP TABLE todos, todos_lists;"
        cursor.execute(command)
        connection.commit()
        cursor.close()

    def test_get_unknown_url_returns_formatted_404(self):
        """Given a web user, when he hits /api/unknown with a GET request,
        then the response should have a status code of 404
        and the response body should contain the expected payload"""
        res = self.client().get('/api/unknown')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json["msg"], "resource not found, aborting...")
        self.assertEqual(res.json["data"], None)
        self.assertFalse(res.json["success"])

    def test_get_base_url_expected_payload(self):
        """Given a web user, when he hits /api with a get request,
           then the response should have a status code of 200"""
        res = self.client().get('/api')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["msg"], "todos api is up")
        self.assertEqual(res.json["data"], None)
        self.assertTrue(res.json["success"])



if __name__ == "__main__":
    unittest.main()
