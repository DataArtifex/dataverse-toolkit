API Reference
=============

This section provides detailed documentation for all classes, functions, and modules 
in the ``dartfx-dataverse`` package.

Overview
--------

The package is organized into the following main components:

* :doc:`server` - Server connection and management classes
* :doc:`search` - Search functionality and parameters
* :doc:`models` - Data models and validation
* :doc:`exceptions` - Error handling and exceptions

Quick Links
-----------

Main Classes
~~~~~~~~~~~~

* :class:`~dartfx.dataverse.DataverseServer` - Main server connection class
* :class:`~dartfx.dataverse.ServerInstallation` - Server installation information
* :class:`~dartfx.dataverse.SearchParameters` - Search query parameters
* :class:`~dartfx.dataverse.DataverseApiError` - API error exception

Main Functions
~~~~~~~~~~~~~~

* :func:`~dartfx.dataverse.fetch_dataverse_installations` - Fetch known installations

Complete API
------------

.. toctree::
   :maxdepth: 2
   
   server
   search
   models
   exceptions

Module Contents
---------------

.. automodule:: dartfx.dataverse
   :members:
   :undoc-members:
   :show-inheritance:
