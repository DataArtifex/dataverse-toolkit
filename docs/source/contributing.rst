Contributing
============

We welcome contributions to ``dartfx-dataverse``! This guide will help you get started.

Getting Started
---------------

1. **Fork the Repository**

   Fork the repository on GitHub and clone your fork:

   .. code-block:: bash

      git clone https://github.com/YOUR-USERNAME/dataverse-toolkit.git
      cd dataverse-toolkit

2. **Set Up Development Environment**

   Install Hatch (which will use uv if available):

   .. code-block:: bash

      # Install uv first (recommended)
      curl -LsSf https://astral.sh/uv/install.sh | sh
      
      # Install Hatch
      uv tool install hatch
      
      # Or using pip
      pip install hatch

   Create and activate a development environment:

   .. code-block:: bash

      hatch shell

3. **Install Pre-commit Hooks** (Optional but Recommended)

   .. code-block:: bash

      uv pip install pre-commit
      # Or: pip install pre-commit
      pre-commit install

Development Workflow
--------------------

Making Changes
~~~~~~~~~~~~~~

1. Create a new branch for your feature or fix:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. Make your changes to the code

3. Write tests for your changes

4. Run the test suite:

   .. code-block:: bash

      hatch run test

5. Check code coverage:

   .. code-block:: bash

      hatch run cov

6. Run type checking:

   .. code-block:: bash

      hatch run types:check

7. Format and lint your code:

   .. code-block:: bash

      ruff format .
      ruff check . --fix

Code Style
~~~~~~~~~~

We use Ruff for linting and formatting. The configuration is in ``pyproject.toml``.

* Line length: 100 characters
* Follow PEP 8 guidelines
* Use type hints for all functions
* Write descriptive docstrings

Writing Tests
-------------

Test Structure
~~~~~~~~~~~~~~

Tests are located in the ``tests/`` directory. We use pytest for testing.

.. code-block:: python

   # tests/test_feature.py
   import pytest
   from dartfx.dataverse import DataverseServer, ServerInstallation
   
   def test_my_feature():
       """Test description."""
       # Arrange
       server = DataverseServer(
           installation=ServerInstallation(
               name="Test",
               hostname="test.example.com"
           )
       )
       
       # Act
       result = server.some_method()
       
       # Assert
       assert result is not None
       assert isinstance(result, dict)

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   hatch run test
   
   # Run specific test file
   hatch run test tests/test_search.py
   
   # Run specific test
   hatch run test tests/test_search.py::test_search_simple
   
   # Run with coverage
   hatch run cov

Documentation
-------------

Writing Documentation
~~~~~~~~~~~~~~~~~~~~~

Documentation is written in reStructuredText and built with Sphinx.

1. Documentation source is in ``docs/source/``
2. Build documentation:

   .. code-block:: bash

      hatch run docs:build

3. View documentation locally:

   .. code-block:: bash

      hatch run docs:serve
      # Open http://localhost:8000 in your browser

4. Clean build files:

   .. code-block:: bash

      hatch run docs:clean

Docstring Format
~~~~~~~~~~~~~~~~

We use Google-style docstrings:

.. code-block:: python

   def search(self, query: str, per_page: int = 10) -> dict:
       """Execute a search query.
       
       This method searches the Dataverse installation using the
       provided query parameters.
       
       Args:
           query: The search term or terms to query for
           per_page: Number of results to return per page
           
       Returns:
           A dictionary containing search results and metadata
           
       Raises:
           DataverseApiError: If the API request fails
           
       Example:
           >>> server = DataverseServer(installation=inst)
           >>> results = server.search("climate")
           >>> print(results['data']['total_count'])
       """
       pass

Submitting Changes
------------------

Pull Request Process
~~~~~~~~~~~~~~~~~~~~

1. **Commit Your Changes**

   Write clear, descriptive commit messages:

   .. code-block:: bash

      git add .
      git commit -m "Add feature: description of your change"

2. **Push to Your Fork**

   .. code-block:: bash

      git push origin feature/your-feature-name

3. **Create Pull Request**

   * Go to the original repository on GitHub
   * Click "New Pull Request"
   * Select your fork and branch
   * Fill out the PR template with:
     
     * Description of changes
     * Related issues
     * Testing performed
     * Screenshots (if applicable)

