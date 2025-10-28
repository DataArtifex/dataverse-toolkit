Examples
========

This page provides real-world examples of using ``dartfx-dataverse`` for common tasks.

Example 1: Find All Climate Datasets
-------------------------------------

Search for all datasets related to climate change published in the last 5 years:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, ServerInstallation, SearchParameters
   
   # Connect to Harvard Dataverse
   server = DataverseServer(
       installation=ServerInstallation(
           name="Harvard Dataverse",
           hostname="dataverse.harvard.edu"
       )
   )
   
   # Search for climate datasets from 2020 onwards
   params = SearchParameters(
       q="climate change OR global warming",
       type="dataset",
       fq=["publicationDate:[2020 TO *]"],
       sort="date",
       order="desc",
       per_page=50,
       show_facets=True
   )
   
   results = server.search(params)
   
   print(f"Found {results['data']['total_count']} datasets\n")
   
   # Display results
   for idx, item in enumerate(results['data']['items'], 1):
       print(f"{idx}. {item['name']}")
       print(f"   Published: {item.get('published_at', 'N/A')}")
       print(f"   URL: {item.get('url', 'N/A')}")
       print()

Example 2: Compare Datasets Across Installations
-------------------------------------------------

Search for datasets across multiple Dataverse installations and compare results:

.. code-block:: python

   from dartfx.dataverse import fetch_dataverse_installations, DataverseServer
   import pandas as pd
   
   # Get all installations
   installations = fetch_dataverse_installations()
   
   # Filter for specific installations with active hostnames
   target_installations = [
       i for i in installations 
       if i.hostname and any(name in i.name.lower() 
           for name in ['harvard', 'demo', 'johns hopkins'])
   ]
   
   # Search across installations
   search_query = "COVID-19"
   results_data = []
   
   for installation in target_installations:
       try:
           server = DataverseServer(installation=installation)
           results = server.search_simple(search_query, per_page=1)
           
           results_data.append({
               'Installation': installation.name,
               'Country': installation.country or 'N/A',
               'Total Results': results['data']['total_count'],
               'Hostname': installation.hostname
           })
       except Exception as e:
           print(f"Error with {installation.name}: {e}")
   
   # Create DataFrame and display
   df = pd.DataFrame(results_data)
   df = df.sort_values('Total Results', ascending=False)
   print(df.to_string(index=False))

Example 3: Download Dataset Metadata
-------------------------------------

Retrieve detailed metadata for datasets matching a query:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, ServerInstallation, SearchParameters
   import json
   
   server = DataverseServer(
       installation=ServerInstallation(
           name="Demo Dataverse",
           hostname="demo.dataverse.org"
       )
   )
   
   # Search with metadata fields
   params = SearchParameters(
       q="education",
       type="dataset",
       per_page=10,
       metadata_fields=[
           "citation",
           "identifier",
           "storageIdentifier",
           "subjects"
       ]
   )
   
   results = server.search(params)
   
   # Save metadata to file
   metadata_list = []
   for item in results['data']['items']:
       metadata = {
           'name': item.get('name'),
           'identifier': item.get('identifier'),
           'citation': item.get('citation'),
           'subjects': item.get('subjects', []),
           'url': item.get('url')
       }
       metadata_list.append(metadata)
   
   # Save to JSON file
   with open('dataset_metadata.json', 'w') as f:
       json.dump(metadata_list, f, indent=2)
   
   print(f"Saved metadata for {len(metadata_list)} datasets")

Example 4: Geographic Search for Environmental Data
----------------------------------------------------

Find environmental datasets within a specific geographic area:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, ServerInstallation, SearchParameters
   
   server = DataverseServer(
       installation=ServerInstallation(
           name="Harvard Dataverse",
           hostname="dataverse.harvard.edu"
       )
   )
   
   # Search within 100km of Boston, MA
   params = SearchParameters(
       q="environment OR ecology OR biodiversity",
       type="dataset",
       geo_point="42.3601,-71.0589",  # Boston coordinates
       geo_radius="100",               # 100 km radius
       per_page=25,
       show_facets=True
   )
   
   results = server.search(params)
   
   print(f"Found {results['data']['total_count']} datasets within 100km of Boston\n")
   
   for item in results['data']['items']:
       print(f"- {item['name']}")
       if 'geolocation' in item:
           print(f"  Location: {item['geolocation']}")

