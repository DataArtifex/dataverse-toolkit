from dartfx.dataverse.harvester import (
    ServerHarvester,
    get_dataset_metadata_path,
    is_non_recoverable_error,
    normalize_doi,
    normalize_formats,
    resolve_server_token,
    sanitize_pid,
    save_server_token,
)


def test_normalize_doi():
    assert normalize_doi("doi:10.1234/test") == "doi:10.1234/test"
    assert normalize_doi("doi_10.1234_test") == "doi:10.1234/test"
    assert normalize_doi("10.1234/test") == "doi:10.1234/test"
    assert normalize_doi("hdl:10.1234/test") == "hdl:10.1234/test"


def test_normalize_formats():
    assert normalize_formats("croissant") == ["croissant"]
    assert normalize_formats("croissant,native,ddi") == ["croissant", "native", "ddi"]
    assert normalize_formats("all") == ["croissant", "native", "ddi", "schema.org", "datacite"]
    assert normalize_formats("schemaorg") == ["schema.org"]
    assert normalize_formats(None) == []


def test_sanitize_pid():
    assert sanitize_pid("doi:10.5683/SP3/TEST") == "doi_10.5683_SP3_TEST"


def test_get_dataset_metadata_path(tmp_path):
    server_dir = tmp_path / "dataverse.test"
    meta_path, rel_path = get_dataset_metadata_path(server_dir, "doi:10.1234/foo", ".croissant.json")
    assert rel_path == "doi_10.1234_foo/metadata/croissant.json"
    assert meta_path == server_dir / "doi_10.1234_foo" / "metadata" / "croissant.json"


def test_is_non_recoverable_error():
    assert is_non_recoverable_error("Croissant exception: validation failed") is True
    assert is_non_recoverable_error("HTTP 404") is True
    assert is_non_recoverable_error("HTTP 400") is True
    assert is_non_recoverable_error("HTTP 500") is False
    assert is_non_recoverable_error("Connection timed out") is False


def test_token_persistence_and_resolution(tmp_path, monkeypatch):
    test_host = "dataverse.unc.edu"

    # 1. No token initially
    assert resolve_server_token(test_host, repo_root=tmp_path) is None

    # 2. Save token
    save_server_token(test_host, "test-token-12345", repo_root=tmp_path)

    # 3. Resolve from server directory and central json
    assert resolve_server_token(test_host, repo_root=tmp_path) == "test-token-12345"

    # 4. Explicit token override
    assert resolve_server_token(test_host, repo_root=tmp_path, explicit_token="override-token") == "override-token"

    # 5. Environment variable resolution
    monkeypatch.setenv("DATAVERSE_API_TOKEN_DATAVERSE_UNC_EDU", "env-token-xyz")
    # Without repo_root pointing to saved files, env var is used
    assert resolve_server_token(test_host, repo_root=tmp_path / "empty") == "env-token-xyz"


def test_server_harvester_manifest(tmp_path):
    harvester = ServerHarvester("test.dataverse.org", tmp_path)
    assert harvester.manifest_file.exists() is False

    # Save dummy record
    harvester.manifest["records"]["doi:10.1/test::croissant"] = {
        "global_id": "doi:10.1/test",
        "format": "croissant",
        "sha256": "abcd1234efgh",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    harvester._save_manifest()

    # Reload and verify
    reloaded = ServerHarvester("test.dataverse.org", tmp_path)
    assert "doi:10.1/test::croissant" in reloaded.manifest["records"]


def test_token_resolution_with_repository_env(tmp_path, monkeypatch):
    test_host = "dataverse.unc.edu"
    monkeypatch.setenv("DARTFX_DATAVERSE_REPOSITORY", str(tmp_path))
    save_server_token(test_host, "saved-token-999", repo_root=tmp_path)
    # resolve without passing repo_root explicitly
    assert resolve_server_token(test_host) == "saved-token-999"


def test_fetch_server_stats_caching(tmp_path):
    import json

    from dartfx.dataverse.harvester import fetch_server_stats

    # Create dummy cache file
    server = "cached.dataverse.org"
    server_dir = tmp_path / server
    server_dir.mkdir(parents=True)
    cache_file = server_dir / ".stats_cache.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "server": server,
                "cached_at": "2026-08-20T00:00:00Z",
                "query": "*",
                "datasets": 100,
                "files": 500,
                "tabular_files": 50,
                "is_dataverse": True,
                "version": "6.10",
                "error": None,
            },
            f,
        )

    # Fetch with repo_root pointing to tmp_path
    res = fetch_server_stats(server, repo_root=tmp_path, cache_ttl_hours=100.0)
    assert res.get("cached") is True
    assert res.get("datasets") == 100
    assert res.get("version") == "6.10"


