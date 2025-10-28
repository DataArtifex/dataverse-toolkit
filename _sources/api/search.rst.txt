Search Functionality
====================

This module provides search capabilities for querying Dataverse installations.

SearchParameters
----------------

Model for specifying search query parameters.

.. autoclass:: dartfx.dataverse.SearchParameters
   :members:
   :undoc-members:
   :show-inheritance:

   .. rubric:: Parameters

   .. attribute:: q
      :type: str
      
      The search term or terms. Default is ``"*"`` (match all).
      
      * Use ``"title:data"`` to search only the ``title`` field
      * Use ``"*"`` as a wildcard (e.g., ``"bird*"``)
      * Supports Boolean operators: ``AND``, ``OR``, ``NOT``
      * Use quotes for phrase search: ``"climate change"``

   .. attribute:: type
      :type: Literal["dataverse", "dataset", "file"] | list | None
      
      Filter by type. Can be:
      
      * ``"dataverse"`` - Search dataverse collections
      * ``"dataset"`` - Search datasets only
      * ``"file"`` - Search files only
      * List of multiple types: ``["dataset", "file"]``

   .. attribute:: subtree
      :type: str | None
      
      Identifier of a Dataverse collection to narrow the search.
      The subtree and all its children will be searched.

   .. attribute:: sort
      :type: Literal["name", "date"] | None
      
      Sort field for results:
      
      * ``"name"`` - Sort by name
      * ``"date"`` - Sort by date

   .. attribute:: order
      :type: Literal["asc", "desc"] | None
      
      Sort order:
      
      * ``"asc"`` - Ascending order
      * ``"desc"`` - Descending order

   .. attribute:: per_page
      :type: int | None
      
      Number of results per request. 
      
      * Default: 10
      * Minimum: 1
      * Maximum: 1000

   .. attribute:: start
      :type: int | None
      
      Cursor for pagination. Starting position for results.

   .. attribute:: show_relevance
      :type: bool | None
      
      Whether to show which fields were matched by the query.
      Default is ``False``.

   .. attribute:: show_facets
      :type: bool | None
      
      Whether to show facets for filtering results.
      Default is ``False``.

   .. attribute:: fq
      :type: list[str] | None
      
      Filter queries to narrow results. Examples:
      
      * ``["publicationDate:[2020 TO *]"]`` - From 2020 onwards
      * ``["authorName:Smith"]`` - Author is Smith
      * Multiple filters can be combined

   .. attribute:: show_entity_ids
      :type: bool | None
      
      Whether to show database IDs in results (for developers).

   .. attribute:: geo_point
      :type: str | None
      
      Geographic point in format ``"latitude,longitude"`` (e.g., ``"42.3,-71.1"``).
      Must be used with ``geo_radius``.

   .. attribute:: geo_radius
      :type: str | None
      
      Radial distance in kilometers from ``geo_point`` (e.g., ``"1.5"``).
      Must be used with ``geo_point``.

   .. attribute:: metadata_fields
      :type: list[str] | None
      
      Specific metadata fields to include in response.
      Multiple fields can be requested.

Search Methods
--------------

These methods are available on the :class:`~dartfx.dataverse.DataverseServer` class.

search()
~~~~~~~~

Perform a search with detailed parameters.

.. code-block:: python

   def search(self, parameters: SearchParameters) -> dict:
       """
       Execute a search query with specified parameters.
       
       Args:
           parameters: SearchParameters object with query details
           
       Returns:
           dict: Search results with metadata and items
           
       Raises:
           DataverseApiError: If the API request fails
       """

search_simple()
~~~~~~~~~~~~~~~

Perform a simple text search without creating a SearchParameters object.

.. code-block:: python

   def search_simple(
       self, 
       query: str, 
       start: int = 0, 
       per_page: int = 10
   ) -> dict:
       """
       Execute a simple search query.
       
       Args:
           query: Search term(s)
           start: Starting position for results
           per_page: Number of results per page
           
       Returns:
           dict: Search results
           
       Raises:
           DataverseApiError: If the API request fails
       """

Examples
--------

Basic Search
~~~~~~~~~~~~

