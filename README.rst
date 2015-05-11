=======
aio.app
=======


Installation
------------

Install with:

  pip install -i git@github.com/phlax/aio.app

Configuration
-------------

By default the aio command will look for the following configuration files

   aio.conf
   etc/aio.conf
   /etc/aio.conf

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


Running a scheduler
-------------------


Running a server
----------------


Running aio.test
----------------



