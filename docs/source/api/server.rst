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

   .. rubric:: Methods

   .. autosummary::
      :nosignatures:

      ~DataverseServer.__init__
      ~DataverseServer.get_server_info
      ~DataverseServer.get_metadatablocks
      ~DataverseServer.search
      ~DataverseServer.search_simple

   .. rubric:: Attributes

   .. attribute:: installation
      :type: ServerInstallation
      
      The server installation information.

   .. attribute:: api_key
      :type: str | None
      
      Optional API key for authenticated requests.

   .. attribute:: session
      :type: requests_cache.CachedSession
      
      The requests session used for API calls.

   .. attribute:: user_agent
      :type: str
      
      User agent string sent with requests.

   .. attribute:: ssl_verify
      :type: bool
      
      Whether to verify SSL certificates.

   .. attribute:: on_api_error
      :type: str
      
      How to handle API errors: ``"raise"`` or ``"none"``.

   .. attribute:: on_api_success_return
      :type: str
      
      Response format: ``"json"``, ``"text"``, or ``"response"``.

ServerInstallation
------------------

Represents a Dataverse installation with its metadata.

.. autoclass:: dartfx.dataverse.ServerInstallation
   :members:
   :undoc-members:
   :show-inheritance:

   .. rubric:: Attributes

   .. attribute:: name
      :type: str | None
      
      Name of the Dataverse installation.

   .. attribute:: description
      :type: str | None
      
      Description of the installation.

   .. attribute:: hostname
      :type: str | None
      
      Hostname of the server (e.g., ``"dataverse.harvard.edu"``).

   .. attribute:: lat
      :type: float | None
      
      Latitude coordinate of the installation.

   .. attribute:: lng
      :type: float | None
      
      Longitude coordinate of the installation.

   .. attribute:: metrics
      :type: bool | None
      
      Whether metrics are available for this installation.

   .. attribute:: launch_year
      :type: str | None
      
      Year the installation was launched.

   .. attribute:: country
      :type: str | None
      
      Country where the installation is located.

   .. attribute:: continent
      :type: str | None
      
      Continent where the installation is located.

   .. attribute:: harvesting_sets
      :type: list[str] | None
      
      List of harvesting set identifiers.

   .. attribute:: core_trust_seals
      :type: list[str] | None
      
      Core Trust Seal certifications.

   .. attribute:: gdcc_member
      :type: bool | None
      
      Whether this is a Global Dataverse Community Consortium member.

   .. attribute:: doi_authority
      :type: str | None
      
      DOI authority for this installation.

   .. attribute:: board
      :type: str | None
      
      Governing board information.

   .. attribute:: contact_email
      :type: str | None
      
      Contact email for the installation.

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
   server = DataverseServer(installation=installation)

With API Key
~~~~~~~~~~~~

.. code-block:: python

   server = DataverseServer(
       installation=installation,
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
       installation=installation,
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
