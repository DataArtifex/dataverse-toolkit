API Reference
=============

This section provides detailed documentation for all classes, functions, and modules in the ``dartfx-dataverse`` package.

Overview
--------

The package is organized into the following main components:

* :doc:`server` - Server connection and management classes
* :doc:`search` - Search functionality and parameters
* :doc:`models` - Data models and validation
* :doc:`exceptions` - Error handling and exceptions
* :doc:`harvester` - Harvester metadata synchronization subsystem, statistics, and error analysis

Quick Links
-----------

Main Classes
~~~~~~~~~~~~

* :class:`~dartfx.dataverse.DataverseServer` - Main server connection class
* :class:`~dartfx.dataverse.ServerInstallation` - Server installation information model
* :class:`~dartfx.dataverse.SearchParameters` - Search query parameters model
* :class:`~dartfx.dataverse.ServerHarvester` - Incremental metadata synchronization engine
* :class:`~dartfx.dataverse.DataverseApiError` - API error exception

Main Functions
~~~~~~~~~~~~~~

* :func:`~dartfx.dataverse.fetch_dataverse_installations` - Fetch known Dataverse installations worldwide
* :func:`~dartfx.dataverse.fetch_active_datasets` - Query active dataset records with 24h caching
* :func:`~dartfx.dataverse.fetch_server_stats` - Query live/cached repository metrics and tabular file counts
* :func:`~dartfx.dataverse.classify_harvest_error` - Categorize error reason into standardized taxonomy
* :func:`~dartfx.dataverse.analyze_harvest_errors` - Scan and aggregate error metrics from manifests
* :func:`~dartfx.dataverse.resolve_server_token` - Resolve API token for a server across locations
* :func:`~dartfx.dataverse.save_server_token` - Persist API token for a server
* :func:`~dartfx.dataverse.format_version` - Normalize Dataverse server version strings

Complete API
------------

.. toctree::
   :maxdepth: 2

   server
   search
   models
   exceptions
   harvester
