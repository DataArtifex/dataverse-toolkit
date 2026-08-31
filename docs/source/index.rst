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

.. image:: https://img.shields.io/github/license/DataArtifex/dataverse-toolkit.svg
   :target: https://github.com/DataArtifex/dataverse-toolkit/blob/main/LICENSE.txt
   :alt: License

**A Python toolkit for interacting with Dataverse repositories**

.. warning::
   This project is in its early development stages. Expect the unexpected and breaking changes.
   Feedback and contributions are much appreciated.

Overview
--------

``dartfx-dataverse`` is a type-safe, high-performance Python package and CLI toolkit for programmatic discovery, search, metadata extraction, and incremental bulk synchronization across the worldwide network of `Dataverse <https://dataverse.org/>`_ repositories.

The toolkit focuses on **data discovery, profiling, and metadata harvesting** rather than repository content management, making it an essential utility for researchers, data scientists, machine learning engineers, and catalog administrators.

Comprehensive Multi-Standard Metadata Coverage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``dartfx-dataverse`` provides unified access to diverse dataset representations and standard serialization formats:

* **Croissant ML (JSON-LD)**: Machine Learning-ready metadata specifications adhering to the MLCommons Croissant standard (version 1.0), enabling automated loading into ML pipelines (Hugging Face, TensorFlow, PyTorch).
* **Native Dataverse JSON**: Complete dataset metadata representations including metadata blocks (citation, geospatial, social science, astrophysics, biomedical), file manifests, terms of use, and version histories.
* **DDI Codebook 2.5 (XML)**: Detailed social science study metadata and variable-level codebooks for rectangular tabular datasets.
* **Schema.org (JSON-LD)**: Structured metadata for search engine indexing and Google Dataset Search interoperability.
* **DataCite (XML)**: Persistent identifier and citation metadata conforming to DataCite schemas for academic indexing and DOIs.
* **Dublin Core / OAI-DC**: Standard cross-domain digital library metadata exchange.

Key Capabilities
~~~~~~~~~~~~~~~~

* 🌍 **Global Repository Discovery**: Retrieve and inspect all known Dataverse installations worldwide with ISO 3166-1 country code crosswalk resolution.
* 🔍 **Advanced Search**: Wrapper for the Dataverse Search API supporting Solr queries, boolean expressions, field filtering, faceting, and geographic bounding queries.
* 📦 **Multi-Format Export & Retrieval**: Effortlessly fetch native JSON or exported XML/JSON-LD metadata by DOI or Persistent Identifier (PID).
* ⚡ **High-Performance Metadata Harvester**: Incremental synchronization engine with SHA-256 integrity verification, fast timestamp matching, OAI-PMH deletion detection, and local ``.manifest.json`` tracking.
* 📊 **Repository Statistics & Tabular Profiling**: Live and 24-hour cached metrics reporting dataset totals, file counts, rectangular tabular data file counts, and tabular file percentages across global repositories.
* 🛡️ **Harvest Error Classification Engine**: Automated taxonomy classifying HTTP errors, WAF/Cloudflare interstitials, timeouts, rate limits, and unsupported exporter notices with tabular, JSON, and CSV diagnostics.
* 🔑 **Flexible Authentication & Caching**: Automatic 24-hour catalog caching (``.catalog_cache.json``), per-server API token management (``.api_token``, ``.dataverse_tokens.json``), and HTTP request caching via ``requests-cache``.
* 🛡️ **Strict Type-Safety**: Built with Pydantic V2 models for parameters, server info, and CLI argument validation.

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   # Using uv (recommended - fast and reliable)
   uv add dartfx-dataverse

   # Or using pip
   pip install dartfx-dataverse

Basic Python Usage
~~~~~~~~~~~~~~~~~~

1. Discover Known Dataverse Installations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from dartfx.dataverse import fetch_dataverse_installations

   installations = fetch_dataverse_installations()
   for inst in installations[:5]:
       print(f"{inst.name} ({inst.country}): https://{inst.hostname}")

