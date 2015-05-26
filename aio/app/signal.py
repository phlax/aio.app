import asyncio
import logging

from zope.dottedname.resolve import resolve

import aio.app


def listener(*la, **kwa):

    def wrapper(func):

        def wrapped(*la, **kwa):
            if asyncio.iscoroutinefunction(func):
                coro = func
            else:
                coro = asyncio.coroutine(func)
            try:
                result = yield from coro(*la)
            except Exception as e:
                # import traceback
                # traceback.print_exc()
                logging.getLogger('aio').error(
                    "Error calling listener: %s" % e)
                raise e
            return result
        wrapped.__annotations__['decorator'] = listener
        wrapped.__annotations__['function'] = func
        return wrapped

    if len(la) == 1 and callable(la[0]):
        return wrapper(la[0])
    return wrapper


def listener_checker(func):
    if not func.__annotations__.get("decorator") == listener:
        dotted_func = "%s.%s" % (func.__module__, func.__name__)
        raise RuntimeError(
            "Signal listener (%s) must be wrapped with " % dotted_func
            + "@aio.app.signal.listener")


def start_listeners(config):
    log = logging.getLogger("aio")
    log.debug('adding event listeners')

    try:
        listener_check = config["aio/signals"]["listener_check"]
        listener_check = resolve(listener_check)
    except (IndexError, KeyError):
        listener_check = None

    for s in config.sections():
        if s.startswith("listen/"):
            section = config[s]
            for signal, handlers in section.items():
                for handler in [h.strip() for h in handlers.split('\n')]:
                    handler = resolve(handler)
                    if listener_check:
                        listener_check(handler)
                    aio.app.signals.listen(signal, handler)
