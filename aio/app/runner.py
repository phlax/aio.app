import argparse

from collections import OrderedDict

from zope.dottedname.resolve import resolve

import aio.app
import aio.config
import aio.signals
import aio.app.logging


def start_listening(app, signals=None):
    app.signals = signals or aio.signals.Signals()


def load_modules(app, config):
    # load up builtins and modules
    app.modules = []

    try:
        _modules = [
            m.strip() for
            m in config['aio']['builtin'].strip('').split('\n')
            if m.strip()]
        for m in _modules:
            app.modules.append(resolve(m))
    except KeyError:
        pass

    try:
        _modules = [
            m.strip() for
            m in config['aio']['modules'].strip('').split('\n')
            if m.strip()]
        for m in _modules:
            app.modules.append(resolve(m))
    except KeyError:
        pass

    app.modules = tuple(app.modules)


def setup_config(app, config_file=None, config_string=None,
                 search_for_config=None):

    import aio.config

    # read default aio.app.config
    config = aio.config.parse_config(
        modules=[app])

    # read user config
    config = aio.config.parse_config(
        config=config_file,
        config_string=config_string,
        parser=config,
        search_for_config=search_for_config)

    load_modules(app, config)

    # read module config
    config = aio.config.parse_config(
        modules=app.modules, parser=config)

    # read user config again
    app.config = aio.config.parse_config(
        config=config_file,
        config_string=config_string,
        parser=config,
        search_for_config=search_for_config)


def get_commands(app):
    commands = OrderedDict(
        app.config['aio/builtin_commands'])
    if "aio/commands" in app.config:
        commands.update(
            OrderedDict(app.config['aio/commands']))
    return commands


def run_command(command, argv):
    return resolve(command)(argv)


def runner(argv, app=None, configfile=None,
           signals=None, config_string=None, search_for_config=False):
    app = app or resolve("aio.app")
    parser = argparse.ArgumentParser(
        prog="aio",
        description='aio app runner')
    parser.add_argument(
        "-c", nargs="?",
        help="configuration file")
    parsed = parser.parse_known_args(argv)

    if parsed[0].c:
        configfile = parsed[0].c
    setup_config(
        app,
        config_file=configfile,
        config_string=config_string,
        search_for_config=search_for_config)
    commands = get_commands(app)
    parser.add_argument(
        "command", choices=commands,
        help="command to run")
    try:
        parsed_args, remainder = parser.parse_known_args(argv)
    except (SystemExit, IndexError):
        parser.print_help()
        return
    except Exception as e:
        # import traceback
        # traceback.print_exc()
        print(repr(e))
        return

    if parsed_args.command in commands:
        start_listening(app, signals)
        run_command(commands[parsed_args.command], remainder)
    else:
        parser.print_help()
