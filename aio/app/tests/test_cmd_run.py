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

test_dir = os.path.dirname(__file__)


@asyncio.coroutine
def test_listener(signal, resp):
    from aio import app
    yield from app.signals.emit(
        'test-signal-received',
        'Signal %s received with %s' % (signal, resp))


@asyncio.coroutine
def test_scheduler(name):
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


class RunCommandListenersTestCase(AioAppTestCase):

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
            # test that "test-signal" listener has been setup from config file
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


class RunCommandSchedulersTestCase(AioAppTestCase):

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

SERVER_CONFIG_NO_FACTORY_OR_PROTOCOL = """
[aio:commands]
run: aio.app.cmd.cmd_run

[server:test]
port: 8080
address: 127.0.0.1
"""

SERVER_CONFIG_FACTORY = """
[aio:commands]
run: aio.app.cmd.cmd_run

[server:test]
port: 8080
address: 127.0.0.1
factory: aio.app.tests.test_addition_server
"""

SERVER_CONFIG_PROTOCOL = """
[aio:commands]
run: aio.app.cmd.cmd_run

[server:test]
port: 8080
address: 127.0.0.1
protocol: aio.app.tests.AdditionTestServerProtocol
"""
    

class RunCommandServersTestCase(AioAppTestCase):

    def test_run_servers_no_factory_or_protocol(self):

        def run_server():            
            res = yield from runner(
                ['run'],
                config_string=SERVER_CONFIG_NO_FACTORY_OR_PROTOCOL)

        with self.assertRaises(MissingConfiguration):
            aiofuturetest(run_server)()

    @aiofuturetest        
    def test_run_servers_factory(self):
        res = yield from runner(
            ['run'],
            config_string=SERVER_CONFIG_FACTORY)
        
        @asyncio.coroutine
        def test_cb():
            reader, writer = yield from asyncio.open_connection(
                '127.0.0.1', 8080)
            writer.write(b'2 + 2 + 3')
            yield from writer.drain()     
            result = yield from reader.read()
            self.assertEqual(int(result), 7)

        return test_cb

    @aiofuturetest        
    def test_run_servers_protocol(self):
        res = yield from runner(
            ['run'],
            config_string=SERVER_CONFIG_PROTOCOL)
        
        @asyncio.coroutine
        def test_cb():
            reader, writer = yield from asyncio.open_connection(
                '127.0.0.1', 8080)
            writer.write(b'2 + 2 + 3')
            yield from writer.drain()     
            result = yield from reader.read()
            self.assertEqual(int(result), 7)

        return test_cb
    
        
