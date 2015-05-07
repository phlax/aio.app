import os
import io
from configparser import ConfigParser

from aio.testing import aiotest
from aio.testing.contextmanagers import redirect_all
from aio.app.testing import AioAppTestCase
from aio.app.runner import runner
from aio.signals import Signals

TEST_DIR = os.path.dirname(__file__)


class RunnerTestCase(AioAppTestCase):

    @aiotest
    def test_runner_no_command(self):
        """
        with no args, runner reads config, but does not setup app
        help msg is printed to stdout
        """
        from aio import app
        conf = os.path.join(
            TEST_DIR, "resources", "test-1.conf")

        with io.StringIO() as o, io.StringIO() as e, redirect_all(o, e):
            yield from runner([], configfile=conf)
            stdout = o.getvalue()

        # print help msg
        self.assertEquals(
            stdout,
            ('usage: aio [-h] {test}\n\naio app runner'
             + '\n\npositional arguments:'
             + '\n  {test}      command to run\n\noptional arguments:'
             + '\n  -h, --help  show this help message and exit\n'))

        # config has been loaded
        self.assertIsInstance(app.config, ConfigParser)

        # no signals have been set up
        self.assertIsNone(getattr(app, 'signals', None))

    @aiotest
    def test_runner_bad_command(self):
        conf = os.path.join(
            TEST_DIR, "resources", "test-1.conf")
        from aio import app

        with io.StringIO() as o, io.StringIO() as e, redirect_all(o, e):
            yield from runner(['BAD'], configfile=conf)
            stdout = o.getvalue()
            stderr = e.getvalue()

        self.assertEquals(
            stderr,
            ("usage: aio [-h] {test}\naio: error: argument command: "
             + "invalid choice: 'BAD' (choose from 'test')\n"))

        self.assertEquals(
            stdout,
            ('usage: aio [-h] {test}\n\naio app runner'
             + '\n\npositional arguments:'
             + '\n  {test}      command to run\n\noptional arguments:'
             + '\n  -h, --help  show this help message and exit\n'))

        # config is set up
        self.assertIsInstance(app.config, ConfigParser)

        # signals are not
        self.assertIsNone(getattr(app, 'signals', None))

        # modules are not
        self.assertIsNone(getattr(app, 'modules', None))

    @aiotest
    def _test_runner_app_custom_conf(self):
        conf = os.path.join(
            TEST_DIR, "resources", "test-1.conf")
        from aio import app
        yield from runner([], configfile=conf)
        self.assertIsInstance(app.config, ConfigParser)
        self.assertIsInstance(app.signals, Signals)

    def tearDown(self):
        from aio import app
        if hasattr(app, "signals"):
            del(app.signals)
        if hasattr(app, "config"):
            del(app.config)
        if hasattr(app, "modules"):
            del(app.modules)
