Command Line Interface (CLI)
==============================

``dartfx-dataverse`` provides a powerful, type-safe command-line interface for discovering Dataverse installations, inspecting server configurations, searching records, downloading metadata exports, and managing bulk metadata harvesting.

The CLI is built with **Typer** and **Rich**, featuring interactive terminal tables, colored progress reporting, JSON/CSV streaming outputs, and automatic ``.env`` configuration loading.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview & Syntax
-----------------

To run the CLI:

.. code-block:: bash

   # Using uv (recommended)
   uv run dartfx-dataverse [COMMAND] [OPTIONS] [ARGUMENTS]

   # Or when installed in your active environment
   dartfx-dataverse [COMMAND] [OPTIONS] [ARGUMENTS]

Get global help or command-specific options:

.. code-block:: bash

   dartfx-dataverse --help
   dartfx-dataverse search --help
   dartfx-dataverse info --help

Available Commands
------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Command
     - Description
   * - ``installations``
     - Discover and list worldwide Dataverse repositories from the global registry.
   * - ``info``
     - Inspect server version, build metadata, and all supported metadata export formats.
   * - ``search``
     - Search across datasets, dataverses, and files with filtering, sorting, and pagination.
   * - ``dataset``
     - Retrieve native JSON metadata or standard export formats (Croissant, Native JSON, DDI, Schema.org, DataCite).
   * - ``metadatablocks``
     - List registered metadata schema blocks (citation, geospatial, social science, etc.).
   * - ``stats``
     - Inspect live/cached counts of datasets, files, and tabular rectangular data files.
   * - ``harvest``
     - Incrementally synchronize and hash-verify multi-standard metadata across global repositories.
   * - ``errors``
     - Analyze and report counts per harvest error type across repository manifests.

---

Environment Variables & Configuration
-------------------------------------

You can customize default connection settings using environment variables or a local ``.env`` file:

.. list-table::
   :widths: 35 65
   :header-rows: 1

   * - Variable
     - Purpose
   * - ``DATAVERSE_SERVER``
     - Default Dataverse server hostname (default: ``dataverse.harvard.edu``).
   * - ``DATAVERSE_API_KEY``
     - Default API token for authenticated queries.
   * - ``DARTFX_DATAVERSE_API_KEY``
     - Alternative package-specific API token variable.
   * - ``DARTFX_DATAVERSE_REPOSITORY``
     - Default local storage root directory for the metadata harvester and catalog cache.

Example ``.env`` file:

.. code-block:: bash

   DATAVERSE_SERVER=dataverse.nl
   DATAVERSE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   DARTFX_DATAVERSE_REPOSITORY=./harvested_records

---

1. ``installations`` - List Global Repositories
-----------------------------------------------

Fetches and displays the worldwide directory of Dataverse installations maintained by the Harvard IQSS registry.

Syntax
~~~~~~

.. code-block:: bash

   dartfx-dataverse installations [OPTIONS]

Options
~~~~~~~

* ``--limit``, ``-l`` *(integer)*: Maximum number of installations to display.
* ``--format``, ``-f`` *(string)*: Output format: ``table`` (default), ``json``, or ``csv``.

Examples
~~~~~~~~

**Display first 10 global installations in a formatted terminal table:**

.. code-block:: bash

   dartfx-dataverse installations --limit 10

**Export all worldwide installations to a CSV file:**

.. code-block:: bash

   dartfx-dataverse installations --format csv > dataverse_installations.csv

**Extract hostnames with jq:**

.. code-block:: bash

   dartfx-dataverse installations --format json | jq -r '.[].hostname'

---

2. ``info`` - Server & Export Formats Inspection
------------------------------------------------

Queries a Dataverse server for its name, API version, build identifier, and the complete catalog of supported metadata export formats.

Syntax
~~~~~~

.. code-block:: bash

   dartfx-dataverse info [HOSTNAME] [OPTIONS]

