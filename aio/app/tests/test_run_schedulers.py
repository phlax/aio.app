import os
import asyncio

import aio.app
import aio.testing
from aio.app.testing import AioAppTestCase
from aio.app.runner import runner

test_dir = os.path.dirname(__file__)

SCHEDULER_CONFIG = """
[schedule/test]
every: 2
func: aio.app.tests._test_scheduler
"""


class RunCommandSchedulersTestCase(AioAppTestCase):

    @aio.testing.run_forever(timeout=5)
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
            # this is called 5 seconds after the server has started
            self.assertTrue(counter.hit_count == 3)

        return test_complete
