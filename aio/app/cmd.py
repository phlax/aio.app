import os
import asyncio
import logging
import argparse
import configparser
import lockfile

from daemon import runner, daemon

import aio.app
import aio.config


def cmd_config(argv):

    parser = argparse.ArgumentParser(
        prog="aio config",
        description='aio configuration')

    parser.add_argument(
        "-f",
        nargs=1,
        help=(
            "Configuration file to get/set values from. "
            + "Values are not interpolated if you set this"))

    parser.add_argument(
        "-g", "--get",
        nargs=1,
        help="Get a config value")

    parser.add_argument(
        "-s", "--set",
        nargs=2,
        help="Set a config value")

    parsed = parser.parse_args(argv)

    if parsed.set and parsed.get:
        parser.print_help()
        raise Exception(
            "Please use either -g (--get) or -s (--set) "
            + "with aio config, not both")

    if not parsed.set and not parsed.get:
        aio.config.dump_config(aio.app.config)
    else:
        if parsed.get:
            if parsed.f:
                config = configparser.RawConfigParser()
                config.read_file(open(parsed.f[0]))
            else:
                config = aio.app.config

            if ":" in parsed.get[0]:
                section = parsed.get[0].split(":")[0]
                option = parsed.get[0].split(":")[1]
            else:
                section = parsed.get[0]
                option = None
            if option:
                print(config[section][option])
            else:
                for option_name, option in config[section].items():
                    print(
                        "%s = %s" % (
                            option_name,
                            option.replace("\n", "\n\t")))
        else:
            k, v = parsed.set

            if ":" not in k:
                parser.print_help()
                raise Exception(
                    'Please specify a "section:key" to set the value for')

            conf_file = parsed.f or aio.config.find_config()
            if not conf_file:
                conf_file = os.path.abspath('aio.conf')

            config_parser = configparser.RawConfigParser()
            config_parser.read_file(open(conf_file))
            section = k.split(":")[0]
            option = k.split(":")[1]

            if section not in config_parser.sections():
                config_parser.add_section(section)

            # not sure if this is the correct way to unescape str
            v = bytes(v, 'utf-8').decode('unicode-escape')

            # now lets replace any newlines with
            # a newline + tab to ensure its treated as multi-line
            v.replace("\n", "\n\t")
            config_parser[section][option] = v
            config_parser.write(open(conf_file, "w"))
            log = logging.getLogger('aio')
            log.info("Config file (%s) updated" % conf_file)


@asyncio.coroutine
def app_start():
    from aio.app import config
    log = logging.getLogger('aio')
    log.debug('aio app starting')
    yield from aio.app.signals.emit('aio-starting', None)
    yield from aio.app.schedule.start_schedulers(config)
    yield from aio.app.server.start_servers(config)
    yield from aio.app.signals.emit('aio-started', None)
    log.debug('aio app started')
    return 3


def app_runner():
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.async(app_start())
    if not loop.is_running():
        loop.run_forever()


def cmd_run(argv):
    parser = argparse.ArgumentParser(
        prog="aio run",
        description='aio app runner')
    parser.add_argument(
        "-d", action="store_true",
        help="daemonize process")
    parsed, remainder = parser.parse_known_args()

    aio.app.logging.start_logging(aio.app.config)
    aio.app.signal.start_listeners(aio.app.config)

    if parsed.d:
        pidfile = runner.make_pidlockfile(
            os.path.abspath('var/run/aio.pd'), 1)

        if runner.is_pidfile_stale(pidfile):
            pidfile.break_lock()

        if pidfile.is_locked():
            print(
                "There seems to be another aio process running "
                + "already, stop that one first")
            exit()

        class open_logs:

            def __enter__(self):
                return (
                    open("var/log/aio.log", "a"),
                    open("var/log/aio.log", "a"))

            def __exit__(self, *la):
                pass

        with open_logs() as (stdout, stderr):
            daemon_context = dict(
                stdout=stdout,
                stderr=stderr,
                working_directory=os.getcwd(),
                pidfile=pidfile)
            dc = daemon.DaemonContext(**daemon_context)
            try:
                dc.open()
                app_runner()
            except lockfile.AlreadyLocked:
                print('LOCKFILE LOCKED')
    else:
        app_runner()