Arguments & Options
~~~~~~~~~~~~~~~~~~~

* ``HOSTNAME`` *(positional, optional)*: Dataverse server hostname (e.g. ``dataverse.nl``, ``borealisdata.ca``). Defaults to ``DATAVERSE_SERVER`` or ``dataverse.harvard.edu``.
* ``--api-key``, ``-k`` *(string)*: API key for servers requiring authentication.

Output
~~~~~~

The command outputs:

1. **Server message / Name**
2. **Dataverse Version & Build Number**
3. **Export Formats Table**:
   - **ID**: Exporter format identifier (e.g. ``ddi``, ``schema.org``, ``croissant``, ``native``, ``oai_dc``, ``datacite``).
   - **Display Name**: Human-readable format name (e.g. *DDI Codebook 2.5*, *Croissant ML*).
   - **Media Type**: MIME type (e.g. ``application/xml``, ``application/ld+json``).
   - **Harvest**: Whether this exporter is available for OAI-PMH / bulk harvesting.
   - **Visible**: Whether this export format is enabled in the web user interface.

Examples
~~~~~~~~

**Inspect Harvard Dataverse:**

.. code-block:: bash

   dartfx-dataverse info dataverse.harvard.edu

**Inspect Borealis (Canada) using an API key:**

.. code-block:: bash

   dartfx-dataverse info borealisdata.ca --api-key "YOUR_KEY"

---

3. ``search`` - Search Datasets, Dataverses & Files
---------------------------------------------------

Performs full-text, faceted, and filtered queries against the Dataverse Search API.

Syntax
~~~~~~

.. code-block:: bash

   dartfx-dataverse search <QUERY> [OPTIONS]

Arguments & Options
~~~~~~~~~~~~~~~~~~~

* ``QUERY`` *(positional, required)*: Search query string (supports Solr query syntax).
* ``--hostname``, ``-H`` *(string)*: Target server hostname (default: ``dataverse.harvard.edu``).
* ``--type``, ``-t`` *(string)*: Filter result object type: ``dataset``, ``dataverse``, or ``file``.
* ``--per-page`` / ``--limit``, ``-p`` / ``-l`` *(integer)*: Number of results per page (default: 25).
* ``--sort``, ``-s`` *(string)*: Sort field: ``name`` or ``date``.
* ``--order``, ``-o`` *(string)*: Sort order: ``asc`` or ``desc``.
* ``--format``, ``-f`` *(string)*: Output format: ``table`` (default), ``json``, or ``csv``.
* ``--api-key``, ``-k`` *(string)*: API key for restricted repositories.

Search Query Syntax Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Keyword Search**: ``"quantum mechanics"``
* **Wildcards**: ``climat*``
* **Boolean Operators**: ``climate AND (temperature OR precipitation) NOT politics``
* **Field Filters**: ``authorName:Smith``, ``subject:Medicine``, ``dvName:OpenData``
* **Date Range Queries**: ``publicationDate:[2022-01-01 TO 2026-12-31]``

Examples
~~~~~~~~

**Search for climate datasets sorted by date descending:**

.. code-block:: bash

   dartfx-dataverse search "climate change" --type dataset --sort date --order desc --limit 10

**Search files on a specific regional server:**

.. code-block:: bash

   dartfx-dataverse search "archaeology" --hostname dataverse.nl --type file

**Stream search results to JSON:**

.. code-block:: bash

   dartfx-dataverse search "genomics" --format json > results.json

**Export search results directly to CSV:**

.. code-block:: bash

   dartfx-dataverse search "machine learning" --format csv > ml_datasets.csv

---

4. ``dataset`` - Metadata & Export Formats
------------------------------------------

Fetches the complete native JSON metadata or standard export representation (XML, JSON-LD) for a specific dataset.

Syntax
~~~~~~

.. code-block:: bash

   dartfx-dataverse dataset <IDENTIFIER> [OPTIONS]

