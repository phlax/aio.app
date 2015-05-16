import sys
import asyncio
import argparse
import os
import doctest
import functools
from unittest import (
    TestLoader, TestSuite, TextTestRunner)

from zope.dottedname.resolve import resolve

from aio import app

import logging

log = logging.getLogger("aio.app.testing")


@asyncio.coroutine
def cmd_test(argv):
    loop = asyncio.get_event_loop()

    if argv:
        parser = argparse.ArgumentParser(
            prog="aio test",
            description='run aio tests')
        parser.add_argument(
            "modules",
            nargs="*",
            default=None,
            choices=[m.__name__ for m in app.modules],
            help="module to test")

        try:
            parsed = parser.parse_args(argv)
        except (SystemExit, IndexError):
            loop.stop()

        modules = []
        for module in parsed.modules:
            log.info("Importing: %s" % module)
            modules.append(resolve(module))
    else:
        modules = app.modules

    app.clear()

    errors = 0

    for module in modules:

        try:
            test_module = resolve("%s.tests" % module.__name__)
            suite = TestSuite()
            loader = TestLoader()
            this_dir = "%s/tests" % module.__path__[0]
            readme = "%s/README.rst" % module.__path__[0]
            if os.path.exists(readme):
                suite.addTest(doctest.DocFileSuite(
                    readme,
                    module_relative=False,
                    optionflags=doctest.ELLIPSIS))
            package_tests = loader.discover(start_dir=this_dir)
            suite.addTests(package_tests)

            print('Running tests for %s...' % module.__name__)
            print("------------------------------------------"
                  + "----------------------------")
            result = TextTestRunner(verbosity=2).run(suite)
            print("")
            if result.failures or result.errors:
                errors += 1
        except ImportError:
            print('No tests for %s' % module.__name__)
        except:
            import traceback
            traceback.print_exc()
            errors += 1

    if errors:
        loop.stop()
        sys.exit(1)
    loop.stop()
