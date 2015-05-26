import os
import io
from configparser import ConfigParser

import aio.app
import aio.testing
from aio.testing.contextmanagers import redirect_all
from aio.app.testing import AioAppTestCase
from aio.app.runner import runner
from aio.signals import Signals

TEST_DIR = os.path.dirname(__file__)


class RunnerTestCase(AioAppTestCase):

    @aio.testing.run_until_complete
    def test_runner_no_command(self):
        """
        with no args, runner reads config, but does not setup app
        help msg is printed to stdout
        """
        from aio import app

        with io.StringIO() as o, io.StringIO() as e, redirect_all(o, e):
            runner([])
            stdout = o.getvalue()

        # print help msg
        self.assertTrue(
            stdout.startswith(
                'usage: aio [-h] [-c [C]] {run,config,test}\n\naio'))

        # config has been loaded
        self.assertIsInstance(app.config, ConfigParser)

        # no signals have been set up
        self.assertIsNone(getattr(app, 'signals', None))

    @aio.testing.run_until_complete
    def test_runner_bad_command(self):
        from aio import app

        with io.StringIO() as o, io.StringIO() as e, redirect_all(o, e):
            runner(['BAD'])
            stdout = o.getvalue()
            stderr = e.getvalue()

        self.assertTrue(
            stderr.strip().endswith(
                "invalid choice: 'BAD' (choose from 'run', 'config', 'test')"))

        self.assertTrue(
            stdout.startswith(
                'usage: aio [-h] [-c [C]] {run,config,test}'))

        # config is set up
        self.assertIsInstance(app.config, ConfigParser)

        # signals are not
        self.assertIsNone(app.signals)

        # builtin modules are set up
        self.assertEqual(app.modules, (aio.app, ))

    @aio.testing.run_until_complete
    def test_runner_app_file_conf(self):
        from aio import app
        runner(
            ['run'], configfile=os.path.join(
                TEST_DIR, "resources", "test-1.conf"))
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
