# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-10-05

### Added

- **First-Class Metadata Harvester & Sync Subsystem** (`dartfx-dataverse harvest`):
  - Fixed deletion logic to protect previously harvested datasets when running with `--limit`, `--query`, `--since`, or `--doi` filters (only prune deletions during full, unconstrained server syncs).
  - Enhanced Sync Summary Report table and completion panel to explicitly report **Datasets** processed alongside **Files Added / Updated / Unchanged / Deleted**.
  - Added `harvest` command for incremental, hash-verified downloading of datasets and multiple metadata formats (`croissant`, `native`, `ddi`, `schema.org`, `datacite`).
  - Added `stats` command with live and 24-hour cached global repository statistics (datasets, total files, tabular files, tabular %, server version).
  - Added `errors` command to inspect, categorize, and report counts per harvest error type across repository manifests (`--by-format`, `--by-server`, `--details`, JSON/CSV export).
  - Added granular error classification engine (`classify_harvest_error`, `analyze_harvest_errors`, `render_harvest_errors`).
  - Fast timestamp matching and SHA-256 integrity verification via `.manifest.json`.
  - Local catalog and statistics 24-hour caching (`.catalog_cache.json` and `.stats_cache.json`) with `--refresh-catalog` (`-r`) and `--cache-ttl` options.
  - Per-server API token resolution via `.api_token` and `.dataverse_tokens.json`.
  - Support for multi-format harvesting (`--format all` or comma-separated lists).
  - Native Croissant endpoint prioritization with automatic graceful fallback.
  - Single-notice reporting and auto-skipping for unsupported format exporters on remote servers.
- **Reconciliation & Unification of Server Installations & Harvester Registry**:
  - Reconciled `ServerInstallation` model and Harvester registry into a unified, type-safe architecture.
  - Enhanced `ServerInstallation` model with ISO 3166-1 Alpha-2 `country_code` auto-derivation, `about_url`, `dv_hub_id`, and `clean_hostname`/`url` helper properties.
  - Centralized and expanded ISO country crosswalk (`COUNTRY_TO_ISO2`, `get_iso2_code`, `matches_country`) to cover all worldwide installations and standard ISO 3166-1 Alpha-2 codes (e.g. Slovenia `SI`, Botswana `BW`, Croatia `HR`, Hong Kong `HK`, Taiwan `TW`, Ukraine `UA`, Iceland `IS`, Ecuador `EC`, Luxembourg `LU`, Uruguay `UY`).
  - Upgraded `fetch_dataverse_installations` with timeout resilience, country filtering, hostname targeting, and fallback synthesis for unlisted/private servers.
  - Refactored `harvester.py`'s `get_global_installations` and `fetch_raw_installations` to delegate directly to the unified `fetch_dataverse_installations` engine.
  - Enhanced `dartfx-dataverse installations` and `dartfx-dataverse search` CLI commands with active clickable hyperlink URLs in terminal tables (`Name/Title` and `Identifier`), and included the `url` column in CSV exports.
- **Environment & Configuration Management**:
  - Added environment variable to define the local root storage repository directory for harvested datasets and cache.
  - Standardized remote server host resolution via .
  - Added automatic discovery and loading using .
- **Harvesting Usability Enhancements**:
  - Set default harvesting record limit to datasets per server (pass for unlimited).
  - Enabled tabular dataset filtering by default (pass to harvest all datasets).
  - Added column to table with compact semantic version formatting.
  - Normalized long repository version strings with commit hashes and build metadata (e.g. `v1.3.1-bfb997c0ad...`) to clean semantic version format (`vN.N.N`) in `stats` table.
  - Added live progress bar updates during the initial dataset catalog pagination phase (`Cataloging host: X datasets (Y/Z items indexed)`), providing real-time feedback during large catalog scans.
  - Ensured deterministic maximum timestamp aggregation across multi-file datasets and broadened non-recoverable error caching (HTTP 401/403/422/501, syntax/parse errors) to eliminate latency on consecutive sync runs.
  - Refined format unsupported detection to ensure individual dataset permissions (`HTTP 403 Forbidden` / restricted datasets) do not falsely trigger server-wide format skipping.
  - Deferred local server directory creation and added empty directory cleanup to prevent creating orphan folders when harvesting non-existent or unreachable servers.
  - Multi-threaded concurrent repository statistics fetching via `ThreadPoolExecutor` and comprehensive 24-hour error/offline status caching in `.stats_cache.json` for sub-second subsequent `stats` runs.
  - Added configurable `--timeout` / `-t` option to `dartfx-dataverse stats` and parallelized sub-queries (files and tabular counts) to accelerate queries on slow servers.
  - Added dedicated `Response` column to `dartfx-dataverse stats` table featuring color-coded performance tier badges (`⚡ <3s Fast`, `🟢 3–8s Normal`, `🟡 8–15s Moderate`, `🔴 >15s Degraded`).
  - Fine-grained SSL error classification distinguishing incomplete certificate chains (`SSL: Missing Intermediate CA / Incomplete Chain`), expired certificates, hostname mismatches, and self-signed certificates.
  - Streamlined CLI by removing redundant `--stats` and `--list-servers` options from `dartfx-dataverse harvest` in favor of dedicated top-level `dartfx-dataverse stats` and `dartfx-dataverse installations` commands.
  - Robust edge gateway User-Agent header for bypassing WAF/bot challenge interstitials on Dataverse repositories.
- **Documentation & Tests**:
  - Comprehensive user guide for Harvester in Sphinx documentation (`docs/source/harvester.md`).
  - Added documentation explaining multi-tabular dataset export behavior, dataset-level packaging granularity, and cross-standard representation (Croissant, DDI, Schema.org, Native JSON, DataCite).
  - Added API documentation reference for `harvester` in Sphinx.
  - Extensive unit test suite covering token resolution, manifest persistence, error classification, stats caching, and limit normalization (30 tests passing).

## [0.1.0] - 2026-03-11

### Added

- Initial release of toolkit.
- class for API interactions.
- model for Dataverse installations.
- model for advanced search API.
- Support for Worldwide Dataverse installations discovery.
- integration for improved performance.
- Sphinx documentation with detailed guides and API reference.
- Strict Pydantic V2 integration for all core models.
- Convenience and methods.
- Typer-based Command Line Interface () with Table, JSON, and CSV support.

### Changed

- Refactored to inherit from .
- Improved type safety across the entire package.
- Updated Mypy configuration for strict type checking.

### Fixed

- Module collision issues in Mypy checks.
- Invalid method references in documentation.
