import os
import io
import asyncio
import functools
from configparser import ConfigParser

from aio.testing import aiotest, aiofuturetest
from aio.testing.contextmanagers import redirect_all
from aio.app.testing import AioAppTestCase
from aio.app.runner import runner
from aio.signals import Signals
from aio.core.exceptions import MissingConfiguration

LISTENER_CONFIG = """
[aio:commands]
run: aio.app.cmd.cmd_run

[listen:foo]
test-signal: aio.app.tests._test_listener
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