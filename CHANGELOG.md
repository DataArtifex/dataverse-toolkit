# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-08-20

### Added
- **First-Class Metadata Harvester & Sync Subsystem** ():
  - Added  command for incremental, hash-verified downloading of datasets and multiple metadata formats (, , , , ).
  - Added  command with live and 24-hour cached global repository statistics (datasets, total files, tabular files, tabular %, server version).
  - Fast timestamp matching and SHA-256 integrity verification via .
  - Local catalog and statistics 24-hour caching ( and ) with  () and  options.
  - Per-server API token resolution via  and .
  - Support for multi-format harvesting ( or comma-separated lists).
  - Native Croissant endpoint prioritization with automatic graceful fallback.
  - Single-notice reporting and auto-skipping for unsupported format exporters on remote servers.
- **Environment & Configuration Management**:
  - Added  environment variable to define the local root storage repository directory for harvested datasets and cache.
  - Standardized remote server host resolution via .
  - Added automatic  discovery and loading using .
- **Harvesting Usability Enhancements**:
  - Set default harvesting record limit to  datasets per server (pass  for unlimited).
  - Enabled tabular dataset filtering by default (pass  to harvest all datasets).
  - Added  column to  table with compact semantic version formatting.
  - Robust edge gateway User-Agent header for bypassing WAF/bot challenge interstitials on Dataverse repositories.
- **Documentation & Tests**:
  - Comprehensive user guide for Harvester in Sphinx documentation ().
  - Added API documentation reference for  in Sphinx.
  - Extensive unit test suite covering token resolution, manifest persistence, error classification, stats caching, and limit normalization (30 tests passing).

## [0.1.0] - 2026-03-11

### Added
- Initial release of  toolkit.
-  class for API interactions.
-  model for Dataverse installations.
-  model for advanced search API.
- Support for Worldwide Dataverse installations discovery.
-  integration for improved performance.
- Sphinx documentation with detailed guides and API reference.
- Strict Pydantic V2 integration for all core models.
- Convenience  and  methods.
- Typer-based Command Line Interface () with Table, JSON, and CSV support.

### Changed
- Refactored  to inherit from .
- Improved type safety across the entire package.
- Updated Mypy configuration for strict type checking.

### Fixed
- Module collision issues in Mypy checks.
- Invalid method references in documentation.
