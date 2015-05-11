import asyncio
import argparse
from unittest import TestLoader, TestSuite, TextTestRunner

from zope.dottedname.resolve import resolve

from aio import app

import logging

log = logging.getLogger("aio.app.testing")


@asyncio.coroutine
def cmd_test(argv):
    loop = asyncio.get_event_loop()

    parser = argparse.ArgumentParser(
        prog="aio test",
        description='run aio tests')
    parser.add_argument(
        "module",
        nargs="?",
        default=None,
        choices=[
            m.__name__ for m in app.modules],
        help="module to test")

    try:
        argv = parser.parse_args(argv)
    except (SystemExit, IndexError):
        loop.stop()
        return

    if argv.module:
        log.info("Importing: %s" % argv.module)
        modules = [resolve(argv.module)]
    else:
        modules = app.modules

    app.clear()
    
    for module in modules:
        
        try:
            test_module = resolve("%s.tests" % module.__name__)
            
            suite = TestSuite()
            loader = TestLoader()
            this_dir = "%s/tests" % module.__path__[0]
            package_tests = loader.discover(start_dir=this_dir)
            suite.addTests(package_tests)
            
            print('Running tests for %s...' % module.__name__)
            print("------------------------------------------"
                  + "----------------------------")
            TextTestRunner(verbosity=2).run(suite)
            print("")
        except ImportError:
            print('No tests for %s' % module.__name__)
        except:
            import traceback
            traceback.print_exc()
    loop.stop()
