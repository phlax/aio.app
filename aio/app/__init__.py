__version__ = "0.0.1"
signals = None
config = None
modules = ()


def clear():
    import aio.app
    aio.app.signals = None
    aio.app.config = None
    aio.app.modules = ()
