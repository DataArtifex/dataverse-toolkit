Exceptions
==========

This page documents the exceptions used in ``dartfx-dataverse`` for error handling.

DataverseApiError
-----------------

The main exception class for API-related errors.

.. autoclass:: dartfx.dataverse.DataverseApiError
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __str__

   .. rubric:: Attributes

   .. attribute:: message
      :type: str
      
      Human-readable error message describing what went wrong.

   .. attribute:: url
      :type: str
      
      The URL that was being accessed when the error occurred.

   .. attribute:: status_code
      :type: int | None
      
      HTTP status code from the response, if available.

   .. attribute:: response
      :type: requests.Response | None
      
      The raw response object from the failed request, if available.

Common HTTP Status Codes
-------------------------

The exception includes HTTP status codes to help identify the type of error:

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Code
     - Status
     - Description
   * - 400
     - Bad Request
     - Invalid request parameters or malformed query
   * - 401
     - Unauthorized
     - Missing or invalid API key
   * - 403
     - Forbidden
     - Insufficient permissions to access resource
   * - 404
     - Not Found
     - Resource does not exist
   * - 429
     - Too Many Requests
     - Rate limit exceeded
   * - 500
     - Internal Server Error
     - Server-side error
   * - 502
     - Bad Gateway
     - Gateway or proxy error
   * - 503
     - Service Unavailable
     - Server is temporarily unavailable
   * - 504
     - Gateway Timeout
     - Gateway or proxy timeout

Usage Examples
--------------

Basic Error Handling
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from dartfx.dataverse import DataverseServer, DataverseApiError, ServerInstallation
   
   server = DataverseServer(
       installation=ServerInstallation(
           name="Test",
           hostname="dataverse.example.com"
       )
   )
   
   try:
       results = server.search_simple("test")
   except DataverseApiError as e:
       print(f"Error: {e.message}")
       print(f"Status Code: {e.status_code}")
       print(f"URL: {e.url}")

Handling Specific Status Codes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   try:
       results = server.search_simple("test")
   except DataverseApiError as e:
       if e.status_code == 404:
           print("Resource not found")
       elif e.status_code == 401:
           print("Authentication failed - check your API key")
       elif e.status_code == 429:
           print("Rate limit exceeded - please wait before retrying")
       elif e.status_code and e.status_code >= 500:
           print(f"Server error ({e.status_code}) - try again later")
       else:
           print(f"Unexpected error: {e}")

Accessing Response Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   try:
       results = server.search_simple("test")
   except DataverseApiError as e:
       print(f"Error: {e.message}")
       
       # Access raw response if available
       if e.response:
           print(f"Response Status: {e.response.status_code}")
           print(f"Response Headers: {e.response.headers}")
           print(f"Response Text: {e.response.text}")
           
           # Try to parse JSON error response
           try:
               error_data = e.response.json()
               print(f"Error Data: {error_data}")
           except ValueError:
               print("Response is not JSON")

Retry on Specific Errors
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from time import sleep
   
   def search_with_retry(server, query, max_retries=3):
       """Retry search on specific error codes."""
       for attempt in range(max_retries):
           try:
               return server.search_simple(query)
           except DataverseApiError as e:
               # Retry on server errors or rate limiting
               if e.status_code in [429, 500, 502, 503, 504]:
                   if attempt < max_retries - 1:
                       wait_time = 2 ** attempt  # Exponential backoff
                       print(f"Retry {attempt + 1}/{max_retries} in {wait_time}s...")
                       sleep(wait_time)
                       continue
               # Re-raise for all other errors
               raise
       
       raise DataverseApiError(
           "Max retries exceeded",
           server.installation.hostname or "",
           None,
           None
       )

Logging Errors
~~~~~~~~~~~~~~

.. code-block:: python

   import logging
   
   logger = logging.getLogger(__name__)
   
   try:
       results = server.search_simple("test")
   except DataverseApiError as e:
       logger.error(
           "Dataverse API Error",
           extra={
               "message": e.message,
               "url": e.url,
               "status_code": e.status_code,
               "server": server.installation.name
           }
       )
       # Optionally re-raise
       raise

