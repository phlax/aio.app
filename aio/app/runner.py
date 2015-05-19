import os
import argparse
import asyncio
import logging.config
from configparser import ConfigParser, ExtendedInterpolation
from collections import OrderedDict

from zope.dottedname.resolve import resolve

import aio.app
import aio.config
import aio.signals


@asyncio.coroutine
def start_logging():
    # combine system config with any logging config
    parser = ConfigParser(interpolation=ExtendedInterpolation())
    parser.read_dict(aio.config.replicate_config(aio.app.config))

    if os.path.exists('logging.conf'):
        parser.read_file(open('logging.conf'))

    # filter out the logging sections
    logging_sections = ['handler', 'logger', 'formatter']
    logging_config = aio.config.replicate_config(
        parser,
        test_section=lambda section: (
            any([section.startswith(x) for x in logging_sections])))

    logging_parser = ConfigParser()
    logging_parser.read_dict(logging_config)
    logging.config.fileConfig(logging_parser)


@asyncio.coroutine
def runner(argv, app=None, configfile=None,
           signals=None, config_string=None, search_for_config=False):
    loop = asyncio.get_event_loop()

    if not app:
        app = resolve("aio.app")

    parser = argparse.ArgumentParser(
        prog="aio",
        description='aio app runner')

    parser.add_argument(
        "-c", nargs="?",
        help="configuration file")

    parsed = parser.parse_known_args(argv)

    if parsed[0].c:
        configfile = parsed[0].c

    import aio.config

    # read default aio.app.config
    config = yield from aio.config.parse_config(
        modules=[aio.app])

    # read user config
    config = yield from aio.config.parse_config(
        config=configfile,
        config_string=config_string,
        parser=config,
        search_for_config=search_for_config)

    # load up builtins and modules
    app.modules = []

    try:
        _modules = config['aio']['builtin']
        for m in _modules.strip('').split('\n'):
            app.modules.append(resolve(m))
    except KeyError:
        pass

    try:
        _modules = config['aio']['modules']
        for m in _modules.strip('').split('\n'):
            app.modules.append(resolve(m))
    except KeyError:
        pass

    aio.app.modules = tuple(aio.app.modules)

    # read module config
    config = yield from aio.config.parse_config(
        modules=aio.app.modules, parser=config)

    # read user config again
    aio.app.config = yield from aio.config.parse_config(
        config=configfile,
        config_string=config_string,
        parser=config,
        search_for_config=search_for_config)

    commands = OrderedDict(
        app.config['aio:builtin_commands'])

    if "aio:commands" in app.config:
        commands.update(
            OrderedDict(app.config['aio:commands']))

    parser.add_argument(
        "command", choices=commands,
        help="command to run")
    parser.add_argument(
        'nargs',
        default=[],
        help=argparse.SUPPRESS,
        nargs="*")

    try:
        parsed_args = parser.parse_args(argv)
    except (SystemExit, IndexError):
        parser.print_help()
        loop.stop()
        return

    if parsed_args.command in commands:
        yield from start_logging()
        app.signals = signals or aio.signals.Signals()

        try:
            task = resolve(commands[parsed_args.command])
        except Exception as e:
            import traceback
            traceback.print_exc()
            # print(e)
            loop.stop()

        yield from task(parsed_args.nargs)

    else:
        parser.print_help()
        loop.stop()