Arguments & Options
~~~~~~~~~~~~~~~~~~~

* ``IDENTIFIER`` *(positional, required)*: Persistent Identifier (DOI or Handle, e.g. ``doi:10.7910/DVN/WGCRY7``, ``doi:10.5683/SP3/FNS9EF``).
* ``--hostname``, ``-H`` *(string)*: Server hostname (default: ``dataverse.harvard.edu``).
* ``--export``, ``-e`` *(string)*: Specific export format name (e.g. ``ddi``, ``croissant``, ``schema.org``, ``native``, ``datacite``, ``oai_dc``). If omitted, returns full native JSON dataset version metadata.
* ``--api-key``, ``-k`` *(string)*: API key.

Examples
~~~~~~~~

**Retrieve complete native JSON metadata for a dataset:**

.. code-block:: bash

   dartfx-dataverse dataset doi:10.7910/DVN/WGCRY7

**Download DDI Codebook 2.5 XML export:**

.. code-block:: bash

   dartfx-dataverse dataset doi:10.7910/DVN/WGCRY7 --export ddi > dataset_ddi.xml

**Retrieve Schema.org JSON-LD:**

.. code-block:: bash

   dartfx-dataverse dataset doi:10.5683/SP3/FNS9EF -H borealisdata.ca --export schema.org

---

5. ``metadatablocks`` - Metadata Schema Blocks
----------------------------------------------

Lists the metadata schema blocks configured and available on a Dataverse server (such as Citation, Geospatial, Social Science, Astronomy, Life Sciences).

Syntax
~~~~~~

.. code-block:: bash

   dartfx-dataverse metadatablocks [HOSTNAME] [OPTIONS]

Arguments & Options
~~~~~~~~~~~~~~~~~~~

* ``HOSTNAME`` *(positional, optional)*: Server hostname (defaults to ``DATAVERSE_SERVER`` or ``dataverse.harvard.edu``).
* ``--format``, ``-f`` *(string)*: Output format: ``table`` (default) or ``csv``.
* ``--api-key``, ``-k`` *(string)*: API key.

Examples
~~~~~~~~

**View registered metadata blocks:**

.. code-block:: bash

   dartfx-dataverse metadatablocks dataverse.harvard.edu

---

6. ``stats`` - Global Repository Statistics
-------------------------------------------

Queries and presents live and 24-hour cached counts of total datasets, files, tabular rectangular data files (with variables), and tabular percentage across servers, along with real-time response latency indicators and fine-grained server status diagnostics.

Syntax
~~~~~~

.. code-block:: bash

   dartfx-dataverse stats [OPTIONS]

Options
~~~~~~~

* ``--server``, ``-s`` *(string)*: Target server hostname or ``ALL`` (default: ``ALL``).
* ``--country``, ``-c`` *(string)*: Filter servers by 2-letter ISO 3166-1 code (e.g. ``NL``, ``US``, ``FR``, ``DE``, ``CA``, ``GB``).
* ``--query``, ``-q`` *(string)*: Filter statistics by search keyword (e.g. ``climate``).
* ``--api-token`` / ``--key``, ``-k`` *(string)*: API token for protected servers.
* ``--refresh`` / ``--refresh-catalog``, ``-r`` *(flag)*: Force a live statistics refresh from servers, bypassing local 24-hour cache.
* ``--cache-ttl`` *(integer)*: Statistics cache expiration time in hours (default: ``24``).
* ``--timeout``, ``-t`` *(integer)*: HTTP request timeout in seconds per server query (default: ``10``).

Output Table Columns
~~~~~~~~~~~~~~~~~~~~

The ``stats`` command renders an interactive Rich table with the following columns:

