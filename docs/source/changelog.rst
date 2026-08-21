Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[0.2.0] - 2026-08-20
--------------------

Added
~~~~~

* **First-Class Metadata Harvester & Sync Subsystem** (``dartfx-dataverse harvest``):
  * Added ``harvest`` command for incremental, hash-verified downloading of datasets and multiple metadata formats (``croissant``, ``native``, ``ddi``, ``schema.org``, ``datacite``).
  * Added ``stats`` command with live and 24-hour cached global repository statistics (datasets, total files, tabular files, tabular %, server version).
  * Fast timestamp matching and SHA-256 integrity verification via ``.manifest.json``.
  * Local catalog and statistics 24-hour caching (``.catalog_cache.json`` and ``.stats_cache.json``) with ``--refresh-catalog`` (``-r``) and ``--cache-ttl`` options.
  * Per-server API token resolution via ``.api_token``, ``.dataverse_tokens.json``, and environment variables.
  * Support for multi-format harvesting (``--format all`` or comma-separated lists).
  * Native Croissant endpoint prioritization with automatic graceful fallback.
  * Single-notice reporting and auto-skipping for unsupported format exporters on remote servers.

* **Environment & Configuration Management**:
  * Added ``DARTFX_DATAVERSE_REPOSITORY`` environment variable to define local root storage repository directory.
  * Standardized remote server host resolution via ``DATAVERSE_SERVER_DEFAULT``.
  * Added automatic ``.env`` discovery and loading using ``python-dotenv``.

* **Harvesting Usability Enhancements**:
  * Set default harvesting record limit to 10 datasets per server (pass ``--limit 0`` for unlimited).
  * Enabled tabular dataset filtering by default (pass ``--all-types`` to harvest all datasets).
  * Added ``Version`` column to ``stats`` table with compact semantic version formatting.
  * Robust edge gateway User-Agent header for bypassing WAF/bot challenge interstitials on Dataverse repositories.

* **Documentation & Tests**:
  * Comprehensive user guide for Harvester in Sphinx documentation (``harvester.md``).
  * Added API documentation reference for ``dartfx.dataverse.harvester`` in Sphinx.
  * Extensive unit test suite covering token resolution, manifest persistence, error classification, stats caching, and limit normalization.

[0.1.0] - 2026-03-11
--------------------

Initial release of ``dartfx-dataverse`` toolkit.

Added
~~~~~

* ``DataverseServer`` class for API interactions.
* ``ServerInstallation`` model for Dataverse installations.
* ``SearchParameters`` model for advanced search API.
* Support for worldwide Dataverse installations discovery.
* ``requests-cache`` integration for improved performance.
* Sphinx documentation with detailed guides and API reference.
* Strict Pydantic V2 integration for all core models.
* Convenience ``search_simple`` and ``get_dataset_export`` methods.
* Typer-based Command Line Interface (``dartfx-dataverse``) with Table, JSON, and CSV support.

Changed
~~~~~~~

* Refactored ``DataverseServer`` to inherit from ``DataverseBase``.
* Improved type safety across the entire package.
* Updated Mypy configuration for strict type checking.

Fixed
~~~~~

* Module collision issues in Mypy checks.
* Invalid method references in documentation.

Planned Features
----------------

The following features are planned for future releases:

v0.3.0+
~~~~~~~

* File metadata retrieval
* Dataset and file download capabilities with progress tracking
* Batch download and resume support
* Pydantic models for search results and datasets

v1.0.0
~~~~~~

* Stable API
* Complete test coverage
* Full documentation
* Performance optimizations
* Comprehensive examples

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
