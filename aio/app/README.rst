

The aio command runner
----------------------

The aio command can be run with any commands listed in the [aio:commands] section of its configuration


Initially aio.app does not have any config, signals, modules or servers

  >>> import aio.app

  >>> print(aio.app.signals, aio.app.config, aio.app.modules, aio.app.servers)
  None None () {}


Lets start the app runner in a test loop with the default configuration and print out the signals and config objects

  >>> from aio.app.runner import runner

  >>> def run_app():
  ...     yield from runner(['run'])
  ... 
  ...     print(aio.app.signals)
  ...     print(aio.app.config)
  ...     print(aio.app.modules)
  ...     print(aio.app.servers)

  >>> from aio.testing import aiotest
  >>> import pdb; pdb.set_trace()
  >>> aiotest(run_app)()
  <aio.signals.Signals object ...>
  <configparser.ConfigParser ...>
  (<module 'aio.app' from ...>,)
  {}


Clear the app
-------------

We can clear the app vars

  >>> aio.app.clear()

  >>> print(aio.app.signals, aio.app.config, aio.app.modules, aio.app.servers)
  None None () {}


Adding a signal listener
------------------------

Lets create a test listener and make it importable

  >>> def test_listener(signal, message):
  ...     print("Listener received: %s" % message)

The listener needs to be a coroutine

  >>> import asyncio
  >>> aio.app.tests._test_listener = asyncio.coroutine(test_listener)

  >>> config = """
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
  ... """

  >>> def run_app_print_modules():
  ...     yield from runner(['run'], config_string=config)
  ...     print(aio.app.modules)

  >>> aiotest(run_app_print_modules)()
  (<module 'aio.app' from ...>, <module 'aio.core' from ...>)

  >>> aio.app.clear()


Running a scheduler
-------------------

Lets create a scheduler function. It needs to be a coroutine

  >>> def test_scheduler(name):
  ...      print('HIT: %s' % name)

  >>> aio.app.tests._test_scheduler = asyncio.coroutine(test_scheduler)

We need to use a aiofuturetest to wait for the scheduled events to occur

  >>> from aio.testing import aiofuturetest

  >>> config = """
  ... [schedule:test-scheduler]
  ... every: 2
  ... func: aio.app.tests._test_scheduler
  ... """

  >>> def run_app_scheduler():
  ...     yield from runner(['run'], config_string=config)

Running the test for 5 seconds we get 3 hits

  >>> aiofuturetest(run_app_scheduler, timeout=5)()
  HIT: test-scheduler
  HIT: test-scheduler
  HIT: test-scheduler

  >>> aio.app.clear()
  >>> del aio.app.tests._test_scheduler


Running a server
----------------

Lets set up and run an addition server

  >>> class AdditionServerProtocol(asyncio.Protocol):
  ... 
  ...     def connection_made(self, transport):
  ...         self.transport = transport
  ... 
  ...     def data_received(self, data):
  ...         nums = [
  ...            int(x.strip())
  ...            for x in
  ...            data.decode("utf-8").split("+")] 
  ...         self.transport.write(str(sum(nums)).encode())
  ...         self.transport.close()

  >>> aio.app.tests._test_AdditionServerProtocol = AdditionServerProtocol

  >>> config = """
  ... [server:additiontest]
  ... protocol: aio.app.tests._test_AdditionServerProtocol
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
  ...          result = yield from reader.read()
  ...   
  ...          print(int(result))
  ... 
  ...     return call_addition_server

  >>> addition = '2 + 2 + 3'
  >>> aiofuturetest(run_app_addition, timeout=5)(addition)
  7

  >>> aio.app.clear()
  >>> del aio.app.tests._test_AdditionServerProtocol

If you need more control over how the server protocol is created you can specify a factory instead

The factory method must be a coroutine

  >>> def addition_server_factory(name, protocol, address, port):
  ...     loop = asyncio.get_event_loop()
  ...     return (
  ...         yield from loop.create_server(
  ...            AdditionServerProtocol,
  ...            address, port))

  >>> aio.app.tests._test_addition_server_factory = asyncio.coroutine(addition_server_factory)
  
  >>> config = """
  ... [server:additiontest]
  ... factory = aio.app.tests._test_addition_server_factory
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
  ...          result = yield from reader.read()
  ...   
  ...          print(int(result))
  ... 
  ...     return call_addition_server

  >>> addition = '17 + 5 + 1'
  >>> aiofuturetest(run_app_addition, timeout=5)(addition)
  23
  
  >>> del aio.app.tests._test_addition_server_factory