.. code-block:: python

   from dartfx.dataverse import SearchParameters
   
   params = SearchParameters(
       q="climate change",
       type="dataset",
       per_page=20
   )
   
   results = server.search(params)

Advanced Search with Filters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   params = SearchParameters(
       q="title:education AND description:data",
       type="dataset",
       fq=[
           "publicationDate:[2020 TO 2024]",
           "authorName:Smith"
       ],
       sort="date",
       order="desc",
       per_page=50,
       show_facets=True
   )
   
   results = server.search(params)

Geographic Search
~~~~~~~~~~~~~~~~~

.. code-block:: python

   params = SearchParameters(
       q="*",
       geo_point="42.3601,-71.0589",  # Boston, MA
       geo_radius="50",                # 50 km
       type="dataset"
   )
   
   results = server.search(params)

Search with Metadata Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   params = SearchParameters(
       q="health",
       type="dataset",
       metadata_fields=[
           "citation",
           "identifier",
           "subjects",
           "authorName"
       ],
       per_page=10
   )
   
   results = server.search(params)

Faceted Search
~~~~~~~~~~~~~~

.. code-block:: python

   params = SearchParameters(
       q="*",
       type="dataset",
       show_facets=True
   )
   
   results = server.search(params)
   
   # Access facets
   if 'facets' in results['data']:
       for facet in results['data']['facets']:
           print(f"Facet: {facet['friendly_name']}")
           for label in facet['labels']:
               print(f"  {label['label']}: {label['count']}")

Pagination
~~~~~~~~~~

.. code-block:: python

   # Page 1
   params = SearchParameters(
       q="data",
       per_page=25,
       start=0
   )
   page1 = server.search(params)
   
   # Page 2
   params.start = 25
   page2 = server.search(params)
   
   # Page 3
   params.start = 50
   page3 = server.search(params)

Simple Search
~~~~~~~~~~~~~

.. code-block:: python

   # Quick search without SearchParameters
   results = server.search_simple("climate", per_page=20)
   
   print(f"Found {results['data']['total_count']} results")
   for item in results['data']['items']:
       print(f"- {item['name']}")

Search Query Syntax
-------------------

The search query supports Solr syntax:

Field-Specific Search
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   params = SearchParameters(q="title:climate")
   params = SearchParameters(q="authorName:Smith")
   params = SearchParameters(q="description:temperature")

Boolean Operators
~~~~~~~~~~~~~~~~~

.. code-block:: python

   params = SearchParameters(q="climate AND temperature")
   params = SearchParameters(q="climate OR weather")
   params = SearchParameters(q="climate NOT politics")

Phrase Search
~~~~~~~~~~~~~

.. code-block:: python

   params = SearchParameters(q='"climate change"')
   params = SearchParameters(q='"data analysis"')

Wildcards
~~~~~~~~~

.. code-block:: python

   params = SearchParameters(q="climat*")     # Prefix
   params = SearchParameters(q="*climate*")   # Contains
   params = SearchParameters(q="climat?")     # Single character

Range Queries
~~~~~~~~~~~~~

.. code-block:: python

   # Date range in filter
   params = SearchParameters(
       q="*",
       fq=["publicationDate:[2020 TO 2024]"]
   )
   
   # Numeric range
   params = SearchParameters(
       q="*",
       fq=["fileCount:[10 TO 100]"]
   )

Response Format
---------------

Search results are returned as a dictionary with the following structure:

.. code-block:: python

   {
       "status": "OK",
       "data": {
           "total_count": 150,
           "start": 0,
           "items": [
               {
                   "name": "Dataset Name",
                   "type": "dataset",
                   "url": "https://...",
                   "identifier": "doi:...",
                   "published_at": "2024-01-15",
                   "description": "...",
                   # Additional fields...
               },
               # More items...
           ],
           "facets": [
               {
                   "name": "subject_ss",
                   "friendly_name": "Subject",
                   "labels": [
                       {"label": "Medicine", "count": 45},
                       {"label": "Social Sciences", "count": 32},
                       # More labels...
                   ]
               },
               # More facets...
           ]
       }
   }
