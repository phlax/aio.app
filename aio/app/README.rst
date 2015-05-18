

The aio command runner
----------------------

The aio command can be run with any commands listed in the [aio:commands] section of its configuration


Initially aio.app does not have any config, signals, modules or servers

  >>> import aio.app

  >>> print(aio.app.config)
  None

  >>> print(aio.app.signals)
  None

  >>> print(aio.app.modules)
  ()

  >>> print(aio.app.servers)
  {}
  
Lets start the app runner in a test loop with a minimal configuration

  >>> config = """
  ... [aio:commands]
  ... run: aio.app.cmd.cmd_run
  ... """

  >>> from aio.app.runner import runner

  >>> def run_app():
  ...     yield from runner(['run'], config_string=config)
  ...     print(aio.app.signals)
  ...     print(aio.app.config)  

  >>> from aio.testing import aiotest
  >>> aiotest(run_app)()
  <aio.signals.Signals object ...>
  <configparser.ConfigParser ...>


Clear the app
-------------

We can clear the app vars

  >>> aio.app.clear()

  >>> print(aio.app.signals)
  None

  >>> print(aio.app.config)
  None

  >>> print(aio.app.modules)
  ()

  >>> print(aio.app.servers)
  {}

  
Adding a signal listener
------------------------

  >>> def test_listener(signal, message):
  ...     print("Listener received: %s" % message)

  >>> import asyncio
  >>> aio.app.tests._test_listener = asyncio.coroutine(test_listener)

  >>> config = """
  ... [aio:commands]
  ... run: aio.app.cmd.cmd_run
  ... 
  ... [listen:testlistener]
  ... test-signal: aio.app.tests._test_listener
  ... """

  >>> def run_app_test_emit(msg):
  ...     yield from runner(['run'], config_string=config)  
  ...     yield from aio.app.signals.emit('test-signal', msg)
  
  >>> aiotest(run_app_test_emit)('BOOM!')
  Listener received: BOOM!
  
  >>> aio.app.clear()


Adding app modules
------------------

We can make the app runner aware of any modules that we want to include

  >>> config = """
  ... [aio]
  ... modules = aio.app
  ...          aio.core
  ...
  ... [aio:commands]
  ... run: aio.app.cmd.cmd_run
  ... """

  >>> def run_app_print_modules():
  ...     yield from runner(['run'], config_string=config)
  ...     print(aio.app.modules)

  >>> aiotest(run_app_print_modules)()
  [<module 'aio.app' from ...>, <module 'aio.core' from ...>]

  >>> aio.app.clear()


Running a scheduler
-------------------

We can schedule events in the configuration

  >>> def test_scheduler():
  ...      print('HIT!')

  >>> aio.app.tests._test_scheduler = asyncio.coroutine(test_scheduler)

  >>> from aio.testing import aiofuturetest

  >>> config = """
  ... [aio:commands]
  ... run: aio.app.cmd.cmd_run
  ... 
  ... [schedule:test]
  ... every: 2
  ... func: aio.app.tests._test_scheduler
  ... """
  
  >>> def run_app_scheduler():
  ...     yield from runner(['run'], config_string=config)
  
  >>> aiofuturetest(run_app_scheduler, timeout=5)()
  HIT!
  HIT!
  HIT!
  
  >>> aio.app.clear()

Running a server
----------------

Lets run an addition server

  >>> class AdditionServerProtocol(asyncio.Protocol):
  ... 
  ...     def connection_made(self, transport):
  ...         self.transport = transport
  ... 
  ...     def data_received(self, data):
  ...         self.transport.write(
  ...             str(
  ...                 sum([
  ...                     int(x.strip()) for x in
  ...         data.decode("utf-8").split("+")])).encode())
  ...         self.transport.close()
  
  >>> def addition_server(name, address, port):
  ...     loop = asyncio.get_event_loop()
  ...     return (
  ...         yield from loop.create_server(
  ...            AdditionServerProtocol,
  ...            address, port))

  >>> aio.app.tests._test_addition_server = asyncio.coroutine(addition_server)
  
  >>> config = """
  ... [aio:commands]
  ... run: aio.app.cmd.cmd_run
  ... 
  ... [server:additiontest]
  ... factory: aio.app.tests._test_addition_server
  ... address: 127.0.0.1
  ... port: 8888
  ... """

  >>> def run_app_addition(addition):
  ...     yield from runner(['run'], config_string=config)
  ... 
  ...     @asyncio.coroutine
  ...     def call_addition_server():
  ...          reader, writer = yield from asyncio.open_connection(
  ...              '127.0.0.1', 8888)
  ...          writer.write(addition.encode())
  ...          yield from writer.drain()
  ...   
  ...          result = yield from reader.read()
  ...          print(int(result))
  ... 
  ...     return call_addition_server

  >>> aiofuturetest(run_app_addition, timeout=5)('2 + 2 + 3')
  7


Running aio.test
----------------

To test aio modules add the test cmd in the application config, and make sure any modules that are to be tested are listed in the aio modules

  >>> config = """
  ... [aio]
  ... modules = aio.core
  ...         aio.app
  ... 
  ... [aio:commands]
  ... test: aio.app.cmd.cmd_test
  ... """

The aio test runner can then be run from the command line

  # aio test

You can also specify a module

 # aio test aio.app
