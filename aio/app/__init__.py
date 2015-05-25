signals = None
config = None
modules = ()
servers = {}


def clear():
    import aio.app
    aio.app.signals = None
    aio.app.config = None
    aio.app.modules = ()

    for app_server in aio.app.servers.values():
        app_server.close()

    import logging
    del logging.root.handlers[:]
    logging.basicConfig()

    aio.app.servers = {}

from aio.app import server
server
