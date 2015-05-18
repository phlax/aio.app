aio.app
=======

Application runner for the aio_ asyncio framework

.. _aio: https://github.com/phlax/aio


Build status
------------

.. image:: https://travis-ci.org/phlax/aio.app.svg?branch=master
	       :target: https://travis-ci.org/phlax/aio.app


Installation
------------

Install with:

.. code:: bash

  pip install aio.app


Configuration
-------------

By default the aio command will look for the following configuration files

- aio.conf

- etc/aio.conf

- /etc/aio.conf

Once it has found a config file it uses that one

A custom configuration file can also be provide with "-c", eg

.. code:: bash

	  aio -c custom.conf run

A basic configuration with the 2 provided commands, test and run is

.. code:: ini

	  [aio:commands]
	  run = aio.app.cmd.cmd_run
	  test = aio.app.testing.cmd.cmd_test

aio run
-------

With the above configuration the app server can be run with

.. code:: bash

	  aio run

On startup the app server sets up the following

- Configuration - system-wide read-only configuration
- Modules - known modules
- Schedulers - functions called at set times
- Servers - listening on tcp/udp or other type of socket
- Signals - functions called in response to events

Configuration
~~~~~~~~~~~~~

The system configuration is importable from aio.app

.. code:: python

	  from aio.app import config


Modules
~~~~~~~

You can list any modules that should be imported at runtime in the configuration

.. code:: ini

	  [aio]
	  modules = aio.app
	          aio.signals

The system modules can be accessed from aio.app

.. code:: python

	  from aio.app import modules


Schedulers
----------

Any sections in the configuration that start with schedule: will create a scheduler.

Specify the frequency and the function to call. The function should be a co-routine.

.. code:: ini

	  [schedule:example]
	  every = 2
	  func = my.scheduler.example_scheduler

The scheduler function takes 1 argument the name of the scheduler

.. code:: python

	  @asyncio.coroutine
	  def example_scheduler(name):
	      # do something
	      pass

Servers
-------

Any sections in the configuration that start with server: will create a server

The server requires either a factory or a protocol to start

Protocol configuration example:


.. code:: ini

	  [server:example]
	  protocol = my.example.ServerProtocol
	  address = 127.0.0.1
	  port = 8888

Protocol example code:

.. code:: python

	  class ServerProtocol(asyncio.Protocol):

	      def connection_made(self, transport):
	          self.transport = transport

	      def data_received(self, data):
	          # do stuff
	          self.transport.close()

If you need further control over how the protocol is created and attached you can specify a factory method

Factory configuration example:

.. code:: ini

	  [server:example]
	  factory = my.example.server_factory
	  address = 127.0.0.1
	  port = 8080

Factory code example:

.. code:: python

	  @asyncio.coroutine
	  def server_factory(name, protocol, address, port):
	      loop = asyncio.get_event_loop()
	      return (
	          yield from loop.create_server(
		     ServerProtocol, address, port))


Signals
~~~~~~~

Any section in the configuration that starts with listen: will subscribe listed functions to given events

An example listen configuration section

.. code:: ini

	  [listen:example]
	  example-signal = my.example.listener

And an example listener function

.. code:: python

	  @asyncio.coroutine
	  def listener(signal, message):
	      print(message)

	  yield from app.signals.emit(
              'example-signal', "BOOM!")

You can add multiple subscriptions within the section

.. code:: ini

	  [listen:example]
	  example-signal = my.example.listener
	  example-signal-2 = my.example.listener2

You can also subscribe multiple functions to a signal

.. code:: ini

	  [listen:example]
	  example-signal = my.example.listener
	                 my.example.listener2


aio test
--------

Include the test command in your config

.. code:: ini

	  [aio]
	  modules = aio.app
	           aio.signals

	  [aio:commands]
	  test = aio.app.testing.cmd.cmd_test


The aio test runner will then test all modules listed in the aio config section

.. code:: bash

	  aio test

You can also specify a module

.. code:: bash

	  aio test aio.app


Dependencies
------------

aio.app depends on the following packages

- aio.core_
- aio.signals_
- aio.config_


Related software
----------------

- aio.http_
- aio.web_


.. _aio.core: https://github.com/phlax/aio.core
.. _aio.signals: https://github.com/phlax/aio.signals
.. _aio.config: https://github.com/phlax/aio.config

.. _aio.http: https://github.com/phlax/aio.http
.. _aio.web: https://github.com/phlax/aio.web
