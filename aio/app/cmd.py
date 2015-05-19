import asyncio

from zope.dottedname.resolve import resolve
from aio import app
from aio.core.exceptions import MissingConfiguration

import logging

log = logging.getLogger('aio')


def schedule(name, func, cb, t, exc=None):
    log.info(
        'Scheduler started (%s): %s.%s' % (
            name, func.__module__, func.__name__))
    while True:
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
            "Section [server:%s] must specify port to listen on" % name)

    if not factory and not protocol:
        message = (
            "Section [server:%s] must specify one of factory or "
            + "protocol to start server") % name
        raise MissingConfiguration(message)

    if not factory:
        factory = server_factory

    module = "%s.%s" % (factory.__module__, factory.__name__)

    try:
        res = yield from factory(name, protocol, address, port)
    except Exception as e:
        log.error("Server(%s) failed to start: %s" % (name, module))
        raise e

    app.servers[name] = res
    log.info(
        'Server(%s) %s started on %s:%s' % (
            name,
            module,
            address, port))
    return res


@asyncio.coroutine
def cmd_run(argv):
    from aio.app import config

    # yield from app.signals.emit('aio-starting', None)
    log.debug('aio app starting')

    log.debug('adding event listeners')
    for s in config.sections():
        if s.startswith("listen:"):
            msg = s.split(":")[1].strip()
            section = config[s]
            for signal, handlers in section.items():
                for handler in [h.strip() for h in handlers.split('\n')]:
                    app.signals.listen(signal, resolve(handler))

    log.debug('adding schedulers')
    for s in config.sections():
        if s.startswith("schedule:"):
            msg = s.split(":")[1].strip()
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
        if s.startswith("server:"):
            name = s.split(":")[1].strip()
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
    yield from app.signals.emit('aio-started', None)
