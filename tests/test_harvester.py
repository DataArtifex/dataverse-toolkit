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
