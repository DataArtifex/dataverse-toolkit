from dartfx.dataverse.dataverse import DataverseServer, SearchParameters


def test_harvard_demo_all(test_server: DataverseServer) -> None:
    params = SearchParameters()
    data = test_server.search(params)
    print(data)
    assert data


def test_search_all_dataverses(test_server: DataverseServer) -> None:
    params = SearchParameters(type=["dataverse"], per_page=1)
    data = test_server.search(params)
    print(data)
    assert data


def test_search_all_datasets(test_server: DataverseServer) -> None:
    params = SearchParameters(type=["dataset"], per_page=1)
    data = test_server.search(params)
    print(data)
    assert data


def test_search_all_files(test_server: DataverseServer) -> None:
    params = SearchParameters(type=["file"], per_page=1)
    data = test_server.search(params)
    print(data)
    assert data


def test_search_all_files_and_datasets(test_server: DataverseServer) -> None:
    params = SearchParameters(type="dataset", per_page=1)
    data = test_server.search(params)
    total_datasets = data["data"]["total_count"]
    params.type = "file"
    data = test_server.search(params)
    total_files = data["data"]["total_count"]
    params.type = ["dataset", "file"]
    data = test_server.search(params)
    total_both = data["data"]["total_count"]
    print(f"Datasets: {total_datasets}, Files: {total_files}, Both: {total_both}")
    assert total_datasets + total_files == total_both
    assert data


def test_cli_search_command(monkeypatch):
    import json

    from typer.testing import CliRunner

    from dartfx.dataverse.cli import app

    mock_results = {
        "status": "OK",
        "data": {
            "total_count": 1,
            "items": [
                {
                    "type": "dataset",
                    "name": "Test Study on Climate",
                    "global_id": "doi:10.5072/FK2/TEST123",
                    "url": "https://doi.org/10.5072/FK2/TEST123",
                    "published_at": "2026-01-01T00:00:00Z",
                }
            ],
        },
    }

    class MockServer:
        def search(self, _params):
            return mock_results

    monkeypatch.setattr("dartfx.dataverse.cli.get_server", lambda *_args, **_kwargs: MockServer())

    runner = CliRunner()
    result_table = runner.invoke(app, ["search", "climate", "--limit", "1"])
    assert result_table.exit_code == 0
    assert "Test Study" in result_table.stdout
    assert "dataset" in result_table.stdout

    result_csv = runner.invoke(app, ["search", "climate", "--format", "csv"])
    assert result_csv.exit_code == 0
    assert "url" in result_csv.stdout
    assert "https://doi.org/10.5072/FK2/TEST123" in result_csv.stdout

    result_json = runner.invoke(app, ["search", "climate", "--format", "json"])
    assert result_json.exit_code == 0
    data = json.loads(result_json.stdout)
    assert data["data"]["total_count"] == 1
