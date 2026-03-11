# Technical Implementation

This document describes the technical architecture and implementation details of `dartfx-dataverse`.

## Architecture Overview

The toolkit is designed to be a high-level, type-safe wrapper around the Dataverse Search and Info APIs. It prioritizes discovery and ease of use.

### Core Components

1.  **`DataverseServer`**: The primary interface for API interactions.
    - Inherits from `pydantic.BaseModel` for configuration management.
    - Manages `requests-cache` sessions for performance.
    - Provides convenience methods for common API calls (Search, Info, Metadata Blocks).
2.  **`ServerInstallation`**: A Pydantic model representing a Dataverse installation with metadata (name, hostname, coordinates, etc.).
3.  **`SearchParameters`**: A comprehensive Pydantic model for validating and managing Dataverse Search API parameters.
4.  **`fetch_dataverse_installations`**: A utility function that retrieves the worldwide list of Dataverse installations from the IQSS repository.

## Design Decisions

### Pydantic for Modeling
We use Pydantic models for all data structures (input parameters and metadata) instead of standard Python dataclasses. This provides:
- Automatic type validation.
- Easy serialization/deserialization (json/dict).
- Improved IDE support and developer experience.

### Request Caching
Native support for `requests-cache` is built-in. By default, it uses a memory backend, but it can be easily configured to use SQLite, Redis, or other backends for persistent caching.

### Error Handling
A custom `DataverseApiError` exception provides detailed information about API failures, including status codes, request URLs, and raw response content.

### Strict Typing
The project follows strict type hinting and is continuously validated using `mypy`. This ensures high code quality and reliability.

## External Dependencies

- `requests`: Base HTTP library.
- `requests-cache`: Transparent caching for HTTP requests.
- `pydantic`: Data validation and settings management.
- `polars`: Preferred for data management (though currently used primarily in search result processing workflows).
