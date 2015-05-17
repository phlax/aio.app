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
	  run: aio.app.cmd.cmd_run
	  test: aio.app.testing.cmd.cmd_test

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

	  
Dependencies
------------

aio.app depends on the following packages

  - aio.core_
  - aio.signals_
  - aio.config_
  - aio.logging_


Related software
----------------

  - aio.http_
  - aio.web_


.. _aio.core: https://github.com/phlax/aio.core
.. _aio.signals: https://github.com/phlax/aio.signals
.. _aio.config: https://github.com/phlax/aio.config
.. _aio.logging: https://github.com/phlax/aio.logging

.. _aio.http: https://github.com/phlax/aio.http
.. _aio.web: https://github.com/phlax/aio.web    

