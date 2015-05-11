=======
aio.app
=======


Installation
------------

Install with:

  pip install aio.app

Configuration
-------------

By default the aio command will look for the following configuration files

   - aio.conf
   
   - etc/aio.conf
   
   - /etc/aio.conf

Once it has found a config file it uses that one


The aio command
---------------

the aio command can be run with any commands listed in the [aio:commands] section of its configuration

a minimal configuration for the app runner is

  >>> CONFIG = """
  ... [aio:commands]
  ... run: aio.app.cmd.cmd_run
  ... """

This will allow you to run the app runner with following command

 # aio run

Running
-------

  >>> import aio.app

Initially aio.app does not have any config

  >>> print(aio.app.config)
  None

There are no signals set up for the app

  >>> print(aio.app.signals)
  None

And the app is not aware of any modules

  >>> aio.app.modules
  ()


The app runner needs to be run in an async function

  >>> from aio.app.runner import runner
  
  >>> def run_app():
  ...    yield from runner(['run'], config_string=CONFIG)

Lets run the app in a test loop

  >>> from aio.testing import aiotest
  >>> aiotest(run_app)()

Now the aio.app module should have signals set up

  >>> aio.app.signals
  <aio.signals.Signals object ...>

  >>> aio.app.config
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


Adding a signal listener
------------------------

  >>> CONFIG = """
  ... [aio:commands]
  ... run: aio.app.cmd.cmd_run
  ... 
  ... [listen:testlistener]
  ... test-signal: aio.app.tests.test_cmd_run.test_listener
  ... """
  
  >>> aiotest(run_app)()

  >>> aio.app.signals._signals
  {'test-signal': {<function test_listener at ...>}}

  >>> aio.app.clear()


Adding app modules
------------------

We can make the app runner aware of any modules that we want to include

  >>> CONFIG = """
  ... [aio]
  ... modules = aio.app
  ...          aio.core
  ... 
  ... [aio:commands]
  ... run: aio.app.cmd.cmd_run
  ... """

  >>> aiotest(run_app)()  
  
These modules are imported at runtime and stored in the aio.app.modules var

  >>> aio.app.modules
  [<module 'aio.app' from ...>, <module 'aio.core' from ...>]

  >>> aio.app.clear()


Passing a signals object to the runner
--------------------------------------

We can start the runner with a custom signals object

  >>> def scheduled(signal, res):
  ...      pass

  >>> import asyncio
  >>> from aio.signals import Signals
  >>> signals = Signals()
  >>> signals.listen('test-scheduled', asyncio.coroutine(scheduled))
  
  >>> def run_app():
  ...    yield from runner(['run'], config_string=CONFIG, signals=signals)

  >>> aiotest(run_app)()
  
  >>> aio.app.signals._signals
  {'test-scheduled': {<function scheduled at ...>}}

  >>> aio.app.clear()
  
  
Running a scheduler
-------------------

We can schedule events in the configuration

  >>> CONFIG = """
  ... [aio:commands]
  ... run: aio.app.cmd.cmd_run
  ... 
  ... [schedule:test]
  ... every: 2
  ... func: aio.app.tests.test_cmd_run.test_scheduler  
  ... """

We can listen for the scheduled event and increment a counter
  
  >>> class Counter:
  ...     hit_count = 0
  >>> counter = Counter()

  >>> def scheduled(signal, res):
  ...      counter.hit_count += 1

  >>> signals = Signals()  
  >>> signals.listen('test-scheduled', asyncio.coroutine(scheduled))
  
To catch scheduled events we need to use a future test

  >>> from aio.testing import aiofuturetest

After running the app for 5 seconds

  >>> aiofuturetest(run_app, timeout=5)()

  >>> counter.hit_count
  3

  >>> aio.app.clear()
  
Running a server
----------------

Lets run an echo server

  >>> CONFIG = """
  ... [aio:commands]
  ... run: aio.app.cmd.cmd_run
  ... 
  ... [server:echotest]
  ... factory: aio.app.tests.test_cmd_run.test_echo_server
  ... address: 127.0.0.1
  ... port: 8888
  ... """

And define an object to collect the results

  >>> class Response:
  ...     message = None
  >>> response = Response()

And lets create an async test to send a message to the echo server once its running
  
  >>> def run_future_app():
  ...     yield from runner(['run'], config_string=CONFIG)
  ... 
  ...     @asyncio.coroutine
  ...     def _test_echo():
  ...          reader, writer = yield from asyncio.open_connection('127.0.0.1', 8888)
  ...          writer.write(b'Hello World!')
  ...          yield from writer.drain()
  ...          response.message = (yield from reader.read())
  ... 
  ...     return _test_echo

And lets run the test

  >>> aiofuturetest(run_future_app, timeout=5)()
  >>> response.message
  b'Hello World!'


Running aio.test
----------------

To test aio modules add the test cmd in the application config, and make sure any modules that are to be tested are listed in the aio modules

  >>> CONFIG = """
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
