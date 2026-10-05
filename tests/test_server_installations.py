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
    server = DataverseServer("https://dataverse.harvard.edu", lookup_installation=False)
    print(server.installation)
    assert server.installation.hostname == "dataverse.harvard.edu"


def test_default_server_from_env(monkeypatch) -> None:
    monkeypatch.setenv("DATAVERSE_SERVER", "dataverse.nl")
    server = DataverseServer()
    assert server.installation.hostname == "dataverse.nl"


def test_dotenv_loaded():
    from dotenv import find_dotenv

    # find_dotenv should find root .env if it exists
    env_file = find_dotenv(usecwd=True)
    assert env_file is not None


def test_server_installation_country_code_derivation():
    from dartfx.dataverse.dataverse import ServerInstallation

    inst = ServerInstallation(name="Test Server", hostname="https://dataverse.example.org/", country="United States")
    assert inst.country_code == "US"
    assert inst.clean_hostname == "dataverse.example.org"
    assert inst.url == "https://dataverse.example.org"


def test_server_installation_extra_fields():
    from dartfx.dataverse.dataverse import ServerInstallation

    inst = ServerInstallation(
        name="Test Hub",
        hostname="hub.dataverse.org",
        about_url="https://about.dataverse.org",
        dv_hub_id="hub-123",
        extra_unknown_field="ignored",
    )
    assert inst.about_url == "https://about.dataverse.org"
    assert inst.dv_hub_id == "hub-123"


def test_country_crosswalk_and_matching():
    from dartfx.dataverse.dataverse import get_iso2_code, matches_country

    assert get_iso2_code("Netherlands") == "NL"
    assert get_iso2_code("USA") == "US"
    assert get_iso2_code("Germany") == "DE"
    assert get_iso2_code("Deutschland") == "DE"
    assert get_iso2_code("FR") == "FR"
    assert get_iso2_code("Slovenia") == "SI"
    assert get_iso2_code("Botswana") == "BW"
    assert get_iso2_code("Croatia") == "HR"
    assert get_iso2_code("Hong Kong") == "HK"
    assert get_iso2_code("Taiwan (ROC)") == "TW"
    assert get_iso2_code("Taiwan") == "TW"
    assert get_iso2_code("Ukraine") == "UA"
    assert get_iso2_code("Iceland") == "IS"
    assert get_iso2_code("Ecuador") == "EC"
    assert get_iso2_code("Luxembourg") == "LU"
    assert get_iso2_code("Uruguay") == "UY"

    # Match by ISO-2 code
    assert matches_country("NL", "Netherlands") is True
    assert matches_country("US", "United States") is True
    assert matches_country("US", "Netherlands") is False
    assert matches_country("SI", "Slovenia") is True
    assert matches_country("TW", "Taiwan (ROC)") is True

    # Match by country name
    assert matches_country("Netherlands", "Netherlands") is True
    assert matches_country("nether", "Netherlands") is True
    assert matches_country("Slovenia", "Slovenia") is True
    assert matches_country("taiwan", "Taiwan (ROC)") is True


def test_fetch_dataverse_installations_filtering():
    from dartfx.dataverse.dataverse import fetch_dataverse_installations

    # Country filter
    nl_servers = fetch_dataverse_installations(country="NL")
    assert len(nl_servers) > 0
    for s in nl_servers:
        assert s.country_code == "NL"

    # Specific known target server filter
    harvard_list = fetch_dataverse_installations(target_server="dataverse.harvard.edu")
    assert len(harvard_list) == 1
    assert harvard_list[0].clean_hostname == "dataverse.harvard.edu"
    assert harvard_list[0].country_code == "US"

    # Unlisted fallback
    fallback_list = fetch_dataverse_installations(target_server="private.dataverse.internal", fallback_unlisted=True)
    assert len(fallback_list) == 1
    assert fallback_list[0].clean_hostname == "private.dataverse.internal"
    assert fallback_list[0].country_code == "-"


def test_cli_installations_command(monkeypatch):
    import json

    from typer.testing import CliRunner

    from dartfx.dataverse.cli import app
    from dartfx.dataverse.dataverse import ServerInstallation

    mock_insts = [
        ServerInstallation(name="Test NL 1", hostname="test1.nl", country="Netherlands", launch_year="2020"),
        ServerInstallation(name="Test NL 2", hostname="test2.nl", country="Netherlands", launch_year="2021"),
    ]
    monkeypatch.setattr("dartfx.dataverse.cli.fetch_dataverse_installations", lambda **_kwargs: mock_insts)

    runner = CliRunner()
    result = runner.invoke(app, ["installations", "--country", "NL", "--limit", "3", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert len(data) == 2
    assert all(d.get("country_code") == "NL" for d in data)

    result_csv = runner.invoke(app, ["installations", "--country", "NL", "--limit", "3", "--format", "csv"])
    assert result_csv.exit_code == 0
    assert "country_code" in result_csv.stdout
    assert "NL" in result_csv.stdout


def test_cli_smart_dash_normalization(monkeypatch):
    import sys

    from dartfx.dataverse.cli import _normalize_smart_dashes

    monkeypatch.setattr(sys, "argv", ["dartfx-dataverse", "stats", "-–country", "CA", "—limit", "5"])
    _normalize_smart_dashes()
    assert sys.argv == ["dartfx-dataverse", "stats", "--country", "CA", "--limit", "5"]


def test_cli_stats_command_flags():
    from typer.testing import CliRunner

    from dartfx.dataverse.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["stats", "--help"])
    assert result.exit_code == 0
    assert "--refresh" in result.stdout
    assert "-r" in result.stdout
    assert "--cache-ttl" in result.stdout
