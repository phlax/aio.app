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
