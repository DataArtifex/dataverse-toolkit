from dartfx.dataverse import DataverseServer, ServerInstallation


def test_get_info_export_formats():
    """Test fetching export formats from Harvard Dataverse."""
    installation = ServerInstallation(hostname="dataverse.harvard.edu")
    server = DataverseServer(server=installation)

    results = server.get_info_export_formats()

    assert results is not None
    assert results.get("status") == "OK"
    assert "data" in results
    assert isinstance(results["data"], dict)

    # Check for some common formats
    formats = results["data"]
    assert "ddi" in formats or "Datacite" in formats or "dataverse_json" in formats
