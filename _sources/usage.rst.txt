Usage Guide
===========

This guide covers detailed usage patterns and advanced features of ``dartfx-dataverse``.

Server Management
-----------------

Creating Server Connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``DataverseServer`` class is the main entry point for interacting with Dataverse installations:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, ServerInstallation
   
   # Create a server installation object
   installation = ServerInstallation(
       name="My Dataverse",
       hostname="dataverse.example.com",
       description="Example Dataverse installation"
   )
   
   # Create server connection
   server = DataverseServer(installation=installation)

Configuration Options
~~~~~~~~~~~~~~~~~~~~~

The ``DataverseServer`` class accepts several configuration parameters:

.. code-block:: python

   server = DataverseServer(
       installation=installation,
       api_key="your-api-key",          # Optional API key
       ssl_verify=True,                  # SSL certificate verification
       on_api_error="raise",             # Error handling: "raise" or "none"
       on_api_success_return="json"      # Response format: "json", "text", or "response"
   )

Custom Session Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can provide a custom requests session for advanced configuration:

.. code-block:: python

   import requests_cache
   from datetime import timedelta
   
   # Create custom cached session
   session = requests_cache.CachedSession(
       cache_name='dataverse_cache',
       backend='sqlite',
       expire_after=timedelta(hours=2),
       allowable_methods=['GET', 'POST'],
       stale_if_error=True
   )
   
   server = DataverseServer(
       installation=installation,
       session=session
   )

Server Information
~~~~~~~~~~~~~~~~~~

Retrieve server metadata and version information:

.. code-block:: python

   # Get server information
   info = server.get_server_info()
   print(f"Version: {info['data']['version']}")
   print(f"Build: {info['data']['build']}")
   
   # Get metadata blocks
   metadata_blocks = server.get_metadatablocks()
   for block in metadata_blocks['data']:
       print(f"- {block['name']}: {block.get('displayName', 'N/A')}")

Searching
---------

Simple Search
~~~~~~~~~~~~~

For quick searches, use the ``search_simple`` method:

.. code-block:: python

   # Simple text search
   results = server.search_simple("climate")
   
   # Search with pagination
   results = server.search_simple("climate", start=10, per_page=20)

Advanced Search with Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``SearchParameters`` for full control over search options:

.. code-block:: python

   from dartfx.dataverse import SearchParameters
   
   params = SearchParameters(
       q="title:climate AND description:temperature",
       type="dataset",
       sort="date",
       order="desc",
       per_page=50,
       start=0,
       show_relevance=True,
       show_facets=True,
       show_entity_ids=False
   )
   
   results = server.search(params)

Search Query Syntax
~~~~~~~~~~~~~~~~~~~

The search query supports Solr query syntax:

.. code-block:: python

   # Field-specific search
   params = SearchParameters(q="title:climate")
   
   # Boolean operators
   params = SearchParameters(q="climate AND temperature")
   params = SearchParameters(q="climate OR weather")
   params = SearchParameters(q="climate NOT politics")
   
   # Phrase search
   params = SearchParameters(q='"climate change"')
   
   # Wildcard search
   params = SearchParameters(q="climat*")
   params = SearchParameters(q="*climate*")
   
   # Range search
   params = SearchParameters(
       q="*",
       fq=["publicationDate:[2020 TO 2024]"]
   )

Filtering Results
~~~~~~~~~~~~~~~~~

Use filter queries (``fq``) to narrow results:

.. code-block:: python

   params = SearchParameters(
       q="*",
       type="dataset",
       fq=[
           "publicationDate:[2020 TO *]",        # Published after 2020
           "authorName:Smith",                   # Author is Smith
           "dvName:climateData"                  # In climate dataverse
       ]
   )

Faceted Search
~~~~~~~~~~~~~~

Enable facets to see result distributions:

.. code-block:: python

   params = SearchParameters(
       q="climate",
       show_facets=True
   )
   
   results = server.search(params)
   
   # Process facets
   if 'facets' in results['data']:
       for facet in results['data']['facets']:
           print(f"\nFacet: {facet['friendly_name']}")
           for label in facet['labels']:
               print(f"  {label['label']}: {label['count']}")

Geographic Search
~~~~~~~~~~~~~~~~~

Search by geographic location:

.. code-block:: python

   # Search within radius of a point
   params = SearchParameters(
       q="*",
       geo_point="42.3601,-71.0589",  # Boston, MA (lat,lon)
       geo_radius="50"                 # 50 km radius
   )
   
   results = server.search(params)

Searching Multiple Types
~~~~~~~~~~~~~~~~~~~~~~~~

Search across dataverses, datasets, and files:

.. code-block:: python

   # Search all types
   params = SearchParameters(
       q="climate",
       type=["dataverse", "dataset", "file"]
   )
   
   results = server.search(params)

Pagination
~~~~~~~~~~

Handle large result sets with pagination:

.. code-block:: python

   def paginate_search(server, query, items_per_page=100):
       """Generator function for paginating through search results."""
       start = 0
       
       while True:
           params = SearchParameters(
               q=query,
               per_page=items_per_page,
               start=start
           )
           
           results = server.search(params)
           items = results['data']['items']
           
           if not items:
               break
               
           for item in items:
               yield item
               
           start += items_per_page
   
   # Usage
   for item in paginate_search(server, "climate"):
       print(item['name'])