def test_limit_normalization():
    from dartfx.dataverse.harvester import fetch_active_datasets

    # Test caching behavior with limit=0 (unlimited)
    res_0 = fetch_active_datasets("mock.host", limit=0, cache_ttl_hours=0.0)
    assert isinstance(res_0, dict)

    res_100 = fetch_active_datasets("mock.host", limit=100, cache_ttl_hours=0.0)
    assert isinstance(res_100, dict)


def test_is_format_unsupported_error():
    from dartfx.dataverse.harvester import is_format_unsupported_error

    assert is_format_unsupported_error("Croissant export not supported on server (HTTP 404)") is True
    assert is_format_unsupported_error("pyDataverse Croissant module not found") is True
    assert is_format_unsupported_error("Unsupported format") is True
    assert is_format_unsupported_error("Connection timeout") is False
    assert is_format_unsupported_error(None) is False


def test_tabular_default():
    # Test that default tabular_only is True
    import inspect

    from dartfx.dataverse.harvester import fetch_active_datasets

    sig = inspect.signature(fetch_active_datasets)
    assert sig.parameters["tabular_only"].default is True


def test_classify_harvest_error():
    from dartfx.dataverse.harvester import classify_harvest_error

    # 1. Croissant checksum error
    assert (
        classify_harvest_error("Croissant exception: FileObject(foo.zip) defined: ['md5', 'sha256']")
        == "Croissant Validation: Missing Checksum (md5/sha256)"
    )
    # 2. Croissant schema/mandatory error
    assert (
        classify_harvest_error("Croissant exception: Mandatory property missing")
        == "Croissant Validation: Missing Mandatory Field"
    )
    assert (
        classify_harvest_error("pyDataverse Croissant exception: schema error")
        == "Croissant Validation: Schema Incompatibility"
    )

    # 3. Exporter unsupported
    assert classify_harvest_error("Exporter not found on server") == "Exporter Not Supported on Server"

    # 4. HTTP status codes
    assert classify_harvest_error("HTTP 401: Unauthorized") == "HTTP 401: Authentication Required (API Token)"
    assert classify_harvest_error("HTTP 403: Cloudflare Challenge") == "HTTP 403: Forbidden / Bot Protection (WAF)"
    assert classify_harvest_error("HTTP 404: Not Found") == "HTTP 404: Dataset / Exporter Not Found"
    assert classify_harvest_error("HTTP 422: Unprocessable Entity") == "HTTP 422: Unprocessable Entity"
    assert classify_harvest_error("HTTP 500: Internal Server Error") == "HTTP 5xx: Server / Upstream Error"

    # 5. Network errors
    assert classify_harvest_error("Connection timed out (ReadTimeout)") == "Network: Request Timeout"
    assert (
        classify_harvest_error("Failed to establish a new connection: Connection refused")
        == "Network: Connection Failure"
    )
    assert classify_harvest_error("SSL: CERTIFICATE_VERIFY_FAILED") == "Network: SSL / TLS Certificate Error"

    # 6. Parse errors
    assert (
        classify_harvest_error("xml.etree.ElementTree.ParseError: syntax error") == "Parse Error: Malformed XML / JSON"
    )
    assert (
        classify_harvest_error("json.decoder.JSONDecodeError: Expecting value") == "Parse Error: Malformed XML / JSON"
    )

    # 7. Fallbacks
    assert classify_harvest_error("Some arbitrary error") == "Other Error"
    assert classify_harvest_error(None) == "Unknown Error"


def test_analyze_harvest_errors_empty(tmp_path):
    from dartfx.dataverse.harvester import analyze_harvest_errors

    res = analyze_harvest_errors(tmp_path)
    assert res["total_errors"] == 0
    assert res["total_datasets"] == 0
    assert res["by_type"] == {}
    assert res["records"] == []


