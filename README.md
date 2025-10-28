# dartfx-dataverse

[![PyPI - Version](https://img.shields.io/pypi/v/dartfx-dataverse.svg)](https://pypi.org/project/dartfx-dataverse)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dartfx-dataverse.svg)](https://pypi.org/project/dartfx-dataverse)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.txt)

**A Python toolkit for interacting with Dataverse repositories**

> ⚠️ **Early Development**: This project is in its early development stages. While functional, the API may change and some features are still being implemented. We welcome your feedback and contributions!

## Overview

`dartfx-dataverse` is a Python package that facilitates programmatic interactions with [Dataverse](https://dataverse.org/) server installations via their API. The package focuses on discovery and access rather than content management, making it ideal for researchers, data scientists, and developers who need to search and retrieve data from Dataverse repositories.

### Key Features

- 🔍 **Powerful Search**: Advanced search capabilities with filtering, faceting, and geographic queries
- 🌍 **Server Discovery**: Retrieve information about known Dataverse installations worldwide
- 🛡️ **Type-Safe**: Built with Pydantic models for robust data validation
- ⚡ **Performance**: Built-in request caching for improved performance
- 🔧 **Configurable**: Flexible error handling, SSL verification, and session management
- 📚 **Well-Documented**: Comprehensive documentation with examples

### Current Features

- Retrieve server installation information and metadata
- Search datasets, dataverses, and files
- Advanced search with filters, facets, and geographic queries
- Paginated result handling
- Comprehensive error handling
- Request caching support

## Requirements

- Python 3.12 or higher
- uv or pip for package management

## Installation

> **Note**: This package is not yet published on PyPI. Please use the development installation method below.

### Development Installation (Current Method)

To install the package, clone the repository and install locally:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/DataArtifex/dataverse-toolkit.git
   cd dataverse-toolkit
   ```

2. **Install in Editable Mode:**

   Using uv (recommended):
   ```bash
   uv pip install -e ".[dev]"
   ```

   Or using pip:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Using Hatch (Recommended for Development):**

   ```bash
   # Install Hatch
   uv tool install hatch
   
   # Activate development environment
   hatch shell
   
   # Run tests
   hatch run test
   ```

### Future PyPI Release

Once stable, this package will be released on [PyPI](https://pypi.org/). Installation will then be:

#### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dartfx-dataverse
uv pip install dartfx-dataverse
```

#### Using pip

```bash
pip install dartfx-dataverse
```
## Quick Start

### Discover Dataverse Installations

Get a list of known Dataverse installations worldwide:

```python
from dartfx.dataverse import fetch_dataverse_installations

# Fetch all known installations
installations = fetch_dataverse_installations()

# Display first 5
for installation in installations[:5]:
    print(f"{installation.name}: {installation.hostname}")
```

### Connect to a Server

Create a connection to a specific Dataverse server:

```python
from dartfx.dataverse import DataverseServer, ServerInstallation

# Create server installation object
harvard = ServerInstallation(
    name="Harvard Dataverse",
    hostname="dataverse.harvard.edu"
)

# Create server connection
server = DataverseServer(installation=harvard)

# Get server information
info = server.get_server_info()
print(f"Server version: {info['data']['version']}")
```

### Search for Datasets

Perform searches with various options:

```python
from dartfx.dataverse import SearchParameters

# Simple search
results = server.search_simple("climate change")
print(f"Found {results['data']['total_count']} results")

# Advanced search with parameters
params = SearchParameters(
    q="climate change",
    type="dataset",
    per_page=20,
    sort="date",
    order="desc",
    show_facets=True
)

results = server.search(params)
for item in results['data']['items']:
    print(f"- {item['name']}")
```

### More Examples

```python
# Search with filters
params = SearchParameters(
    q="*",
    type="dataset",
    fq=[
        "publicationDate:[2020 TO *]",  # From 2020 onwards
        "authorName:Smith"               # Author is Smith
    ]
)

# Geographic search
params = SearchParameters(
    q="environment",
    geo_point="42.3601,-71.0589",  # Boston, MA
    geo_radius="50"                 # 50 km radius
)

# Search with metadata fields
params = SearchParameters(
    q="health",
    metadata_fields=["citation", "identifier", "subjects"]
)
```

## Documentation

Comprehensive documentation is available, including:

- **Installation Guide**: Detailed installation instructions and requirements
- **Quick Start**: Get up and running in minutes
- **Usage Guide**: In-depth coverage of all features
- **API Reference**: Complete API documentation
- **Examples**: Real-world use cases and code examples
- **Contributing Guide**: How to contribute to the project

Visit the [full documentation](https://dataverse-toolkit.readthedocs.io/) for more details.

## Project Status & Roadmap

### Current Version: 0.1.0 (Development)

This is an early development release. The core functionality is working, but APIs may change.

### Roadmap

#### v0.2.0
- [ ] Pydantic models for search results
- [ ] Enhanced error messages and debugging
- [ ] Batch operation support
- [ ] Progress indicators for long-running operations

#### v0.3.0
- [ ] Dataset metadata retrieval (DDI, Dublin Core, DataCite)
- [ ] File metadata retrieval
- [ ] Support for additional metadata formats (Croissant, schema.org)

#### v0.4.0
- [ ] Dataset and file download capabilities
- [ ] Download progress tracking
- [ ] Resume interrupted downloads

#### v1.0.0
- [ ] Stable API
- [ ] Complete test coverage
- [ ] Performance optimizations
- [ ] Full documentation
## Contributing

We welcome contributions! Here's how you can help:

### Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/dataverse-toolkit.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Set up development environment:
   ```bash
   uv tool install hatch
   hatch shell
   ```

### Development Workflow

```bash
# Run tests
hatch run test

# Run tests with coverage
hatch run cov

# Type checking
hatch run types:check

# Format code
ruff format .

# Lint code
ruff check . --fix
```

### Submitting Changes

1. Make your changes and add tests
2. Ensure all tests pass: `hatch run test`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Submit a pull request

See the [Contributing Guide](CONTRIBUTING.md) for detailed guidelines.

### Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Acknowledgments

- Built with [Pydantic](https://docs.pydantic.dev/) for data validation
- Uses [Requests](https://requests.readthedocs.io/) and [requests-cache](https://requests-cache.readthedocs.io/) for HTTP operations
- Developed using [Hatch](https://hatch.pypa.io/) project manager
- Documentation built with [Sphinx](https://www.sphinx-doc.org/)

## Links

- **Documentation**: https://dataverse-toolkit.readthedocs.io/
- **Source Code**: https://github.com/DataArtifex/dataverse-toolkit
- **Issue Tracker**: https://github.com/DataArtifex/dataverse-toolkit/issues
- **PyPI**: https://pypi.org/project/dartfx-dataverse/
- **Dataverse Project**: https://dataverse.org/

## Support

If you encounter issues or have questions:

1. Check the [documentation](https://dataverse-toolkit.readthedocs.io/)
2. Search [existing issues](https://github.com/DataArtifex/dataverse-toolkit/issues)
3. Create a [new issue](https://github.com/DataArtifex/dataverse-toolkit/issues/new) if needed

## Citation

If you use this package in your research, please cite:

```bibtex
@software{dartfx_dataverse,
  author = {Heus, Pascal},
  title = {dartfx-dataverse: A Python toolkit for Dataverse repositories},
  year = {2024},
  url = {https://github.com/DataArtifex/dataverse-toolkit}
}
```

---

**Maintained by** [Data Artifex](https://github.com/DataArtifex) | **Author**: Pascal Heus
