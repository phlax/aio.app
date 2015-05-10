import argparse
import asyncio

from zope.dottedname.resolve import resolve


@asyncio.coroutine
def runner(argv, app=None, configfile=None,
           signals=None, config_string=None):
    loop = asyncio.get_event_loop()

    if not app:
        app = resolve("aio.app")

    from aio import config

    app.config = yield from config.parse_config(
        config=configfile, config_string=config_string)
    commands = app.config['aio:commands']

    parser = argparse.ArgumentParser(
        prog="aio",
        description='aio app runner')
    parser.add_argument(
        "command", choices=commands,
        help="command to run")

    try:
        parsed_args = parser.parse_args([argv[0]])
    except (SystemExit, IndexError):
        parser.print_help()
        loop.stop()
        return

    from aio import signals as _signals, logging

    yield from logging.start_logging()

    app.signals = signals or _signals.Signals()

    app.modules = []
    try:
        _modules = app.config['aio']['modules']
        for m in _modules.strip('').split('\n'):
            app.modules.append(resolve(m))
    except KeyError:
        pass

    if parsed_args.command in commands:
        try:
            task = resolve(commands[parsed_args.command])
        except:
            import traceback
            traceback.print_exc()
            loop.stop()
        yield from task(argv[1:])
    else:
        parser.print_help()
        loop.stop()