def test_analyze_harvest_errors_aggregation(tmp_path):
    import json

    from dartfx.dataverse.harvester import analyze_harvest_errors

    # Setup 2 server directories with .manifest.json files
    srv1_dir = tmp_path / "dataverse.nl"
    srv1_dir.mkdir()
    srv1_manifest = {
        "server": "dataverse.nl",
        "records": {},
        "errors": {
            "doi:10.34894/AAA::croissant": {
                "global_id": "doi:10.34894/AAA",
                "format": "croissant",
                "reason": "Croissant exception: FileObject(data.csv) ['md5', 'sha256'] missing",
                "failed_at": "2026-08-20T10:00:00Z",
                "non_recoverable": True,
            },
            "doi:10.34894/BBB::croissant": {
                "global_id": "doi:10.34894/BBB",
                "format": "croissant",
                "reason": "Croissant exception: FileObject(doc.pdf) ['md5', 'sha256'] missing",
                "failed_at": "2026-08-20T10:05:00Z",
                "non_recoverable": True,
            },
            "doi:10.34894/AAA::native": {
                "global_id": "doi:10.34894/AAA",
                "format": "native",
                "reason": "HTTP 404: Not found",
                "failed_at": "2026-08-20T10:10:00Z",
                "non_recoverable": True,
            },
        },
    }
    with open(srv1_dir / ".manifest.json", "w") as f:
        json.dump(srv1_manifest, f)

    srv2_dir = tmp_path / "dataverse.harvard.edu"
    srv2_dir.mkdir()
    srv2_manifest = {
        "server": "dataverse.harvard.edu",
        "records": {},
        "errors": {
            "doi:10.7910/DVN/123::ddi": {
                "global_id": "doi:10.7910/DVN/123",
                "format": "ddi",
                "reason": "HTTP 500: Internal Server Error",
                "failed_at": "2026-08-20T11:00:00Z",
                "non_recoverable": False,
            },
        },
    }
    with open(srv2_dir / ".manifest.json", "w") as f:
        json.dump(srv2_manifest, f)

    # Analyze all servers
    all_res = analyze_harvest_errors(tmp_path)
    assert all_res["total_errors"] == 4
    assert all_res["total_datasets"] == 3  # doi:.../AAA, BBB, 123
    assert all_res["servers_with_errors"] == 2
    assert all_res["by_type"]["Croissant Validation: Missing Checksum (md5/sha256)"] == 2
    assert all_res["by_type"]["HTTP 404: Dataset / Exporter Not Found"] == 1
    assert all_res["by_type"]["HTTP 5xx: Server / Upstream Error"] == 1
    assert all_res["by_format"]["croissant"] == 2
    assert all_res["by_format"]["native"] == 1
    assert all_res["by_format"]["ddi"] == 1
    assert all_res["by_server"]["dataverse.nl"] == 3
    assert all_res["by_server"]["dataverse.harvard.edu"] == 1

    # Filter by specific server
    nl_res = analyze_harvest_errors(tmp_path, server="dataverse.nl")
    assert nl_res["total_errors"] == 3
    assert nl_res["total_datasets"] == 2
    assert nl_res["servers_with_errors"] == 1


def test_cli_errors_command(tmp_path):
    import json

    from typer.testing import CliRunner

    from dartfx.dataverse.cli import app

    srv_dir = tmp_path / "dataverse.test"
    srv_dir.mkdir()
    manifest = {
        "server": "dataverse.test",
        "records": {},
        "errors": {
            "doi:10.1/A::croissant": {
                "global_id": "doi:10.1/A",
                "format": "croissant",
                "reason": "Croissant exception: missing md5",
                "failed_at": "2026-08-20T10:00:00Z",
                "non_recoverable": True,
            }
        },
    }
    with open(srv_dir / ".manifest.json", "w") as f:
        json.dump(manifest, f)

    runner = CliRunner()

    # Test Table Output
    res = runner.invoke(app, ["errors", str(tmp_path)])
    assert res.exit_code == 0
    assert "Harvest Error Analysis Summary" in res.stdout
    assert "Croissant Validation" in res.stdout

    # Test JSON Output
    res_json = runner.invoke(app, ["errors", str(tmp_path), "--format", "json"])
    assert res_json.exit_code == 0
    parsed = json.loads(res_json.stdout)
    assert parsed["total_errors"] == 1

    # Test CSV Output
    res_csv = runner.invoke(app, ["errors", str(tmp_path), "--format", "csv"])
    assert res_csv.exit_code == 0
    assert "error_type,count,percentage" in res_csv.stdout

    # Test breakdown flags
    res_fmt = runner.invoke(app, ["errors", str(tmp_path), "--by-format"])
    assert res_fmt.exit_code == 0

    res_srv = runner.invoke(app, ["errors", str(tmp_path), "--by-server"])
    assert res_srv.exit_code == 0

    res_det = runner.invoke(app, ["errors", str(tmp_path), "--details"])
    assert res_det.exit_code == 0
    assert "doi:10.1/A" in res_det.stdout
