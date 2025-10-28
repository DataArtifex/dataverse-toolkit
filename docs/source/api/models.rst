Data Models
===========

This page documents the Pydantic models used throughout the package.

Overview
--------

All data models in ``dartfx-dataverse`` are built using Pydantic for robust 
type validation and serialization. These models ensure data integrity and 
provide excellent IDE support with autocomplete and type hints.

ServerInstallation
------------------

See :class:`~dartfx.dataverse.ServerInstallation` in the :doc:`server` documentation.

SearchParameters
----------------

See :class:`~dartfx.dataverse.SearchParameters` in the :doc:`search` documentation.

Working with Models
-------------------

Creating Model Instances
~~~~~~~~~~~~~~~~~~~~~~~~~

Models can be created by passing keyword arguments:

.. code-block:: python

   from dartfx.dataverse import ServerInstallation
   
   installation = ServerInstallation(
       name="Harvard Dataverse",
       hostname="dataverse.harvard.edu",
       country="USA",
       launch_year="2014"
   )

From Dictionary
~~~~~~~~~~~~~~~

Create models from dictionaries:

.. code-block:: python

   data = {
       "name": "Demo Dataverse",
       "hostname": "demo.dataverse.org",
       "country": "USA"
   }
   
   installation = ServerInstallation(**data)

Model Validation
~~~~~~~~~~~~~~~~

Pydantic automatically validates data:

.. code-block:: python

   from pydantic import ValidationError
   from dartfx.dataverse import SearchParameters
   
   try:
       # This will fail: per_page exceeds maximum
       params = SearchParameters(
           q="test",
           per_page=2000  # Maximum is 1000
       )
   except ValidationError as e:
       print(e)

Exporting Models
~~~~~~~~~~~~~~~~

Convert models to dictionaries or JSON:

.. code-block:: python

   # To dictionary
   data = installation.model_dump()
   
   # To dictionary (exclude None values)
   data = installation.model_dump(exclude_none=True)
   
   # To JSON string
   json_str = installation.model_dump_json()
   
   # To JSON with indentation
   json_str = installation.model_dump_json(indent=2)

Model Fields
~~~~~~~~~~~~

Access model fields as attributes:

.. code-block:: python

   print(installation.name)
   print(installation.hostname)
   print(installation.country)
   
   # Check if field is set
   if installation.description:
       print(installation.description)

Updating Models
~~~~~~~~~~~~~~~

Models are immutable by default. To update, create a copy:

.. code-block:: python

   # Create a copy with updated fields
   updated = installation.model_copy(
       update={"description": "Updated description"}
   )

Model Schema
~~~~~~~~~~~~

Get the JSON schema for a model:

.. code-block:: python

   schema = SearchParameters.model_json_schema()
   print(schema)

Type Hints
----------

All models provide full type hints for better IDE support:

.. code-block:: python

   from dartfx.dataverse import ServerInstallation, SearchParameters
   
   def process_installation(inst: ServerInstallation) -> None:
       # IDE will provide autocomplete for 'inst'
       print(inst.name)
       print(inst.hostname)
   
   def create_search(query: str) -> SearchParameters:
       # IDE knows the return type
       return SearchParameters(
           q=query,
           type="dataset",
           per_page=20
       )

Optional vs Required Fields
---------------------------

Understanding which fields are optional:

ServerInstallation
~~~~~~~~~~~~~~~~~~

All fields in ``ServerInstallation`` are optional except when explicitly required 
by your use case. The ``hostname`` field is essential for connecting to a server:

.. code-block:: python

   # Minimum required for server connection
   installation = ServerInstallation(hostname="dataverse.example.com")
   
   # With additional metadata
   installation = ServerInstallation(
       name="My Dataverse",
       hostname="dataverse.example.com",
       country="USA",
       launch_year="2023"
   )

SearchParameters
~~~~~~~~~~~~~~~~

Only the ``q`` field has a default value (``"*"``). All other fields are optional:

.. code-block:: python

   # Minimal search (uses defaults)
   params = SearchParameters()  # q="*"
   
   # Typical search
   params = SearchParameters(
       q="climate",
       type="dataset",
       per_page=20
   )
   
   # Comprehensive search
   params = SearchParameters(
       q="climate change",
       type="dataset",
       sort="date",
       order="desc",
       per_page=50,
       fq=["publicationDate:[2020 TO *]"],
       show_facets=True
   )

Field Constraints
-----------------

Some fields have validation constraints:

Numeric Constraints
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # per_page must be between 1 and 1000
   SearchParameters(per_page=1)     # Valid
   SearchParameters(per_page=1000)  # Valid
   SearchParameters(per_page=2000)  # ValidationError
   SearchParameters(per_page=0)     # ValidationError

String Literals
~~~~~~~~~~~~~~~

Some fields only accept specific values:

.. code-block:: python

   # type field
   SearchParameters(type="dataset")   # Valid
   SearchParameters(type="file")      # Valid
   SearchParameters(type="invalid")   # ValidationError
   
   # sort field
   SearchParameters(sort="name")      # Valid
   SearchParameters(sort="date")      # Valid
   SearchParameters(sort="invalid")   # ValidationError
   
   # order field
   SearchParameters(order="asc")      # Valid
   SearchParameters(order="desc")     # Valid
   SearchParameters(order="invalid")  # ValidationError

Best Practices
--------------

Use Type Hints
~~~~~~~~~~~~~~

Always use type hints for better code quality:

.. code-block:: python

   from dartfx.dataverse import ServerInstallation, SearchParameters
   
   def search_installations(
       installations: list[ServerInstallation],
       query: str
   ) -> list[dict]:
       results = []
       for inst in installations:
           # Type hints enable autocomplete
           server = DataverseServer(installation=inst)
           result = server.search_simple(query)
           results.append(result)
       return results

Validate Early
~~~~~~~~~~~~~~

Let Pydantic catch errors early:

.. code-block:: python

   from pydantic import ValidationError
   
   def create_search_from_user_input(user_data: dict) -> SearchParameters | None:
       try:
           return SearchParameters(**user_data)
       except ValidationError as e:
           print(f"Invalid search parameters: {e}")
           return None

Use model_dump() for Serialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When saving to files or databases:

.. code-block:: python

   import json
   
   # Save installation data
   with open('installation.json', 'w') as f:
       json.dump(installation.model_dump(), f, indent=2)
   
   # Load installation data
   with open('installation.json', 'r') as f:
       data = json.load(f)
       installation = ServerInstallation(**data)

Exclude None Values
~~~~~~~~~~~~~~~~~~~

When None values are not needed:

.. code-block:: python

   # Only include fields with values
   data = installation.model_dump(exclude_none=True)
   
   # Useful for cleaner API requests
   params_dict = params.model_dump(exclude_none=True)
