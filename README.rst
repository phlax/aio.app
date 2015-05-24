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

Requires python >= 3.4 to work

Install with:

.. code:: bash

	  pip install aio.app


Quick start - hello world scheduler
-----------------------------------

Save the following into a file "hello.conf"

.. code:: ini
	  
	  [schedule/EXAMPLE]
	  every = 2
	  func = my_example.schedule_handler

And save the following into a file named "my_example.py"	  
	  
.. code:: python

	  import asyncio
	  
	  @asyncio.coroutine
	  def schedule_handler(name):
	      print ("Received scheduled: %s" % name)

Run with the aio run command

.. code:: bash

	  aio run -c hello.conf
	  
	  
Running an aio app
------------------

You can run an aio app as follows:

.. code:: bash

	  aio run

Or with a custom configuration file
	  
.. code:: bash

	  aio -c custom.conf run

	  
If you run the command without specifying a configuration file the aio command will look look for one in the following places on your filesystem

- aio.conf
- etc/aio.conf
- /etc/aio/aio.conf
  

The *aio run* command
---------------------

On startup aio run sets up the following

- Configuration - system-wide configuration
- Modules - initialization and configuration of modules
- Logging - system logging policies  
- Schedulers - functions called at set times
- Servers - listening on tcp/udp or other type of socket
- Signals - functions called in response to events


Configuration
~~~~~~~~~~~~~

Configuration is in ini syntax

.. code:: ini

	  [aio]
	  modules = aio.app
	          aio.signals

While the app is running the system configuration is importable from aio.app

.. code:: python

	  from aio.app import config

Configuration is parsed using ExtendedInterpolation_ as follows

- aio.app defaults read
- user configuration read to initialize modules
- "aio.conf" read from initialized modules where present
- user configuration read again to ensure for precedence


Logging
~~~~~~~

Logging policies can be placed in the configuration file, following pythons fileConfig_ format

.. _fileConfig: https://docs.python.org/3/library/logging.config.html#logging-config-fileformat

As the configuration is parsed with ExtendedInterpolation_ you can use options from other sections

.. code:: ini

	  [logger_root]
	  level=${aio:log_level}
	  handlers=consoleHandler
	  qualname=aio

The default aio:log_level is INFO
	  

Modules
~~~~~~~

You can list any modules that should be imported at runtime in the configuration

Default configuration for each of these modules is read from a file named aio.conf in the module's path, if it exists.

The system modules can be accessed from aio.app

.. code:: python

	  from aio.app import modules


Schedulers
~~~~~~~~~~

Any sections in the configuration that start with "schedule/" will create a scheduler.

Specify the frequency and the function to call. The function should be a co-routine.

.. code:: ini

	  [schedule/example]
	  every = 2
	  func = my.scheduler.example_scheduler

The scheduler function takes 1 argument the name of the scheduler

.. code:: python

	  @asyncio.coroutine
	  def example_scheduler(name):
              yield from asyncio.sleep(2)
	      # do something
	      pass

Servers
~~~~~~~

Any sections in the configuration that start with "server/" will create a server

The server requires either a factory or a protocol to start

Protocol configuration example:

.. code:: ini

	  [server/example]
	  protocol = my.example.ServerProtocol
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

	  [server/example]
	  factory = my.example.server_factory
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

Any section in the configuration that starts with "listen/" will subscribe listed functions to given events

An example listen configuration section

.. code:: ini

	  [listen/example]
	  example-signal = my.example.listener

And an example listener function

.. code:: python

	  @asyncio.coroutine
	  def listener(signal, message):
	      print(message)

Signals are emitted in a coroutine

.. code:: python

	  yield from app.signals.emit(
              'example-signal', "BOOM!")

You can add multiple subscriptions within the section

.. code:: ini

	  [listen/example]
	  example-signal = my.example.listener
	  example-signal-2 = my.example.listener2

You can also subscribe multiple functions to a signal

.. code:: ini

	  [listen/example]
	  example-signal = my.example.listener
	                 my.example.listener2


And you can have multiple "listen/" sections

.. code:: ini

	  [listen/example]
	  example-signal = my.example.listener
	                 my.example.listener2

	  [listen/example2]
	  example-signal2 = my.example.listener2			 


The *aio config* command
------------------------

To dump the system configuration you can run

.. code:: bash

	  aio config

To dump a configuration section you can use -g or --get with the section name

.. code:: bash

	  aio config -g aio

	  aio config --get aio/commands

To get a configuration option, you can use -g with the section name and option

.. code:: bash

	  aio config -g aio:log_level

	  aio config --get listen/example:example-signal

You can set a configuration option with -s or --set

Multi-line options should be enclosed in " and separated with "\\n"

.. code:: bash

	  aio config --set aio:log_level DEBUG

	  aio config -s listen/example:example-signal "my.listener\nmy.listener2"

When saving configuration options, configuration files are searched for in order from the following locations

- aio.conf
- etc/aio.conf
- /etc/aio/aio.conf

If none are present aio will attempt to save it in "aio.conf" in the current working directory

To get or set an option in a particular file you can use the -f flag

.. code:: bash

	  aio config -g aio:modules -f custom.conf

	  aio config -s aio:log_level DEBUG -f custom.conf

When getting config values with the -f flag, ExtendedInterpolation_ is not used, and you therefore see the raw values

	  
The *aio test* command
----------------------

You can test the installed modules using the aio test command

.. code:: ini

	  [aio]
	  modules = aio.app
	           aio.signals

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

- aio.http.server_
- aio.web.server_


.. _aio.core: https://github.com/phlax/aio.core
.. _aio.signals: https://github.com/phlax/aio.signals
.. _aio.config: https://github.com/phlax/aio.config

.. _aio.http.server: https://github.com/phlax/aio.http.server
.. _aio.web.server: https://github.com/phlax/aio.web.server

.. _ExtendedInterpolation: https://docs.python.org/3/library/configparser.html#interpolation-of-values

