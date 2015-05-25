import asyncio
import logging
import inspect


def factory(*la, **kwa):

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
                    "Error starting server: %s" % e)
                raise e
            return result
        wrapped.__annotations__['decorator'] = factory
        wrapped.__annotations__['function'] = func
        return wrapped

    if len(la) == 1 and callable(la[0]):
        return wrapper(la[0])
    return wrapper


def factory_checker(func):
    if not func.__annotations__.get("decorator") == factory:
        dotted_func = "%s.%s" % (func.__module__, func.__name__)
        raise RuntimeError(
            "Server factory (%s) must be wrapped with " % dotted_func
            + "@aio.app.server.factory")


def protocol(*la, **kwa):
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
                    "Error starting server: %s" % e)
                raise e
            return result
        wrapped.__annotations__['decorator'] = protocol
        wrapped.__annotations__['function'] = func
        return wrapped

    if len(la) == 1 and callable(la[0]):
        return wrapper(la[0])
    return wrapper


def protocol_checker(func):
    if inspect.isclass(func) and issubclass(func, asyncio.Protocol):
        return

    if not func.__annotations__.get("decorator") == protocol:
        dotted_func = "%s.%s" % (func.__module__, func.__name__)
        raise RuntimeError(
            "Server factory (%s) must be wrapped with " % dotted_func
            + "@aio.app.server.factory")
