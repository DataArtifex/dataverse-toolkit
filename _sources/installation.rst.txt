Installation
============

.. important::
   **This package is not yet published on PyPI.** Please use the development 
   installation method below. Once the package is stable, it will be released 
   on PyPI for easier installation.

Requirements
------------

* Python 3.12 or higher
* uv (recommended) or pip (Python package installer)
* Git (for cloning the repository)

.. note::
   We recommend using `uv <https://github.com/astral-sh/uv>`_, a fast Python package 
   installer and resolver written in Rust. It's significantly faster than pip and 
   provides better dependency resolution.

Development Installation (Current Method)
------------------------------------------

Since the package is not yet on PyPI, you must clone the repository and install locally.

1. **Clone the Repository**

   .. code-block:: bash

      git clone https://github.com/DataArtifex/dataverse-toolkit.git
      cd dataverse-toolkit

2. **Install in Editable Mode**

   Using uv (recommended):

   .. code-block:: bash

      # Install uv if you haven't already
      curl -LsSf https://astral.sh/uv/install.sh | sh
      
      # Install the package in editable mode
      uv pip install -e .
      
      # Or with development dependencies
      uv pip install -e ".[dev]"

   Using pip:

   .. code-block:: bash

      pip install -e .
      
      # Or with development dependencies
      pip install -e ".[dev]"

Using Hatch (Recommended for Development)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project uses Hatch for development. Hatch will automatically use uv if available:

.. code-block:: bash

   # Install Hatch (will use uv if available)
   uv tool install hatch
   
   # Or using pip
   pip install hatch

   # Create and activate default environment
   hatch shell

   # Run tests
   hatch run test

   # Run tests with coverage
   hatch run cov

   # Type checking
   hatch run types:check

Dependencies
------------

Core Dependencies
~~~~~~~~~~~~~~~~~

* **pydantic** (>=2.0.0) - Data validation using Python type annotations
* **requests** (>=2.31.0) - HTTP library for Python
* **requests-cache** (>=1.0.0) - Persistent cache for requests

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~

Development Tools (``[dev]``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **pytest** (>=7.0) - Testing framework
* **coverage** (>=6.5) - Code coverage measurement
* **mypy** (>=1.0.0) - Static type checker
* **ruff** (>=0.1.0) - Fast Python linter and formatter

Documentation Tools (``[docs]``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **sphinx** (>=7.0) - Documentation generator
* **sphinx-rtd-theme** (>=2.0) - Read the Docs theme for Sphinx

Installing with Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For development installation (current method), use editable mode with optional dependencies:

Using uv (recommended):

.. code-block:: bash

   # Install with development tools
   uv pip install -e ".[dev]"

   # Install with documentation tools
   uv pip install -e ".[docs]"

   # Install with all optional dependencies
   uv pip install -e ".[dev,docs]"

Using pip:

.. code-block:: bash

   # Install with development tools
   pip install -e ".[dev]"

   # Install with documentation tools
   pip install -e ".[docs]"

   # Install with all optional dependencies
   pip install -e ".[dev,docs]"

Future PyPI Installation
-------------------------

Once the package is stable and officially released on PyPI, you will be able to install it with:

Using uv (Recommended)
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install the package
   uv pip install dartfx-dataverse
   
   # With optional dependencies
   uv pip install dartfx-dataverse[dev,docs]

Using pip
~~~~~~~~~

.. code-block:: bash

   pip install dartfx-dataverse
   
   # With optional dependencies
   pip install dartfx-dataverse[dev,docs]

Verifying Installation
----------------------

To verify that the package is installed correctly:

.. code-block:: python

   import dartfx.dataverse
   from dartfx.dataverse.__about__ import __version__
   
   print(f"dartfx-dataverse version: {__version__}")

You should see the version number printed without any errors.

Troubleshooting
---------------

Import Errors
~~~~~~~~~~~~~

If you encounter import errors, ensure that:

1. You have Python 3.12 or higher installed
2. The package is installed in the correct Python environment
3. Your ``PYTHONPATH`` is set correctly if using a development installation

SSL Certificate Errors
~~~~~~~~~~~~~~~~~~~~~~~

If you encounter SSL certificate errors when connecting to Dataverse servers:

.. code-block:: python

   from dartfx.dataverse import DataverseServer
   
   # Disable SSL verification (not recommended for production)
   server = DataverseServer(
       installation=installation,
       ssl_verify=False
   )

.. warning::
   Disabling SSL verification should only be done in development environments 
   or when absolutely necessary. It makes your connection vulnerable to 
   man-in-the-middle attacks.

Upgrading
---------

To upgrade to the latest version:

Using uv (recommended):

.. code-block:: bash

   uv pip install --upgrade dartfx-dataverse

Using pip:

.. code-block:: bash

   pip install --upgrade dartfx-dataverse

To upgrade to a specific version:

.. code-block:: bash

   uv pip install dartfx-dataverse==X.Y.Z

Uninstalling
------------

To uninstall the package:

.. code-block:: bash

   uv pip uninstall dartfx-dataverse
   
   # Or using pip
   pip uninstall dartfx-dataverse
