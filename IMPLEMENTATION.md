# Technical Implementation

This document describes the technical architecture and implementation details of `dartfx-dataverse`.

## Architecture Overview

The toolkit is designed to be a high-level, type-safe wrapper around the Dataverse Search and Info APIs. It prioritizes discovery and ease of use.

### Core Components

1.  **`DataverseServer`**: The primary interface for API interactions.
    - Inherits from `pydantic.BaseModel` for configuration management.
    - Manages `requests-cache` sessions for performance.
    - Provides convenience methods for common API calls (Search, Info, Metadata Blocks).
2.  **`ServerInstallation`**: A Pydantic model representing a Dataverse installation with rich metadata (name, hostname, coordinates, launch year, ISO 3166-1 alpha-2 `country_code`, `about_url`, `dv_hub_id`, etc.) and helper properties (`clean_hostname`, `url`).
3.  **`SearchParameters`**: A comprehensive Pydantic model for validating and managing Dataverse Search API parameters.
4.  **`fetch_dataverse_installations` & Registry Engine**: The centralized registry subsystem for discovering worldwide Dataverse instances.
    - Multi-registry endpoint fallback with request timeouts.
    - Built-in ISO 3166-1 Alpha-2 country crosswalk (`COUNTRY_TO_ISO2`, `get_iso2_code`, `matches_country`).
    - Filtering by hostname, ISO country code, or country substring.
    - Automatic fallback synthesis for unlisted/private Dataverse deployments.
5.  **`ServerHarvester` / Metadata Harvester**: A resilient bulk metadata synchronization subsystem.
    - Consumes the unified `fetch_dataverse_installations` registry engine.
    - Multi-format harvesting (`croissant`, `native`, `ddi`, `schema.org`, `datacite`).
    - **Dataset-Level Export Granularity**: Exports are fetched per-dataset from Dataverse endpoints (`/api/datasets/export`). Multi-tabular datasets yield exactly one export document per format with standard-specific inner representations (e.g. multiple `RecordSet` items in Croissant, `<fileDscr>` + `<dataDscr>` variables in DDI).
    - Fast timestamp checking and SHA-256 integrity verification via `.manifest.json`.
    - 24-hour catalog (`.catalog_cache.json`) and server statistics (`.stats_cache.json`) caching.
    - Automated API token discovery and resolution (`.api_token`, `.dataverse_tokens.json`, environment variables).
    - Intelligent error classification (short-circuiting non-recoverable exporter errors).
6.  **Server Statistics, Performance Latency & Diagnostics Subsystem**:
    - **Concurrent Metric Queries**: Queries files and tabular files counts in parallel via `ThreadPoolExecutor(max_workers=2)` for low response latency.
    - **Configurable Timeout Protection**: Query timeouts are configurable (default 10s) and explicitly reported in status messages (e.g. `Timeout (10s)`).
    - **Performance Tier Rating Engine** (`format_response_latency`): Classifies response times into semantic color-coded tiers (`⚡ <3s` Fast, `🟢 3–8s` Normal, `🟡 8–15s` Moderate, `🔴 >15s` Degraded, `🔒` Protected, `❌` Failed).
    - **Deep SSL/TLS Diagnostics** (`classify_harvest_error`): Inspects peer certificates and verification error chains to isolate incomplete intermediate CA chains (missing intermediate CA), certificate expirations, hostname mismatches, and self-signed certificates.
    - **24-Hour Persistence**: Stores metrics in `.stats_cache.json` under each server directory with sub-second CLI re-rendering.

## Design Decisions

### Pydantic for Modeling
We use Pydantic models for all data structures (input parameters and metadata) instead of standard Python dataclasses. This provides:
- Automatic type validation.
- Easy serialization/deserialization (json/dict).
- Improved IDE support and developer experience.

### Request & Catalog Caching
Native support for `requests-cache` is built-in for API sessions. Additionally, the harvesting subsystem utilizes disk-backed, TTL-managed catalog and statistics caches with configurable refresh flags.

### Error Handling
A custom `DataverseApiError` exception provides detailed information about API failures, including status codes, request URLs, and raw response content. The harvester engine categorizes network vs schema/exporter validation failures into non-recoverable error registries.

### Strict Typing & Testing
The project follows strict type hinting and is continuously validated using `ruff` and `pytest`.

## External Dependencies

- `requests`: Base HTTP library.
- `requests-cache`: Transparent caching for HTTP requests.
- `pydantic`: Data validation and settings management.
- `typer` & `rich`: Command-line interface and terminal reports.
- `python-dotenv`: Environment configuration loading.
- `polars`: Preferred for tabular data processing.
