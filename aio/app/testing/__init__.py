import unittest

import aio.app


class AioAppTestCase(unittest.TestCase):

    def setUp(self):
        super(AioAppTestCase, self).setUp()
        aio.app.clear()

    def tearDown(self):
        super(AioAppTestCase, self).tearDown()
        aio.app.clear()
