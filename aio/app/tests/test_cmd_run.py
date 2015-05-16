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

test_dir = os.path.dirname(__file__)
        

@asyncio.coroutine
def test_listener(signal, resp):
    from aio import app
    yield from app.signals.emit(
        'test-signal-received',
        'Signal %s received with %s' % (signal, resp))


@asyncio.coroutine
def test_scheduler():
    from aio import app
    yield from app.signals.emit(
        'test-scheduled', "SCHEDULED TEST MESSAGE")


class RunCommandTestCase(AioAppTestCase):

    @aiotest
    def _test_run_command(self):
        """
        with no args, runner reads config, but does not setup app
        help msg is printed to stdout
        """
        from aio import app
        conf = os.path.join(
            test_dir, "resources", "test-2.conf")

        with io.StringIO() as out, redirect_all(out):
            yield from runner(['run'], configfile=conf)
            stdout = out.getvalue()

        self.assertEqual(stdout, "")

        # config has been loaded
        self.assertIsInstance(app.config, ConfigParser)

        # signals have been added
        self.assertIsInstance(app.signals, Signals)

    @aiotest
    def test_run_listeners(self):
        """
        on run a listener for "test-signal" should be set up from config file
        """
        from aio import app
        conf = os.path.join(
            test_dir, "resources", "test-3.conf")

        @asyncio.coroutine
        def run_tests(self, signal, res):
            self.assertEqual(res, 'Signal test-signal received with BOOM')

        @asyncio.coroutine
        def on_start(signal, res):
            # test that "test-signal" listener ha been setup from config file
            yield from app.signals.emit('test-signal', 'BOOM')

        signals = Signals()
        signals.listen('aio-started', on_start)
        signals.listen(
            'test-signal-received',
            functools.partial(run_tests, self))

        yield from runner(
            ['run'],
            configfile=conf,
            signals=signals)

    @aiofuturetest
    def test_run_schedulers(self):
        conf = os.path.join(
            test_dir, "resources", "test-4.conf")

        class Counter:
            hit_count = 0
        counter = Counter()

        @asyncio.coroutine
        def scheduled(signal, res):
            counter.hit_count += 1

        signals = Signals()
        signals.listen('test-scheduled', scheduled)

        yield from runner(
            ['run'],
            configfile=conf,
            signals=signals)

        @asyncio.coroutine
        def test_complete():
            self.assertTrue(
                counter.hit_count > 2)

        return test_complete
