

aio.app usage
-------------

The aio command can be run with any commands listed in the [aio/commands] section of its configuration

There are also 3 builtin commands - run, config and test

Initially aio.app does not have any config, signals, modules or servers

  >>> import aio.app

  >>> print(aio.app.signals, aio.app.config, aio.app.modules, aio.app.servers)
  None None () {}


Lets start the app runner in a test loop with the default configuration and print out the signals and config objects

  >>> from aio.testing import aiotest
  >>> from aio.app.runner import runner

  >>> @aiotest
  ... def run_app():
  ...     yield from runner(['run'])
  ... 
  ...     print(aio.app.signals)
  ...     print(aio.app.config)
  ...     print(aio.app.modules)
  ...     print(aio.app.servers)


  >>> run_app()
  <aio.signals.Signals object ...>
  <configparser.ConfigParser ...>
  (<module 'aio.app' from ...>,)
  {}


Clear the app
-------------

We can clear the app vars.

This will also close any socket servers that are currently running

  >>> aio.app.clear()

  >>> print(aio.app.signals, aio.app.config, aio.app.modules, aio.app.servers)
  None None () {}


Adding a signal listener
------------------------

We can add a signal listener in the app config

  >>> config = """
  ... [listen/testlistener]
  ... test-signal = aio.app.tests._example_listener
  ... """

Lets create a test listener and make it importable

The listener needs to be a coroutine

  >>> import asyncio

  >>> @asyncio.coroutine
  ... def listener(signal, message):
  ...     print("Listener received: %s" % message)

  >>> aio.app.tests._example_listener = listener

Running the test...

  >>> @aiotest 
  ... def run_app(message):
  ...     yield from runner(['run'], config_string=config)
  ...     yield from aio.app.signals.emit('test-signal', message)

  >>> run_app('BOOM!')
  Listener received: BOOM!

  >>> aio.app.clear()

We can also add listeners programatically

  >>> @aiotest 
  ... def run_app(message):
  ...     yield from runner(['run'])
  ... 
  ...     aio.app.signals.listen('test-signal-2', asyncio.coroutine(listener))
  ...     yield from aio.app.signals.emit('test-signal-2', message)

  >>> run_app('BOOM AGAIN!')
  Listener received: BOOM AGAIN!
  

Adding app modules
------------------

When you run the app with the default configuration, the only module listed is aio.app

  >>> @aiotest
  ... def run_app(config_string=None):
  ...     yield from runner(['run'], config_string=config_string)
  ...     print(aio.app.modules)

  >>> run_app()
  (<module 'aio.app' from ...>,)

  >>> aio.app.clear()

We can make the app runner aware of any modules that we want to include, these are imported at runtime

  >>> config = """
  ... [aio]
  ... modules = aio.app
  ...          aio.core
  ... """

  >>> run_app(config_string=config)
  (<module 'aio.app' from ...>, <module 'aio.core' from ...>)

  >>> aio.app.clear()


Running a scheduler
-------------------

A basic configuration for a scheduler

  >>> config = """
  ... [schedule/test-scheduler]
  ... every: 2
  ... func: aio.app.tests._example_scheduler
  ... """

Lets create a scheduler function and make it importable.

The scheduler function should be a coroutine

  >>> @asyncio.coroutine
  ... def scheduler(name):
  ...      print('HIT: %s' % name)

  >>> aio.app.tests._example_scheduler = scheduler

We need to use a aiofuturetest to wait for the scheduled events to occur

  >>> from aio.testing import aiofuturetest

  >>> @aiofuturetest(timeout=5)
  ... def run_app():
  ...     yield from runner(['run'], config_string=config)
    
Running the test for 5 seconds we get 3 hits

  >>> run_app()
  HIT: test-scheduler
  HIT: test-scheduler
  HIT: test-scheduler

  >>> aio.app.clear()


Running a server
----------------

Lets set up and run an addition server

At a minimum we should provide a protocol and a port to listen on

  >>> config_server_protocol = """
  ... [server/additiontest]
  ... protocol: aio.app.tests._example_AdditionServerProtocol
  ... port: 8888
  ... """

Lets create the server protocol and make it importable

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

  >>> aio.app.tests._example_AdditionServerProtocol = AdditionServerProtocol

After the server is set up, let's call it with a simple addition

  >>> @aiofuturetest
  ... def run_addition_server(config_string, addition):
  ...     yield from runner(['run'], config_string=config_string)
  ... 
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

  >>> run_addition_server(
  ...     config_server_protocol,
  ...     '2 + 2 + 3')
  7

  >>> aio.app.clear()

If you need more control over how the server protocol is created you can specify a factory instead

  >>> config_server_factory = """
  ... [server/additiontest]
  ... factory = aio.app.tests._example_addition_server_factory
  ... port: 8888
  ... """

The factory method must be a coroutine

  >>> @asyncio.coroutine
  ... def addition_server_factory(name, protocol, address, port):
  ...     loop = asyncio.get_event_loop()
  ...     return (
  ...         yield from loop.create_server(
  ...            AdditionServerProtocol,
  ...            address, port))

  >>> aio.app.tests._example_addition_server_factory = addition_server_factory

  >>> run_addition_server(
  ...     config_server_protocol,
  ...     '17 + 5 + 1')
  23
  
