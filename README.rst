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

Requires python >= 3.4

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
	  
	  def schedule_handler(event):
	      yield from asyncio.sleep(1)
	      print ("Received scheduled: %s" % event.name)

Run with the aio run command

.. code:: bash

	  aio run -c hello.conf
	  


The *aio config* command
------------------------

When saving or reading configuration options, configuration files are searched for in order from the following locations

- aio.conf
- etc/aio.conf
- /etc/aio/aio.conf

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

Options containing interpolation should be enclosed in single quotes

Multi-line options should be enclosed in " and separated with "\\n"

.. code:: bash

	  aio config --set aio:log_level DEBUG

	  aio config -s aio/otherapp:log_level '${aio:log_level}'
	  
	  aio config -s listen/example:example-signal "my.listener\nmy.listener2"

If no configuration files are present in the standard locations, aio will attempt to save in "aio.conf" in the current working directory

To get or set an option in a particular file you can use the -f flag

.. code:: bash

	  aio config -g aio:modules -f custom.conf

	  aio config -s aio:log_level DEBUG -f custom.conf

When getting config values with the -f flag, ExtendedInterpolation_ is not used, and you therefore see the raw values



the *aio run* command
---------------------

You can run an aio app as follows:

.. code:: bash

	  aio run

Or with a custom configuration file
	  
.. code:: bash

	  aio -c custom.conf run


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
	  foo = eggs
	       spam

While the app is running the system configuration is importable from aio.app

.. code:: python

	  from aio.app import config

Configuration is parsed using ExtendedInterpolation_ as follows

- aio.app defaults read
- user configuration read to initialize modules
- "aio.conf" read from initialized modules where present
- user configuration read again


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

Any sections that begin with handler, logger, or formatter will automattically be added to the relevant logging section

So by adding a section such as

.. code:: ini

	  [logger_custom]
	  level=${aio:log_level}
	  handlers=consoleHandler
	  qualname=custom

"logger_custom" will automatically be added to the logger keys:

.. code:: ini

	  [loggers]
	  keys=root,custom


Modules
~~~~~~~

You can list any modules that should be imported at runtime in the configuration

.. code:: ini

	  [aio]
	  modules = aio.web.server
	          aio.manhole.server

Configuration for each module is read from a file named "aio.conf" in the module's path, if it exists.

The initialized modules can be accessed from aio.app

.. code:: python

	  from aio.app import modules


Schedulers
~~~~~~~~~~

Schedule definition sections follow the following format

.. code:: ini

	  [schedule/SCHEDULE_NAME]


Specify the frequency and the function to call. The function will be wrapped in a coroutine if it isnt one already

.. code:: ini

	  [schedule/example]
	  every = 2
	  func = my.scheduler.example_scheduler

The scheduler function receives a ScheduledEvent object

.. code:: python

	  def example_scheduler(event):
              yield from asyncio.sleep(2)
	      # do something
	      print(event.name)
	      pass

Servers
~~~~~~~

Server definition sections follow the following format

.. code:: ini

	  [server/SERVER_NAME]

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

The factory method must be wrapped in aio.app.server.factory

.. code:: python

	  @aio.app.server.factory
	  def server_factory(name, protocol, address, port):
	      loop = asyncio.get_event_loop()
	      return (
	          yield from loop.create_server(
		     ServerProtocol, address, port))


Signals
~~~~~~~

Signal definition sections follow the following format

.. code:: ini

	  [signal/SIGNAL_NAME]

An example listen configuration section

.. code:: ini

	  [listen/example]
	  example-signal = my.example.listener

And an example listener function. The listener function will be called as a coroutine

.. code:: python

	  def listener(signal, message):
	      yield from asyncio.sleep(2)
	      print(message)

Signals are emitted in a coroutine

.. code:: python

	  yield from app.signals.emit(
              'example-signal', "BOOM!")

You can add multiple subscriptions within each configuration section

You can also subscribe multiple functions to a signal, and you can have multiple "listen/" sections

.. code:: ini

	  [listen/example]
	  example-signal = my.example.listener
	  example-signal-2 = my.example.listener2
	                  my.example.listener

	  [listen/example-2]
	  example-signal-3 = my.example.listener2			 

   
The *aio test* command
----------------------

You can test the modules set in the aio:modules configuration option

.. code:: ini

	  [aio]
	  modules = aio.config
                   aio.core
	           aio.signals

By default the aio test command will test all of your test modules
		   
.. code:: bash

	  aio test

You can also specify a module, or modules

.. code:: bash

	  aio test aio.app

	  aio test aio.app aio.core

If you want to specify a set of modules for testing other than your app modules, you can list them in aio/testing:modules

.. code:: ini

	  [aio/testing]
	  modules = aio.config
                   aio.core

These can include the app modules

.. code:: ini

	  [aio/testing]
	  modules = ${aio:modules}
	           aio.web.page
		   aio.web.server
		   

Dependencies
------------

aio.app depends on the following packages

- aio.core_
- aio.signals_
- aio.config_


Related software
----------------

- aio.testing_
- aio.http.server_
- aio.web.server_
- aio.manhole.server_

.. _aio.testing: https://github.com/phlax/aio.testing
.. _aio.core: https://github.com/phlax/aio.core
.. _aio.signals: https://github.com/phlax/aio.signals
.. _aio.config: https://github.com/phlax/aio.config

.. _aio.http.server: https://github.com/phlax/aio.http.server
.. _aio.web.server: https://github.com/phlax/aio.web.server
.. _aio.manhole.server: https://github.com/phlax/aio.manhole.server

.. _ExtendedInterpolation: https://docs.python.org/3/library/configparser.html#interpolation-of-values

