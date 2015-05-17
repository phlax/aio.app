signals = None
config = None
modules = ()
servers = {}


def clear():
    import aio.app
    aio.app.signals = None
    aio.app.config = None
    aio.app.modules = ()
    aio.app.servers = {}
