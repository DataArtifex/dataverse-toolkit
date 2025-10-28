Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
------------

Added
~~~~~

* Comprehensive Sphinx documentation
* Detailed API reference
* Usage examples and quickstart guide
* Contributing guidelines

Changed
~~~~~~~

* Updated minimum Python version to 3.12
* Enhanced project metadata and classifiers
* Improved pyproject.toml configuration with Ruff and mypy settings

[0.1.0] - 2024-XX-XX
--------------------

Initial development release.

Added
~~~~~

* ``DataverseServer`` class for server connections
* ``ServerInstallation`` model for server metadata
* ``SearchParameters`` model for search queries
* ``DataverseApiError`` exception for error handling
* ``fetch_dataverse_installations()`` function to retrieve known installations
* Basic search functionality:
  
  * Simple text search
  * Advanced search with parameters
  * Faceted search
  * Geographic search
  * Filter queries

* Server information retrieval:
  
  * Get server version and metadata
  * Get metadata blocks

* Request caching with ``requests-cache``
* Pydantic models for data validation
* Configurable error handling modes
* SSL verification control
* Custom user agent support

Dependencies
~~~~~~~~~~~~

* pydantic >= 2.0.0
* requests >= 2.31.0
* requests-cache >= 1.0.0

Development
~~~~~~~~~~~

* pytest for testing
* mypy for type checking
* ruff for linting and formatting
* Hatch for project management
* Sphinx for documentation

[0.0.1] - 2024-XX-XX
--------------------

Pre-release version for initial development.

.. note::
   This project is in early development. Features and APIs may change.

Planned Features
----------------

The following features are planned for future releases:

v0.2.0
~~~~~~

* Pydantic models for search results
* Enhanced error messages and debugging
* Batch operation support
* Progress indicators for long-running operations

v0.3.0
~~~~~~

* Dataset metadata retrieval (DDI, Dublin Core)
* File metadata retrieval
* Support for additional metadata formats:
  
  * Croissant
  * schema.org
  * DataCite

v0.4.0
~~~~~~

* Dataset download capabilities
* File download with progress tracking
* Batch download support
* Resume interrupted downloads

v1.0.0
~~~~~~

* Stable API
* Complete test coverage
* Full documentation
* Performance optimizations
* Comprehensive examples

Migration Notes
---------------

Upgrading to 0.1.0
~~~~~~~~~~~~~~~~~~

This is the first release, no migration needed.

Future Breaking Changes
~~~~~~~~~~~~~~~~~~~~~~~

The following breaking changes are planned:

* v0.2.0: Search result format may change when Pydantic models are added
* v0.3.0: Some method signatures may change to support new features
* v1.0.0: API will be stabilized, no breaking changes after this point

Version Support
---------------

Python Version Support
~~~~~~~~~~~~~~~~~~~~~~

* **Python 3.12+**: Fully supported
* **Python 3.11**: Not supported (use v0.0.x if needed)
* **Python 3.10**: Not supported (use v0.0.x if needed)

Dataverse Version Support
~~~~~~~~~~~~~~~~~~~~~~~~~

This package is tested against:

* Dataverse 5.x
* Dataverse 6.x

Older versions may work but are not officially supported.

Contributing
------------

See the :doc:`contributing` guide for information on how to contribute 
to this project.

Links
-----

* `GitHub Repository <https://github.com/DataArtifex/dataverse-toolkit>`_
* `Issue Tracker <https://github.com/DataArtifex/dataverse-toolkit/issues>`_
* `PyPI Package <https://pypi.org/project/dartfx-dataverse/>`_
* `Documentation <https://dataverse-toolkit.readthedocs.io/>`_
