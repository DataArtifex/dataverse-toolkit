dartfx-dataverse Documentation
================================

.. image:: https://img.shields.io/pypi/v/dartfx-dataverse.svg
   :target: https://pypi.org/project/dartfx-dataverse
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/dartfx-dataverse.svg
   :target: https://pypi.org/project/dartfx-dataverse
   :alt: Python Versions

.. image:: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg
   :target: https://github.com/DataArtifex/dataverse-toolkit/blob/main/CODE_OF_CONDUCT.md
   :alt: Contributor Covenant

**A Python toolkit for interacting with Dataverse repositories**

.. warning::
   This project is in its early development stages. Stability is not guaranteed, 
   and documentation is limited. We welcome your feedback and contributions.

Overview
--------

``dartfx-dataverse`` is a Python package that facilitates interactions with Dataverse 
server installations via their API. The package focuses on discovery and access rather 
than content management, making it ideal for researchers and data scientists who need 
to programmatically search and retrieve data from Dataverse repositories.

Key Features
~~~~~~~~~~~~

* **Server Discovery**: Retrieve information about known Dataverse installations worldwide
* **Search Functionality**: Powerful search capabilities with advanced filtering options
* **Type-Safe**: Built with Pydantic models for robust data validation
* **Caching**: Built-in request caching for improved performance
* **Error Handling**: Comprehensive error handling with detailed exception information

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   # Using uv (recommended - fast and reliable)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv pip install dartfx-dataverse
   
   # Or using pip
   pip install dartfx-dataverse

Basic Usage
~~~~~~~~~~~

Fetch Dataverse Installations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get a list of all known Dataverse installations:

.. code-block:: python

   from dartfx.dataverse import fetch_dataverse_installations
   
   installations = fetch_dataverse_installations()
   for installation in installations:
       print(f"{installation.name}: {installation.hostname}")

Connect to a Dataverse Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a connection to a specific Dataverse server:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, ServerInstallation
   
   # Create a server installation object
   server_info = ServerInstallation(
       name="Harvard Dataverse",
       hostname="dataverse.harvard.edu"
   )
   
   # Connect to the server
   server = DataverseServer(installation=server_info)
   
   # Get server information
   info = server.get_server_info()
   print(info)

Search for Datasets
^^^^^^^^^^^^^^^^^^^

Perform searches across datasets:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, SearchParameters
   
   # Search with parameters
   params = SearchParameters(
       q="climate change",
       type="dataset",
       per_page=20,
       sort="date",
       order="desc"
   )
   
   results = server.search(params)
   for item in results['data']['items']:
       print(f"{item['name']} - {item.get('description', 'No description')}")

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   
   installation
   quickstart
   usage
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference
   
   api/index
   api/server
   api/search
   api/models
   api/exceptions

.. toctree::
   :maxdepth: 1
   :caption: Development
   
   contributing
   changelog

Roadmap
-------

Planned features for future releases:

* Pydantic models for search results
* Dataset and file metadata retrieval (DDI, Croissant, schema.org)
* Dataset and file download capabilities
* Advanced metadata operations
* Batch operations support

Contributing
------------

We welcome contributions! Please see our :doc:`contributing` guide for details.

1. Fork the repository
2. Create your feature branch: ``git checkout -b my-new-feature``
3. Commit your changes: ``git commit -am 'Add some feature'``
4. Push to the branch: ``git push origin my-new-feature``
5. Submit a pull request

License
-------

This project is licensed under the MIT License. See the LICENSE file for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