Example 5: Build a Dataset Catalog
-----------------------------------

Create a catalog of datasets from a specific dataverse collection:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, ServerInstallation, SearchParameters
   from datetime import datetime
   import csv
   
   server = DataverseServer(
       installation=ServerInstallation(
           name="Harvard Dataverse",
           hostname="dataverse.harvard.edu"
       )
   )
   
   # Function to paginate through all results
   def get_all_datasets(server, subtree, max_results=1000):
       """Retrieve all datasets from a dataverse collection."""
       datasets = []
       per_page = 100
       start = 0
       
       while len(datasets) < max_results:
           params = SearchParameters(
               q="*",
               type="dataset",
               subtree=subtree,
               per_page=per_page,
               start=start,
               sort="date",
               order="desc"
           )
           
           try:
               results = server.search(params)
               items = results['data']['items']
               
               if not items:
                   break
               
               datasets.extend(items)
               start += per_page
               
               print(f"Retrieved {len(datasets)} datasets...")
               
           except Exception as e:
               print(f"Error: {e}")
               break
       
       return datasets[:max_results]
   
   # Get datasets from a specific dataverse
   datasets = get_all_datasets(server, "your-dataverse-name", max_results=500)
   
   # Export to CSV
   with open('dataset_catalog.csv', 'w', newline='', encoding='utf-8') as f:
       writer = csv.DictWriter(f, fieldnames=[
           'name', 'identifier', 'type', 'url', 'published_at', 'description'
       ])
       writer.writeheader()
       
       for ds in datasets:
           writer.writerow({
               'name': ds.get('name', ''),
               'identifier': ds.get('identifier', ''),
               'type': ds.get('type', ''),
               'url': ds.get('url', ''),
               'published_at': ds.get('published_at', ''),
               'description': ds.get('description', '')[:200]  # Truncate
           })
   
   print(f"\nExported {len(datasets)} datasets to dataset_catalog.csv")

Example 6: Find Datasets by Author
-----------------------------------

Search for all datasets by a specific author:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, ServerInstallation, SearchParameters
   
   server = DataverseServer(
       installation=ServerInstallation(
           name="Harvard Dataverse",
           hostname="dataverse.harvard.edu"
       )
   )
   
   # Search by author name
   author_name = "Smith"
   params = SearchParameters(
       q=f"authorName:{author_name}",
       type="dataset",
       per_page=50,
       sort="date",
       order="desc",
       show_facets=True
   )
   
   results = server.search(params)
   
   print(f"Datasets by {author_name}: {results['data']['total_count']}\n")
   
   for item in results['data']['items']:
       print(f"Title: {item['name']}")
       if 'authors' in item:
           authors = ', '.join(item['authors'])
           print(f"Authors: {authors}")
       print(f"Published: {item.get('published_at', 'N/A')}")
       print()

Example 7: Monitor New Datasets
--------------------------------

Check for newly published datasets since a specific date:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, ServerInstallation, SearchParameters
   from datetime import datetime, timedelta
   
   server = DataverseServer(
       installation=ServerInstallation(
           name="Harvard Dataverse",
           hostname="dataverse.harvard.edu"
       )
   )
   
   # Calculate date range (last 7 days)
   end_date = datetime.now()
   start_date = end_date - timedelta(days=7)
   
   # Format dates for Dataverse query
   date_query = f"publicationDate:[{start_date.strftime('%Y-%m-%d')} TO {end_date.strftime('%Y-%m-%d')}]"
   
   params = SearchParameters(
       q="*",
       type="dataset",
       fq=[date_query],
       sort="date",
       order="desc",
       per_page=100
   )
   
   results = server.search(params)
   
   print(f"New datasets in the last 7 days: {results['data']['total_count']}\n")
   
   for item in results['data']['items']:
       print(f"- {item['name']}")
       print(f"  Published: {item.get('published_at')}")
       print(f"  URL: {item.get('url')}")
       print()

