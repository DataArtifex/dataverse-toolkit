Harvester Module
================

The harvester module provides classes and functions for incremental multi-standard metadata synchronization, global repository statistics inspection, error classification, and token management.

ServerHarvester
---------------

.. autoclass:: dartfx.dataverse.ServerHarvester
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Functions
---------

Dataset Catalog & Fetching
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: dartfx.dataverse.fetch_active_datasets

.. autofunction:: dartfx.dataverse.harvester.fetch_metadata_record

.. autofunction:: dartfx.dataverse.harvester.fetch_oai_deletions

Repository Statistics & Profiling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: dartfx.dataverse.fetch_server_stats

.. autofunction:: dartfx.dataverse.format_version

Error Classification & Diagnostics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: dartfx.dataverse.classify_harvest_error

.. autofunction:: dartfx.dataverse.analyze_harvest_errors

.. autofunction:: dartfx.dataverse.harvester.render_harvest_errors

Token & Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: dartfx.dataverse.resolve_server_token

.. autofunction:: dartfx.dataverse.save_server_token

Utility Functions
~~~~~~~~~~~~~~~~~

.. autofunction:: dartfx.dataverse.harvester.sanitize_pid

.. autofunction:: dartfx.dataverse.harvester.get_format_extension

.. autofunction:: dartfx.dataverse.harvester.normalize_formats
