Server Classes
==============

This module contains classes for managing connections to Dataverse servers.

DataverseServer
---------------

The main class for interacting with a Dataverse server installation.

.. autoclass:: dartfx.dataverse.DataverseServer
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

ServerInstallation
------------------

Represents a Dataverse installation with its metadata.

.. autoclass:: dartfx.dataverse.ServerInstallation
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

.. autofunction:: dartfx.dataverse.fetch_dataverse_installations

Examples
--------

Creating a Server Connection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from dartfx.dataverse import DataverseServer, ServerInstallation

   # Create installation object
   installation = ServerInstallation(
       name="Harvard Dataverse",
       hostname="dataverse.harvard.edu"
   )

   # Create server connection
   server = DataverseServer(installation)

With API Key
~~~~~~~~~~~~

.. code-block:: python

   server = DataverseServer(
       server=installation,
       api_key="your-api-key-here"
   )

Custom Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import requests_cache
   from datetime import timedelta

   # Create custom session
   session = requests_cache.CachedSession(
       cache_name='my_cache',
       expire_after=timedelta(hours=1)
   )

   # Create server with custom config
   server = DataverseServer(
       server=installation,
       session=session,
       ssl_verify=True,
       on_api_error="raise"
   )

Getting Server Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get server info
   info = server.get_server_info()
   print(f"Version: {info['data']['version']}")

   # Get metadata blocks
   blocks = server.get_metadatablocks()
   for block in blocks['data']:
       print(block['name'])