4. **Address Review Comments**

   * Respond to reviewer feedback
   * Make requested changes
   * Push additional commits to your branch

Pull Request Checklist
~~~~~~~~~~~~~~~~~~~~~~

Before submitting, ensure:

* [ ] Tests pass locally
* [ ] Code is formatted with Ruff
* [ ] Type checking passes
* [ ] Documentation is updated
* [ ] Commit messages are clear
* [ ] No merge conflicts
* [ ] Changes are focused and atomic

Code Review
-----------

What We Look For
~~~~~~~~~~~~~~~~

* **Correctness**: Does the code work as intended?
* **Tests**: Are there tests for new functionality?
* **Style**: Does it follow project conventions?
* **Documentation**: Is it well-documented?
* **Performance**: Are there any performance concerns?
* **Security**: Are there any security issues?

Review Process
~~~~~~~~~~~~~~

1. Maintainers will review your PR
2. Feedback will be provided as comments
3. You may need to make changes
4. Once approved, maintainers will merge

Reporting Bugs
--------------

Bug Report Guidelines
~~~~~~~~~~~~~~~~~~~~~

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Minimal steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**:
   
   * Python version
   * Package version
   * Operating system

6. **Code Sample**: Minimal code that reproduces the issue

Example Bug Report:

.. code-block:: markdown

   ## Bug Description
   Search fails when using geo_point parameter
   
   ## Steps to Reproduce
   ```python
   from dartfx.dataverse import DataverseServer, SearchParameters
   
   server = DataverseServer(installation=...)
   params = SearchParameters(
       q="*",
       geo_point="42.3,-71.1",
       geo_radius="10"
   )
   results = server.search(params)  # Fails here
   ```
   
   ## Expected Behavior
   Should return search results within 10km radius
   
   ## Actual Behavior
   Raises DataverseApiError with status 400
   
   ## Environment
   - Python: 3.12.0
   - dartfx-dataverse: 0.1.0
   - OS: macOS 14.0

Feature Requests
----------------

We welcome feature requests! Please:

1. Check if the feature already exists or is planned
2. Describe the use case clearly
3. Provide examples of how it would work
4. Explain why it would be valuable

Community Guidelines
--------------------

Code of Conduct
~~~~~~~~~~~~~~~

This project follows the `Contributor Covenant Code of Conduct <https://github.com/DataArtifex/dataverse-toolkit/blob/main/CODE_OF_CONDUCT.md>`_.

* Be respectful and inclusive
* Welcome newcomers
* Give constructive feedback
* Focus on what's best for the community

Communication
~~~~~~~~~~~~~

* GitHub Issues: Bug reports and feature requests
* GitHub Discussions: General questions and ideas
* Pull Requests: Code contributions

Getting Help
------------

If you need help:

1. Check the documentation
2. Search existing issues
3. Ask in GitHub Discussions
4. Create a new issue with the "question" label

Development Tips
----------------

Useful Commands
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   hatch run test
   
   # Run tests with coverage
   hatch run cov
   
   # Type checking
   hatch run types:check
   
   # Format code
   ruff format .
   
   # Lint code
   ruff check .
   
   # Fix linting issues
   ruff check . --fix
   
   # Build documentation
   hatch run docs:build
   
   # Serve documentation locally
   hatch run docs:serve

Debugging Tests
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run with verbose output
   hatch run test -v
   
   # Run with print statements
   hatch run test -s
   
   # Drop into debugger on failure
   hatch run test --pdb

Working with Virtual Environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create environment
   hatch env create
   
   # Activate shell
   hatch shell
   
   # Run command in environment
   hatch run python --version
   
   # Remove environment
   hatch env remove

Release Process
---------------

For Maintainers
~~~~~~~~~~~~~~~

1. Update version in ``src/dartfx/dataverse/__about__.py``
2. Update ``CHANGELOG.md``
3. Create a git tag: ``git tag vX.Y.Z``
4. Push tag: ``git push origin vX.Y.Z``
5. Create GitHub release
6. Build and publish to PyPI:

   .. code-block:: bash

      hatch build
      hatch publish

Thank You!
----------

Thank you for contributing to ``dartfx-dataverse``! Your contributions help 
make this project better for everyone.
