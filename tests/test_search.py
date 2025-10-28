import pytest
from dartfx.dataverse.dataverse import DataverseServer, SearchParameters

def test_harvard_demo_all(test_server):
    params = SearchParameters()
    data = test_server.search(params)
    print(data)
    assert data

def test_search_all_dataverses(test_server):
    params = SearchParameters(type=["dataverse"], per_page=1)
    data = test_server.search(params)
    print(data)
    assert data

def test_search_all_datasets(test_server):
    params = SearchParameters(type=["dataset"], per_page=1)
    data = test_server.search(params)
    print(data)
    assert data

def test_search_all_files(test_server):
    params = SearchParameters(type=["file"], per_page=1)
    data = test_server.search(params)
    print(data)
    assert data


def test_search_all_files_and_datasets(test_server):
    params = SearchParameters(type="dataset", per_page=1)
    data = test_server.search(params)
    total_datasets = data['data']['total_count']
    params.type = "file"
    data = test_server.search(params)
    total_files = data['data']['total_count']
    params.type = ["dataset", "file"]
    data = test_server.search(params)
    total_both = data['data']['total_count']
    print(f"Datasets: {total_datasets}, Files: {total_files}, Both: {total_both}")
    assert total_datasets + total_files == total_both
    assert data