Silent Error Handling
~~~~~~~~~~~~~~~~~~~~~~

Use ``on_api_error="none"`` to suppress exceptions:

.. code-block:: python

   # Configure server to return None on errors
   server = DataverseServer(
       installation=installation,
       on_api_error="none"
   )
   
   # No exception will be raised
   result = server.get_server_info()
   
   if result is None:
       print("An error occurred, but was suppressed")
   else:
       print(f"Server version: {result['data']['version']}")

Graceful Degradation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def get_server_info_safe(server):
       """Get server info with fallback."""
       try:
           return server.get_server_info()
       except DataverseApiError as e:
           if e.status_code == 404:
               return {
                   "status": "error",
                   "message": "Info endpoint not available",
                   "data": {}
               }
           elif e.status_code and e.status_code >= 500:
               return {
                   "status": "error",
                   "message": "Server temporarily unavailable",
                   "data": {}
               }
           else:
               raise  # Re-raise unexpected errors
   
   info = get_server_info_safe(server)

Multiple Exception Types
~~~~~~~~~~~~~~~~~~~~~~~~~

Handle both API and network errors:

.. code-block:: python

   import requests
   from dartfx.dataverse import DataverseApiError
   
   try:
       results = server.search_simple("test")
   except DataverseApiError as e:
       print(f"API Error: {e.message}")
   except requests.RequestException as e:
       print(f"Network Error: {e}")
   except Exception as e:
       print(f"Unexpected Error: {e}")

Context Managers
~~~~~~~~~~~~~~~~

Use context managers for cleanup:

.. code-block:: python

   from contextlib import contextmanager
   
   @contextmanager
   def handle_dataverse_errors():
       """Context manager for Dataverse error handling."""
       try:
           yield
       except DataverseApiError as e:
           print(f"Dataverse API Error: {e}")
           if e.status_code == 401:
               print("Please check your API key")
           elif e.status_code == 429:
               print("Rate limit exceeded")
   
   # Usage
   with handle_dataverse_errors():
       results = server.search_simple("test")

Best Practices
--------------

1. **Always Catch Specific Exceptions**
   
   Catch ``DataverseApiError`` specifically instead of generic ``Exception``:

   .. code-block:: python

      # Good
      try:
          results = server.search_simple("test")
      except DataverseApiError as e:
          handle_api_error(e)
      
      # Avoid
      try:
          results = server.search_simple("test")
      except Exception as e:  # Too broad
          pass

2. **Check Status Codes**
   
   Different status codes require different handling:

   .. code-block:: python

      try:
          results = server.search_simple("test")
      except DataverseApiError as e:
          if e.status_code == 429:
              # Implement backoff
              pass
          elif e.status_code >= 500:
              # Log and alert
              pass
          else:
              # Handle client errors
              pass

3. **Provide User-Friendly Messages**
   
   Translate technical errors to user-friendly messages:

   .. code-block:: python

      try:
          results = server.search_simple("test")
      except DataverseApiError as e:
          if e.status_code == 404:
              print("The requested resource was not found")
          elif e.status_code == 401:
              print("Please provide valid credentials")
          else:
              print(f"An error occurred: {e.message}")

4. **Log for Debugging**
   
   Always log errors for troubleshooting:

   .. code-block:: python

      import logging
      
      logger = logging.getLogger(__name__)
      
      try:
          results = server.search_simple("test")
      except DataverseApiError as e:
          logger.exception("Failed to search Dataverse", extra={
              "url": e.url,
              "status_code": e.status_code
          })

5. **Implement Retry Logic**
   
   For transient errors, implement exponential backoff:

   .. code-block:: python

      from time import sleep
      
      retryable_codes = [429, 500, 502, 503, 504]
      
      for attempt in range(3):
          try:
              results = server.search_simple("test")
              break
          except DataverseApiError as e:
              if e.status_code in retryable_codes and attempt < 2:
                  sleep(2 ** attempt)
              else:
                  raise

Related
-------

* :doc:`server` - Server connection configuration
* :doc:`search` - Search functionality
* :class:`~dartfx.dataverse.DataverseServer` - Main server class
