import os
import io
import asyncio
import functools
from configparser import ConfigParser

import aio.app
from aio.testing import aiotest, aiofuturetest
from aio.testing.contextmanagers import redirect_all
from aio.app.testing import AioAppTestCase
from aio.app.runner import runner
from aio.signals import Signals
from aio.core.exceptions import MissingConfiguration

test_dir = os.path.dirname(__file__)

SCHEDULER_CONFIG = """
[aio:commands]
run: aio.app.cmd.cmd_run

[schedule:test]
every: 2
func: aio.app.tests._test_scheduler
"""
    

class RunCommandSchedulersTestCase(AioAppTestCase):

    @aiofuturetest
    def test_run_schedulers(self):

        class Counter:
            hit_count = 0
        counter = Counter()
        
        @asyncio.coroutine
        def scheduler(name):
            counter.hit_count += 1

        aio.app.tests._test_scheduler = scheduler
        
        yield from runner(
            ['run'],
            config_string=SCHEDULER_CONFIG)

        @asyncio.coroutine
        def test_complete():
            self.assertTrue(counter.hit_count == 3)

        return test_complete
