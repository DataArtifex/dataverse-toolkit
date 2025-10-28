Quickstart Guide
================

This guide will help you get started with ``dartfx-dataverse`` in just a few minutes.

Installation
------------

First, install the package using uv (recommended):

.. code-block:: bash

   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dartfx-dataverse
   uv pip install dartfx-dataverse

Or using pip:

.. code-block:: bash

   pip install dartfx-dataverse

Basic Workflow
--------------

The typical workflow for using this package involves:

1. Discovering available Dataverse installations (optional)
2. Creating a server connection
3. Performing searches or retrieving information
4. Processing the results

Step 1: Discover Dataverse Installations
-----------------------------------------

Get a list of all known Dataverse installations worldwide:

.. code-block:: python

   from dartfx.dataverse import fetch_dataverse_installations
   
   # Fetch all known installations
   installations = fetch_dataverse_installations()
   
   # Display the first 5 installations
   for installation in installations[:5]:
       print(f"{installation.name}")
       print(f"  Hostname: {installation.hostname}")
       print(f"  Country: {installation.country}")
       print(f"  Launch Year: {installation.launch_year}")
       print()

Step 2: Connect to a Server
----------------------------

Create a connection to a specific Dataverse server:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, ServerInstallation
   
   # Create server installation object
   harvard = ServerInstallation(
       name="Harvard Dataverse",
       hostname="dataverse.harvard.edu"
   )
   
   # Create server connection
   server = DataverseServer(installation=harvard)
   
   # Get server information
   info = server.get_server_info()
   print(f"Server version: {info['data']['version']}")

With API Key (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~

If you have an API key for authenticated requests:

.. code-block:: python

   server = DataverseServer(
       installation=harvard,
       api_key="your-api-key-here"
   )

Step 3: Search for Data
-----------------------

Perform a simple search:

.. code-block:: python

   # Simple text search
   results = server.search_simple("climate")
   
   print(f"Found {results['data']['total_count']} results")
   
   # Display first 5 results
   for item in results['data']['items'][:5]:
       print(f"- {item['name']}")

Advanced Search
~~~~~~~~~~~~~~~

Use the ``SearchParameters`` model for more control:

.. code-block:: python

   from dartfx.dataverse import SearchParameters
   
   # Create search parameters
   params = SearchParameters(
       q="climate change",          # Search query
       type="dataset",              # Only search datasets
       per_page=10,                 # Results per page
       sort="date",                 # Sort by date
       order="desc",                # Descending order
       show_facets=True            # Include facets in results
   )
   
   # Execute search
   results = server.search(params)
   
   # Process results
   for item in results['data']['items']:
       print(f"Dataset: {item['name']}")
       print(f"  Published: {item.get('published_at', 'N/A')}")
       print(f"  URL: {item.get('url', 'N/A')}")
       print()

Step 4: Filter and Refine
--------------------------

Use filters to refine your search:

.. code-block:: python

   # Search with filters
   params = SearchParameters(
       q="*",                           # Match all
       type="dataset",
       fq=[                             # Filter queries
           "publicationDate:[2020 TO *]",  # From 2020 onwards
           "dvName:climate"                # In climate dataverse
       ],
       per_page=20
   )
   
   results = server.search(params)

Working with Multiple Servers
------------------------------

You can work with multiple Dataverse installations simultaneously:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, fetch_dataverse_installations
   
   # Get installations
   installations = fetch_dataverse_installations()
   
   # Filter for specific installations
   harvard = next(i for i in installations if "harvard" in i.name.lower())
   demo = next(i for i in installations if "demo" in i.name.lower())
   
   # Create connections
   harvard_server = DataverseServer(installation=harvard)
   demo_server = DataverseServer(installation=demo)
   
   # Search both servers
   harvard_results = harvard_server.search_simple("education")
   demo_results = demo_server.search_simple("education")
   
   print(f"Harvard: {harvard_results['data']['total_count']} results")
   print(f"Demo: {demo_results['data']['total_count']} results")

Handling Errors
---------------

The package provides structured error handling:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, DataverseApiError, ServerInstallation
   
   try:
       server = DataverseServer(
           installation=ServerInstallation(
               name="Test Server",
               hostname="invalid.example.com"
           )
       )
       results = server.get_server_info()
   except DataverseApiError as e:
       print(f"API Error: {e.message}")
       print(f"Status Code: {e.status_code}")
       print(f"URL: {e.url}")
   except Exception as e:
       print(f"Unexpected error: {e}")

Configuring Caching
-------------------

The package uses request caching by default. You can configure it:

.. code-block:: python

   import requests_cache
   from datetime import timedelta
   
   # Create a custom cache session
   session = requests_cache.CachedSession(
       cache_name='my_dataverse_cache',
       backend='sqlite',
       expire_after=timedelta(hours=1)
   )
   
   # Use with server
   server = DataverseServer(
       installation=harvard,
       session=session
   )

Disable caching if needed:

.. code-block:: python

   import requests
   
   # Use regular requests session (no caching)
   server = DataverseServer(
       installation=harvard,
       session=requests.Session()
   )

Next Steps
----------

Now that you understand the basics, explore:

* :doc:`usage` - Detailed usage examples and patterns
* :doc:`examples` - Real-world use cases
* :doc:`api/index` - Complete API reference

Common Use Cases
----------------

Finding Datasets by Subject
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   params = SearchParameters(
       q="subject:medicine",
       type="dataset",
       per_page=50
   )
   results = server.search(params)

Searching Within a Collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   params = SearchParameters(
       q="*",
       subtree="myDataverse",  # Collection identifier
       type="dataset"
   )
   results = server.search(params)

Geographic Search
~~~~~~~~~~~~~~~~~

.. code-block:: python

   params = SearchParameters(
       q="*",
       geo_point="42.3,-71.1",  # Latitude, Longitude
       geo_radius="10"           # Radius in kilometers
   )
   results = server.search(params)

Getting Help
------------

If you encounter issues or have questions:

* Check the :doc:`usage` documentation for detailed examples
* Review the :doc:`api/index` for complete API reference
* Report issues on `GitHub <https://github.com/DataArtifex/dataverse-toolkit/issues>`_
* Consult the `Dataverse API Guide <https://guides.dataverse.org/en/latest/api/>`_
