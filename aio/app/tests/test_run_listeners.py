import asyncio

from aio.testing import aiotest
from aio.app.testing import AioAppTestCase
from aio.app.runner import runner

LISTENER_CONFIG = """
[listen/foo]
test-signal = aio.app.tests._test_listener
"""


class RunListenersTestCase(AioAppTestCase):

    @aiotest
    def test_run_listeners(self):
        """
        on run a listener for "test-signal" should be set up from config file
        """
        import aio.app

        class Result:
            message = None
        res = Result()

        @asyncio.coroutine
        def test_listener(signal, resp):
            res.message = "%s received: %s" % (
                signal, resp)

        aio.app.tests._test_listener = test_listener

        yield from runner(
            ['run'],
            config_string=LISTENER_CONFIG)

        yield from aio.app.signals.emit('test-signal', 'BOOM!')

        self.assertEqual(
            res.message,
            'test-signal received: BOOM!')
        del aio.app.tests._test_listener