Error Handling
--------------

Understanding Errors
~~~~~~~~~~~~~~~~~~~~

The package provides the ``DataverseApiError`` exception for API-related errors:

.. code-block:: python

   from dartfx.dataverse import DataverseApiError
   
   try:
       results = server.search_simple("test")
   except DataverseApiError as e:
       print(f"Error: {e.message}")
       print(f"URL: {e.url}")
       print(f"Status Code: {e.status_code}")
       
       # Access the raw response if needed
       if e.response:
           print(f"Response Text: {e.response.text}")

Error Handling Modes
~~~~~~~~~~~~~~~~~~~~

Configure how the server handles API errors:

.. code-block:: python

   # Raise exceptions on errors (default)
   server = DataverseServer(
       installation=installation,
       on_api_error="raise"
   )
   
   # Return None on errors (silent mode)
   server = DataverseServer(
       installation=installation,
       on_api_error="none"
   )
   
   result = server.get_server_info()
   if result is None:
       print("Error occurred, but no exception was raised")

Retry Logic
~~~~~~~~~~~

Implement retry logic for transient failures:

.. code-block:: python

   from time import sleep
   
   def search_with_retry(server, query, max_retries=3):
       """Search with exponential backoff retry."""
       for attempt in range(max_retries):
           try:
               return server.search_simple(query)
           except DataverseApiError as e:
               if e.status_code >= 500 and attempt < max_retries - 1:
                   wait_time = 2 ** attempt
                   print(f"Retry {attempt + 1}/{max_retries} in {wait_time}s...")
                   sleep(wait_time)
               else:
                   raise
   
   results = search_with_retry(server, "climate")

Best Practices
--------------

Use Caching
~~~~~~~~~~~

Enable caching to reduce API calls and improve performance:

.. code-block:: python

   import requests_cache
   
   # Cache responses for 1 hour
   session = requests_cache.CachedSession(
       expire_after=3600,
       allowable_methods=['GET']
   )
   
   server = DataverseServer(installation=installation, session=session)

Rate Limiting
~~~~~~~~~~~~~

Be respectful of server resources:

.. code-block:: python

   from time import sleep
   
   def search_with_rate_limit(server, queries, delay=1.0):
       """Search multiple queries with rate limiting."""
       results = []
       
       for query in queries:
           result = server.search_simple(query)
           results.append(result)
           sleep(delay)  # Wait between requests
       
       return results

Validate Input
~~~~~~~~~~~~~~

Use Pydantic models to validate input data:

.. code-block:: python

   from dartfx.dataverse import SearchParameters
   from pydantic import ValidationError
   
   try:
       # This will raise ValidationError if invalid
       params = SearchParameters(
           q="test",
           per_page=2000  # Exceeds maximum of 1000
       )
   except ValidationError as e:
       print(f"Invalid parameters: {e}")

Handle Missing Data
~~~~~~~~~~~~~~~~~~~

Always check for optional fields in responses:

.. code-block:: python

   results = server.search_simple("test")
   
   for item in results['data']['items']:
       name = item.get('name', 'Unnamed')
       description = item.get('description', 'No description available')
       published_at = item.get('published_at', 'Not published')
       
       print(f"{name}: {description} (Published: {published_at})")

Working with Multiple Installations
------------------------------------

Comparing Results Across Servers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from dartfx.dataverse import fetch_dataverse_installations, DataverseServer
   
   # Get installations
   installations = fetch_dataverse_installations()
   
   # Filter for active installations
   active = [i for i in installations if i.hostname]
   
   # Search across multiple servers
   query = "open data"
   results_by_server = {}
   
   for installation in active[:5]:  # Limit to first 5
       try:
           server = DataverseServer(installation=installation)
           results = server.search_simple(query)
           results_by_server[installation.name] = results['data']['total_count']
       except Exception as e:
           print(f"Error with {installation.name}: {e}")
   
   # Display results
   for name, count in sorted(results_by_server.items(), key=lambda x: x[1], reverse=True):
       print(f"{name}: {count} results")

Advanced Topics
---------------

Custom User Agent
~~~~~~~~~~~~~~~~~

Set a custom user agent for your requests:

.. code-block:: python

   server = DataverseServer(installation=installation)
   server.user_agent = "MyApp/1.0 (contact@example.com)"

Response Format Options
~~~~~~~~~~~~~~~~~~~~~~~

Control the response format:

.. code-block:: python

   # Return JSON (default)
   server = DataverseServer(
       installation=installation,
       on_api_success_return="json"
   )
   
   # Return raw text
   server = DataverseServer(
       installation=installation,
       on_api_success_return="text"
   )
   
   # Return response object
   server = DataverseServer(
       installation=installation,
       on_api_success_return="response"
   )
   
   response = server.get_server_info()
   print(response.status_code)
   print(response.headers)

Debugging
~~~~~~~~~

Enable logging to debug issues:

.. code-block:: python

   import logging
   
   # Enable debug logging
   logging.basicConfig(level=logging.DEBUG)
   logger = logging.getLogger('dartfx.dataverse')
   logger.setLevel(logging.DEBUG)
   
   # Now all API calls will be logged
   results = server.search_simple("test")
