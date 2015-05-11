import unittest


class AioAppTestCase(unittest.TestCase):

    def tearDown(self):
        from aio import app
        app.clear()
