# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-11

### Added
- Initial release of `dartfx-dataverse` toolkit.
- `DataverseServer` class for API interactions.
- `ServerInstallation` model for Dataverse installations.
- `SearchParameters` model for advanced search API.
- Support for Worldwide Dataverse installations discovery.
- `requests-cache` integration for improved performance.
- Sphinx documentation with detailed guides and API reference.
- Strict Pydantic V2 integration for all core models.
- Convenience `search_simple` and `get_server_info` methods.

### Changed
- Refactored `DataverseServer` to inherit from `pydantic.BaseModel`.
- Improved type safety across the entire package.
- Updated Mypy configuration for strict type checking.

### Fixed
- Module collision issues in Mypy checks.
- Invalid method references in documentation.
