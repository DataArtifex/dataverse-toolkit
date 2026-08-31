Search Functionality
====================

This module provides search capabilities and query parameter modeling for querying Dataverse installations.

SearchParameters
----------------

Model for specifying search query parameters.

.. autoclass:: dartfx.dataverse.SearchParameters
   :members:
   :undoc-members:
   :show-inheritance:

Query Examples
--------------

Basic Queries
~~~~~~~~~~~~~

.. code-block:: python

   from dartfx.dataverse import SearchParameters

   # Match all datasets
   params = SearchParameters()

   # Text search
   params = SearchParameters(q="climate change")

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

Range Queries & Filters
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Date range in filter
   params = SearchParameters(
       q="*",
       fq=["publicationDate:[2020 TO 2026]"]
   )

   # Geographic proximity search
   params = SearchParameters(
       q="*",
       geo_point="42.3601,-71.0589",
       geo_radius="50"
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
               },
           ],
           "facets": [
               {
                   "name": "subject_ss",
                   "friendly_name": "Subject",
                   "labels": [
                       {"label": "Medicine", "count": 45},
                       {"label": "Social Sciences", "count": 32},
                   ]
               },
           ]
       }
   }