* **Hostname**: Target repository domain (rendered as a live clickable hyperlink in supporting terminals).
* **Country**: 2-letter ISO 3166-1 Alpha-2 country code (e.g. ``US``, ``NL``, ``CA``).
* **Version**: Clean semantic version string (e.g. ``v6.3``, ``v5.14``) normalized from upstream build info.
* **Datasets**: Total count of published datasets indexed on the server.
* **Files**: Total count of data files across all datasets.
* **Tabular**: Count of rectangular tabular data files (CSV, SPSS, Stata, SAS, RData) indexed with variable metadata.
* **Tabular %**: Percentage of total files that are tabular data files.
* **Response**: Real-time HTTP query latency and performance rating badge (see tiers below).
* **Status / Note**: Server health indicator, cache status (``[cached]``), or specific diagnostics reason.

Response Latency & Performance Indicators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **Response** column measures total round-trip query time and assigns a semantic icon and color badge:

.. list-table::
   :widths: 20 25 55
   :header-rows: 1

   * - Indicator
     - Latency Range
     - Performance Classification
   * - ``⚡ <3.0s``
     - Under 3.0 seconds
     - **Fast / High Performance**: High-throughput indexing and responsive Solr engine.
   * - ``🟢 3.0s–8.0s``
     - 3.0 to 8.0 seconds
     - **Normal**: Standard enterprise response time for large multi-million file repositories.
   * - ``🟡 8.0s–15.0s``
     - 8.0 to 15.0 seconds
     - **Moderate / Slow**: Slower response time or high concurrent search load.
   * - ``🔴 >15.0s``
     - Over 15.0 seconds
     - **Degraded**: Severe latency or infrastructure bottleneck.
   * - ``🔒``
     - N/A
     - **Protected**: Repository requires an API token (``-k`` or ``DATAVERSE_API_TOKEN``).
   * - ``❌``
     - N/A
     - **Failed / Offline**: Connection error, SSL failure, WAF block, or timeout.

Server Status & Diagnostics
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **Status / Note** column displays fine-grained diagnostics for unreachable or restricted repositories:

* **Fine-Grained SSL Certificate Diagnostics**:
  * ``SSL: Missing Intermediate CA / Incomplete Chain``: Server configuration omits the intermediate CA certificate (often works in web browsers due to automatic AIA fetching, but fails in strict OpenSSL/Python clients).
  * ``SSL: Certificate Expired``: Server TLS certificate validity period has expired.
  * ``SSL: Hostname Mismatch``: Certificate Common Name / SAN does not match repository domain.
  * ``SSL: Self-Signed Certificate``: Untrusted self-signed certificate.
* **Network & Gateway Diagnostics**:
  * ``Timeout (10s)``: Query exceeded the configured timeout limit (adjust with ``--timeout`` / ``-t``).
  * ``Cloudflare WAF / Bot Protection``: Cloudflare challenge page intercepted automated query.
  * ``WAF / Bot Protection Interstitial``: Institutional security gateway (AWS/custom) blocked headless request.
  * ``Protected (API Token Required)``: Server configured with ``:SearchApiRequiresToken = true``.
  * ``Host Unreachable / DNS Failure``: DNS resolution error or server host offline.
  * ``HTTP 404 (Inactive / Not Found)``: Obsolete registry path or decommissioned instance.

Examples
~~~~~~~~

**Inspect stats for all Dutch repositories:**

.. code-block:: bash

   dartfx-dataverse stats --country NL

**Force refresh statistics bypassing cache:**

.. code-block:: bash

   dartfx-dataverse stats --server dataverse.harvard.edu --refresh

**Adjust query timeout for slow servers:**

.. code-block:: bash

   dartfx-dataverse stats --country US --timeout 15

**Check statistics for Harvard Dataverse matching a keyword:**

.. code-block:: bash

   dartfx-dataverse stats --server dataverse.harvard.edu --query "climate"

---

7. ``harvest`` - Metadata Harvester & Sync Engine
-------------------------------------------------

Performs intelligent, incremental metadata harvesting with SHA-256 verification and multi-format support into structured local storage directories.

Syntax
~~~~~~

