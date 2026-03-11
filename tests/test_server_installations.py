from dartfx.dataverse.dataverse import DataverseServer


def test_fetch_dataverse_installations() -> None:
    from dartfx.dataverse.dataverse import fetch_dataverse_installations

    installations = fetch_dataverse_installations()
    assert len(installations) > 0


def test_harvard_demo_info(test_server: DataverseServer) -> None:
    server_info = test_server.get_info_server()
    print(server_info)
    assert server_info
    version_info = test_server.get_info_version()
    print(version_info)
    assert version_info


def test_lookup_installation() -> None:
    server = DataverseServer("dataverse.harvard.edu")
    print(server.installation)
    assert server.installation.name == "Harvard Dataverse"


def test_no_lookup_installation() -> None:
    server = DataverseServer("dataverse.harvard.edu", lookup_installation=False)
    print(server.installation)
    assert server.installation.name is None


def test_strip_https_prefix() -> None:
    server = DataverseServer("https://data.harvard.edu", lookup_installation=False)
    print(server.installation)
    assert server.installation.hostname == "dataverse.harvard.edu"
