import os
import asyncio
import logging
import argparse
import configparser

from zope.dottedname.resolve import resolve

from aio.core.exceptions import MissingConfiguration
import aio.app
import aio.config

log = logging.getLogger('aio')


def schedule(name, func, cb, t, exc=None):
    log.info(
        'Scheduler started (%s): %s.%s' % (
            name, func.__module__, func.__name__))
    while True:
        if not asyncio.iscoroutinefunction(func):
            func = asyncio.coroutine(func)
        future = asyncio.async(func(name))

        def _cb(res):
            if res.exception():
                if exc:
                    asyncio.async(exc(res.exception()))
            else:
                if cb:
                    asyncio.async(cb(res.result()))

        future.add_done_callback(_cb)
        yield from asyncio.sleep(t)


@asyncio.coroutine
def server_factory(name, protocol, address, port):
    loop = asyncio.get_event_loop()
    return (
        yield from loop.create_server(
            protocol, address, port))


@asyncio.coroutine
def start_server(name, address="127.0.0.1", port=8080,
                 factory=None, protocol=None):

    if not port:
        raise MissingConfiguration(
            "Section [server/%s] must specify port to listen on" % name)

    if not factory and not protocol:
        message = (
            "Section [server/%s] must specify one of factory or "
            + "protocol to start server") % name
        raise MissingConfiguration(message)

    if not factory:
        factory = server_factory

    module = "%s.%s" % (factory.__module__, factory.__name__)

    try:
        res = yield from factory(name, protocol, address, port)
    except Exception as e:
        log.error("Server(%s) failed to start: %s" % (name, module))
        import traceback
        traceback.print_exc()
        raise e

    aio.app.servers[name] = res
    log.info(
        'Server(%s) %s started on %s:%s' % (
            name,
            module,
            address or "*", port))
    return res


@asyncio.coroutine
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
        yield from aio.config.dump_config(aio.app.config)
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
            log.info("Config file (%s) updated" % conf_file)

    asyncio.get_event_loop().stop()


@asyncio.coroutine
def cmd_run(argv):
    from aio.app import config

    # yield from app.signals.emit('aio-starting', None)
    log.debug('aio app starting')

    log.debug('adding event listeners')
    for s in config.sections():
        if s.startswith("listen/"):
            msg = s.split("/")[1].strip()
            section = config[s]
            for signal, handlers in section.items():
                for handler in [h.strip() for h in handlers.split('\n')]:
                    aio.app.signals.listen(signal, resolve(handler))

    log.debug('adding schedulers')
    for s in config.sections():
        if s.startswith("schedule/"):
            msg = s.split("/")[1].strip()
            section = config[s]
            every = section.get("every")
            func = resolve(section.get('func'))

            cb = section.get('cb', None)
            if cb:
                cb = resolve(cb)

            err = section.get('err', None)
            if err:
                err = resolve(err)

            log.debug("Starting scheduler: %s" % msg)
            asyncio.async(
                schedule(msg, func, cb, int(every), err))

    log.debug('adding servers')
    for s in config.sections():
        if s.startswith("server/"):
            name = s.split("/")[1].strip()
            section = config[s]
            factory = section.get('factory', None)
            if factory:
                factory = resolve(factory)
            protocol = section.get('protocol', None)
            if protocol:
                protocol = resolve(protocol)
            address = section.get('address')
            port = section.get('port')

            log.debug("Starting server: %s" % name)

            task = asyncio.async(
                start_server(
                    name, address, port, factory, protocol))

            def _server_started(res):
                if res.exception():
                    loop = asyncio.get_event_loop()
                    loop.stop()
                    log.error(res.exception())
                    raise res.exception()

            task.add_done_callback(_server_started)

    log.debug('aio app started')
    yield from aio.app.signals.emit('aio-started', None)
