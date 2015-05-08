import asyncio
import argparse
from unittest import TestLoader, TestSuite, TextTestRunner

from zope.dottedname.resolve import resolve

from aio import app


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
        modules = [resolve(argv.module[0])]
    else:
        modules = app.modules

    # remove setup configuration
    if hasattr(app, "signals"):
        del(app.signals)
    if hasattr(app, "config"):
        del(app.config)
    if hasattr(app, "modules"):
        del(app.modules)

    for module in modules:
        try:
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
