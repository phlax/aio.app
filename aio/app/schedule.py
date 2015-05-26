import asyncio
import logging

from zope.dottedname.resolve import resolve

import aio.app


class ScheduledEvent(object):

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def config(self):
        return aio.app.config["schedule/%s" % self.name]


def schedule(name, func, cb, t, exc=None):
    log = logging.getLogger("aio")
    log.info(
        'Scheduler started (%s): %s.%s' % (
            name, func.__module__, func.__name__))
    while True:
        if not asyncio.iscoroutinefunction(func):
            func = asyncio.coroutine(func)
        future = asyncio.async(func(ScheduledEvent(name)))

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
def start_schedulers(config):
    log = logging.getLogger("aio")
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
                aio.app.schedule.schedule(
                    msg, func, cb, int(every), err))
