import sys
import asyncio
import argparse
import os
import doctest
import functools
from unittest import (
    TestLoader, TestSuite, TextTestRunner)

from zope.dottedname.resolve import resolve

import aio.app

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
            choices=[m.__name__ for m in aio.app.modules],
            help="module to test")

        try:
            parsed = parser.parse_args(argv)
        except (SystemExit, IndexError):
            loop.stop()

        modules = []
        for module in parsed.modules:
            log.debug("Importing: %s" % module)
            modules.append(resolve(module))
    else:
        if aio.app.config.get("aio/testing", "modules"):
            modules = [
                resolve(module.strip()) for module
                in aio.app.config["aio/testing"]["modules"].split("\n")
                if module.strip()]
        else:
            modules = aio.app.modules

    aio.app.clear()

    errors = 0

    def setUp(module, self):
        aio.app.clear()

    def tearDown(module, self):
        aio.app.clear()
        for attr in dir(module):
            if attr.startswith('_example_'):
                delattr(module, attr)

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
                    setUp=functools.partial(setUp, test_module),
                    tearDown=functools.partial(tearDown, test_module),
                    optionflags=doctest.ELLIPSIS))
            package_tests = loader.discover(start_dir=this_dir)
            suite.addTests(package_tests)

            print('Running tests for %s...' % module.__name__)
            print("------------------------------------------"
                  + "----------------------------")
            result = TextTestRunner(verbosity=2).run(suite)
            aio.app.clear()
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
