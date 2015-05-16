
import asyncio

from zope.dottedname.resolve import resolve
from aio import app

import logging

log = logging.getLogger('aio')


def schedule(func, cb, t, exc=None):
    log.info(
        'Scheduler started: %s.%s' % (func.__module__, func.__name__))
    while True:
        future = asyncio.async(func())

        def _cb(res):
            if res.exception():
                asyncio.async(exc(res.exception()))
            else:
                asyncio.async(cb(res.result()))

        future.add_done_callback(_cb)
        yield from asyncio.sleep(t)


@asyncio.coroutine
def start_server(name, factory, address="127.0.0.1", port=8080):
    module = "%s.%s" % (factory.__module__, factory.__name__)

    try:
        res = yield from factory(name, address, port)
    except Exception as e:
        import traceback
        traceback.print_exc()        
        log.error("Server(%s) %s failed to start" % (name, module))
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
                schedule(func, cb, int(every), err))

    log.debug('adding servers')
    for s in config.sections():
        if s.startswith("server:"):
            name = s.split(":")[1].strip()
            section = config[s]
            factory = resolve(section.get('factory'))
            address = section.get('address')
            port = section.get('port')
            log.debug("Starting server: %s" % name)

            task = asyncio.async(
                start_server(
                    name, factory, address, port))

            def _server_started(res):
                if res.exception():
                    loop = asyncio.get_event_loop()
                    loop.stop()
                    raise res.exception()
                    
            task.add_done_callback(_server_started)

    log.info('aio app started')
    yield from app.signals.emit('aio-started', None)

