import asyncio
import logging
import inspect

from zope.dottedname.resolve import resolve

from aio.core.exceptions import MissingConfiguration
import aio.app


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


@asyncio.coroutine
def server_factory(name, protocol, address, port):
    loop = asyncio.get_event_loop()
    return (
        yield from loop.create_server(
            protocol, address, port))


@asyncio.coroutine
def start_server(name, address="127.0.0.1", port=8080,
                 factory=None, protocol=None):
    log = logging.getLogger("aio")

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

    if "function" in factory.__annotations__:
        original_function = factory.__annotations__['function']
    else:
        original_function = factory
    module = "%s.%s" % (
        original_function.__module__,
        original_function.__name__)

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
def start_servers(config):
    log = logging.getLogger("aio")
    log.debug('adding servers')
    try:
        factory_check = config["aio/server"]["factory_check"]
        factory_check = resolve(factory_check)
    except (IndexError, KeyError):
        factory_check = None

    try:
        protocol_check = config["aio/server"]["protocol_check"]
        protocol_check = resolve(protocol_check)
    except (IndexError, KeyError):
        protocol_check = None

    for s in config.sections():
        if s.startswith("server/"):
            name = s.split("/")[1].strip()
            section = config[s]
            factory = section.get('factory', None)
            if factory:
                factory = resolve(factory)
                if factory_check:
                    factory_check(factory)
            protocol = section.get('protocol', None)
            if protocol:
                protocol = resolve(protocol)
                if protocol_check:
                    protocol_check(protocol)
            address = section.get('address')
            port = section.get('port')

            log.debug("Starting server: %s" % name)

            task = asyncio.async(
                aio.app.server.start_server(
                    name, address, port, factory, protocol))

            def _server_started(res):
                if res.exception():
                    loop = asyncio.get_event_loop()
                    loop.stop()
                    log.error(res.exception())
                    raise res.exception()

            task.add_done_callback(_server_started)