2. Connect to a Dataverse Server & Inspect Exporters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from dartfx.dataverse import DataverseServer, ServerInstallation

   server = DataverseServer(
       installation=ServerInstallation(
           name="Harvard Dataverse",
           hostname="dataverse.harvard.edu"
       )
   )

   # Inspect server version and supported export formats
   info = server.get_server_info()
   print(f"Version: {info['data']['version']}")

   formats = server.get_info_export_formats()
   for name, details in formats['data'].items():
       print(f"Exporter: {name} -> {details['displayName']}")

3. Search Datasets with Advanced Filters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from dartfx.dataverse import DataverseServer, SearchParameters

   server = DataverseServer(ServerInstallation(hostname="dataverse.harvard.edu"))

   params = SearchParameters(
       q="climate change",
       type="dataset",
       per_page=10,
       sort="date",
       order="desc",
       show_facets=True
   )

   results = server.search(params)
   for item in results['data']['items']:
       print(f"[{item['global_id']}] {item['name']}")

4. Retrieve Multi-Standard Metadata Exports
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   pid = "doi:10.5683/SP3/FNS9EF"

   # 1. Native Dataverse JSON
   native_json = server.get_dataset(pid)

   # 2. Croissant ML (JSON-LD)
   croissant_data = server.get_dataset_export(pid, exporter="croissant")

   # 3. DDI Codebook (XML)
   ddi_xml = server.get_dataset_export(pid, exporter="ddi")

   # 4. Schema.org (JSON-LD)
   schema_json = server.get_dataset_export(pid, exporter="schema.org")

   # 5. DataCite (XML)
   datacite_xml = server.get_dataset_export(pid, exporter="datacite")

Command Line Interface (CLI) Quick Tour
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. List global repositories in a formatted table
   dartfx-dataverse installations --limit 10

   # 2. Inspect live/cached repository metrics and tabular file counts
   dartfx-dataverse stats --country NL

   # 3. Incrementally harvest multi-format metadata (Croissant, Native, DDI, Schema.org, DataCite)
   dartfx-dataverse harvest ./harvested_data --server dataverse.harvard.edu --format all --limit 25

   # 4. Inspect harvest error logs and categorization across manifests
   dartfx-dataverse errors ./harvested_data --by-format

   # 5. Export a single dataset in DDI XML format
   dartfx-dataverse dataset doi:10.5683/SP3/FNS9EF -H borealisdata.ca --export ddi

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   usage
   cli
   harvester
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog

Roadmap
-------

Completed Features (v0.2.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **First-Class Metadata Harvester & Sync Subsystem** (``dartfx-dataverse harvest``): Incremental synchronization and SHA-256 hash verification of Croissant ML, Native Dataverse JSON, DDI Codebook XML, Schema.org JSON-LD, and DataCite XML.
* **Global Server Statistics & Tabular Profiling** (``dartfx-dataverse stats``): Live and 24h-cached metrics for datasets, total files, tabular data files, and tabular file percentages.
* **Harvest Error Classification & Reporting** (``dartfx-dataverse errors``): Categorization of network timeouts, HTTP status errors, WAF/Cloudflare interstitials, authentication blocks, and unsupported exporters.
* **Multi-Format Export Support**: Native JSON, Croissant ML, DDI Codebook XML, Schema.org JSON-LD, and DataCite XML.
* **24h Persistent Catalog/Stats Caching & Per-Server Token Management**: Fast incremental sync with ``.catalog_cache.json``, ``.stats_cache.json``, and ``.dataverse_tokens.json``.

Planned Features (v0.3.0+)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* Direct file downloading and data streaming capabilities with progress bars.
* Batch download and resume support for large dataset payloads.
* Specialized Polars DataFrame loaders for tabular Dataverse files.
* Enhanced Pydantic models for validated search and dataset schemas.

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
