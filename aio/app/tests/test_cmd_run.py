import os
import io
from configparser import ConfigParser

from aio.testing import aiotest
from aio.testing.contextmanagers import redirect_all
from aio.app.testing import AioAppTestCase
from aio.app.runner import runner
from aio.signals import Signals

test_dir = os.path.dirname(__file__)


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