Example 8: Subject-Based Analysis
----------------------------------

Analyze the distribution of datasets across different subjects:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, ServerInstallation, SearchParameters
   from collections import Counter
   
   server = DataverseServer(
       installation=ServerInstallation(
           name="Harvard Dataverse",
           hostname="dataverse.harvard.edu"
       )
   )
   
   # Search with facets enabled
   params = SearchParameters(
       q="*",
       type="dataset",
       per_page=100,
       show_facets=True
   )
   
   results = server.search(params)
   
   # Extract subject facets
   subject_counts = {}
   if 'facets' in results['data']:
       for facet in results['data']['facets']:
           if facet.get('name') == 'subject_ss':
               for label in facet.get('labels', []):
                   subject_counts[label['label']] = label['count']
   
   # Display top 10 subjects
   print("Top 10 Subjects:\n")
   for subject, count in sorted(subject_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
       print(f"{subject}: {count} datasets")

Example 9: Batch Export Dataset Information
--------------------------------------------

Export information for multiple datasets based on identifiers:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, ServerInstallation, SearchParameters
   import json
   
   server = DataverseServer(
       installation=ServerInstallation(
           name="Harvard Dataverse",
           hostname="dataverse.harvard.edu"
       )
   )
   
   # List of dataset identifiers to export
   dataset_identifiers = [
       "doi:10.7910/DVN/XXXXX1",
       "doi:10.7910/DVN/XXXXX2",
       "doi:10.7910/DVN/XXXXX3",
   ]
   
   exported_data = []
   
   for identifier in dataset_identifiers:
       try:
           params = SearchParameters(
               q=f"identifier:{identifier}",
               type="dataset",
               per_page=1
           )
           
           results = server.search(params)
           
           if results['data']['items']:
               item = results['data']['items'][0]
               exported_data.append({
                   'identifier': identifier,
                   'name': item.get('name'),
                   'url': item.get('url'),
                   'citation': item.get('citation'),
                   'published_at': item.get('published_at')
               })
               print(f"✓ Exported: {identifier}")
           else:
               print(f"✗ Not found: {identifier}")
       
       except Exception as e:
           print(f"✗ Error with {identifier}: {e}")
   
   # Save to file
   with open('batch_export.json', 'w') as f:
       json.dump(exported_data, f, indent=2)
   
   print(f"\nExported {len(exported_data)} datasets")

Example 10: Create a Simple Search Interface
---------------------------------------------

Build a simple command-line search interface:

.. code-block:: python

   from dartfx.dataverse import DataverseServer, ServerInstallation, SearchParameters
   
   def search_interface():
       """Simple interactive search interface."""
       
       # Setup server
       server = DataverseServer(
           installation=ServerInstallation(
               name="Harvard Dataverse",
               hostname="dataverse.harvard.edu"
           )
       )
       
       print("=== Dataverse Search Interface ===\n")
       
       while True:
           # Get search query
           query = input("Enter search term (or 'quit' to exit): ").strip()
           
           if query.lower() == 'quit':
               break
           
           if not query:
               continue
           
           # Get number of results
           try:
               num_results = int(input("Number of results (default 10): ") or "10")
           except ValueError:
               num_results = 10
           
           # Perform search
           try:
               params = SearchParameters(
                   q=query,
                   type="dataset",
                   per_page=num_results
               )
               
               results = server.search(params)
               
               print(f"\nFound {results['data']['total_count']} total results")
               print(f"Showing top {len(results['data']['items'])}:\n")
               
               for idx, item in enumerate(results['data']['items'], 1):
                   print(f"{idx}. {item['name']}")
                   print(f"   {item.get('url', 'N/A')}")
                   print()
               
           except Exception as e:
               print(f"Error: {e}\n")
   
   if __name__ == "__main__":
       search_interface()

More Examples
-------------

For more examples and use cases, check out:

* The `examples` directory in the GitHub repository
* The test suite in the `tests` directory
* Community contributions and discussions on GitHub
