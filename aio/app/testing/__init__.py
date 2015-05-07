import unittest


class AioAppTestCase(unittest.TestCase):

    def tearDown(self):
        from aio import app
        if hasattr(app, "signals"):
            del(app.signals)
        if hasattr(app, "config"):
            del(app.config)
        if hasattr(app, "modules"):
            del(app.modules)
