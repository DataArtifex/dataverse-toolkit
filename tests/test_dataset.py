import pytest

from dartfx.dataverse import DataverseServer, ServerInstallation


@pytest.fixture
def server():
    """Fixture for interacting with Borealis Dataverse."""
    installation = ServerInstallation(name="Borealis", hostname="borealisdata.ca")
    return DataverseServer(installation)


def test_get_dataset(server):
    """Test retrieving dataset metadata by persistent identifier."""
    # Using a dataset identifier found in the repository search example
    identifier = "doi:10.5683/SP3/N5BRUY"
    result = server.get_dataset(identifier)

    assert result["status"] == "OK"
    assert "data" in result
    assert result["data"]["protocol"] == "doi"
    assert result["data"]["authority"] == "10.5683"


def test_get_dataset_export(server):
    """Test retrieving a dataset in an export format."""
    # Using the identifier from the user request
    identifier = "doi:10.5683/SP3/FNS9EF"

    # Test with Dublin Core (oai_dc)
    result = server.get_dataset_export(identifier, "oai_dc")

    # Export results are often strings (XML/JSON/etc.)
    assert isinstance(result, str)
    assert "<oai_dc:dc" in result or "Dublin Core" in result


def test_get_dataset_export_ddi(server):
    """Test retrieving a dataset in DDI export format."""
    identifier = "doi:10.5683/SP3/FNS9EF"
    result = server.get_dataset_export(identifier, "ddi")

    assert isinstance(result, str)
    assert "codeBook" in result or "DDI" in result