.. code-block:: bash

   dartfx-dataverse harvest <OUTPUT_DIR> --format <FORMAT> [OPTIONS]

Key Features
~~~~~~~~~~~~

* **Incremental Synchronization**: Checks timestamps and SHA-256 hashes to download only new and modified datasets.
* **Multi-Format Support**: Harvests ``croissant``, ``croissant_slim``, ``native``, ``ddi``, ``oai_ddi``, ``schema.org``, ``datacite``, ``oai_ore``, ``dcterms``, or ``all`` formats simultaneously.
* **Resilient Error Handling**: Short-circuits non-recoverable schema errors and logs failures to ``.manifest.json``.
* **Repository Caching**: 24-hour catalog caching (``.catalog_cache.json``) for rapid incremental runs.

For the full architectural workflow, directory layout specifications, and advanced sync options, refer to the dedicated :doc:`harvester` guide.

---

8. ``errors`` - Harvest Error Analysis & Counts by Type
-------------------------------------------------------

Scans repository storage directories for ``.manifest.json`` files and aggregates all recorded harvest failures into a categorized summary report.

Syntax
~~~~~~

.. code-block:: bash

   dartfx-dataverse errors [REPO_DIR] [OPTIONS]

Arguments & Options
~~~~~~~~~~~~~~~~~~~

* ``REPO_DIR`` *(positional, optional)*: Local storage repository root directory (or specific server subdirectory). Defaults to ``DARTFX_DATAVERSE_REPOSITORY`` env var or current directory.
* ``--server``, ``-s`` *(string)*: Filter error report by server hostname or ``ALL`` (default: ``ALL``).
* ``--by-format`` *(flag)*: Breakdown error counts into a matrix by metadata format (Croissant, Croissant Slim, Native, DDI, OAI-DDI, Schema.org, DataCite, OAI-ORE, DCTerms).
* ``--by-server`` *(flag)*: Breakdown error counts by server repository hostname.
* ``--details``, ``-d`` *(flag)*: Display individual failed dataset records, PIDs, formats, categories, and error reasons.
* ``--format``, ``-f`` *(string)*: Output format: ``table`` (default), ``json``, or ``csv``.

Error Categories Detected
~~~~~~~~~~~~~~~~~~~~~~~~~

* **Croissant Validation: Missing Checksum (md5/sha256)**: Upstream files omitting required cryptographic hashes.
* **Croissant Validation: Missing Mandatory Field**: Datasets missing mandatory MLCommons Croissant properties.
* **Exporter Not Supported on Server**: Requested metadata exporter unavailable on remote server.
* **HTTP 401: Authentication Required (API Token)**: Repositories configured with token restrictions.
* **HTTP 403: Forbidden / Bot Protection (WAF)**: Cloudflare challenge or security gateway intercept.
* **HTTP 404: Dataset / Exporter Not Found**: Inactive, deleted, or deaccessioned dataset.
* **HTTP 422: Unprocessable Entity**: Remote exporter failure.
* **HTTP 5xx: Server / Upstream Error**: Remote Dataverse server internal error.
* **Network: Request Timeout / Connection Failure**: Network transport errors.
* **Parse Error: Malformed XML / JSON**: Payload syntax errors.

Examples
~~~~~~~~

**View summary count per error type across the local repository:**

.. code-block:: bash

   dartfx-dataverse errors ./my_data

**View error counts broken down by metadata format:**

.. code-block:: bash

   dartfx-dataverse errors ./my_data --by-format

**View error counts broken down by server repository:**

.. code-block:: bash

   dartfx-dataverse errors ./my_data --by-server

**List detailed failed records with dataset PIDs and reasons:**

.. code-block:: bash

   dartfx-dataverse errors ./my_data --details

**Export error statistics to JSON or CSV:**

.. code-block:: bash

   dartfx-dataverse errors ./my_data --format json > harvest_errors.json
   dartfx-dataverse errors ./my_data --format csv > harvest_errors.csv
