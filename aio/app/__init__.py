signals = None
config = None
modules = ()
servers = {}


def clear():
    import aio.app
    aio.app.signals = None
    aio.app.config = None
    aio.app.modules = ()

    for server in aio.app.servers.values():
        server.close()

    import logging
    del logging.root.handlers[:]
    logging.basicConfig()
    
    aio.app.servers = {}
