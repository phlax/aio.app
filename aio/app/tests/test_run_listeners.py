import asyncio

import aio.testing
from aio.app.testing import AioAppTestCase
from aio.app.runner import runner
import aio.app

LISTENER_CONFIG = """
[listen/foo]
test-signal = aio.app.tests._test_listener
"""


class RunListenersTestCase(AioAppTestCase):

    @aio.testing.run_until_complete
    def test_run_listeners(self):
        """
        on run a listener for "test-signal" should be set up from config file
        """
        import aio.app

        class Result:
            message = None
        res = Result()

        @aio.app.signal.listener
        def test_listener(signal):
            res.message = "%s received: %s" % (
                signal.name, signal.data)

        aio.app.tests._test_listener = test_listener

        runner(
            ['run'],
            config_string=LISTENER_CONFIG)

        yield from aio.app.signals.emit('test-signal', 'BOOM!')

        self.assertEqual(
            res.message,
            'test-signal received: BOOM!')
        del aio.app.tests._test_listener
