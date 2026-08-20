#!/usr/bin/env python3
"""
Croissant Metadata Harvester & Sync Engine

A smart, incremental harvester for Dataverse Croissant ML and standard metadata records.
Uses Typer for CLI interface and Rich for terminal visualizations.
"""

import hashlib
import json
import os
import re
import time
import urllib.parse
import warnings
import xml.etree.ElementTree as ET
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any

import requests
import typer
from dotenv import find_dotenv, load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

try:
    from pyDataverse.Croissant import Croissant
except ImportError:
    try:
        from pyDataverse import Croissant
    except ImportError:
        Croissant = None

os.environ["PYTHONWARNINGS"] = "ignore"
warnings.filterwarnings("ignore")


app = typer.Typer(
    name="croissant-harvest",
    help="Harvest and incrementally sync Dataverse Croissant ML records into local storage.",
    add_completion=False,
)

load_dotenv(find_dotenv(usecwd=True))

console = Console()


class HarvesterFileLogger:
    """File logger for recording execution requests and verbose activity to a timestamped log file."""

    def __init__(self, log_path: Path | None = None):
        self.log_path = log_path
        if self.log_path:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        try:
            plain_msg = Text.from_markup(message).plain
        except Exception:
            plain_msg = message

        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"{timestamp} [{level}] {plain_msg}"

        if self.log_path:
            try:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(formatted + "\n")
            except Exception:
                pass


file_logger = HarvesterFileLogger()

DATAVERSES_DIRECTORY_URLS = [
    "https://raw.githubusercontent.com/IQSS/dataverse-installations/refs/heads/main/data/data.json",
]


def sanitize_pid(identifier: str) -> str:
    """Convert DOI or Handle PID to safe directory name."""
    return re.sub(r"[^a-zA-Z0-9_\-\.]", "_", identifier)


def get_dataset_metadata_path(server_dir: Path, pid: str, ext: str = ".croissant.json") -> tuple[Path, str]:
    """
    Get dataset directory and metadata file path inside a dedicated metadata/ folder.
    Returns (full_file_path, relative_path_str).
    """
    pid_dir_name = sanitize_pid(pid)
    metadata_dir = server_dir / pid_dir_name / "metadata"
    file_name = ext.lstrip(".")
    rel_path = f"{pid_dir_name}/metadata/{file_name}"
    return metadata_dir / file_name, rel_path


FORMAT_EXTENSIONS: dict[str, str] = {
    "croissant": ".croissant.json",
    "native": ".dataverse.json",
    "ddi": ".ddi-c.xml",
    "schema.org": ".schema.json",
    "schemaorg": ".schema.json",
    "datacite": ".datacite.xml",
}


def get_format_extension(fmt: str) -> str:
    """Return static file extension for a given metadata format."""
    return FORMAT_EXTENSIONS.get(fmt.strip().lower(), f".{fmt.strip().lower()}.json")


DEFAULT_REQUEST_HEADERS: dict[str, str] = {
    "User-Agent": "dartfx-dataverse/0.1.0 (Research Harvester; +https://github.com/DataArtifex/dataverse-toolkit)",
    "Accept": "application/json, text/plain, */*",
}


def resolve_server_token(
    host: str | None = None,
    repo_root: Path | None = None,
    explicit_token: str | None = None,
) -> str | None:
    """
    Resolve API token for a Dataverse server by searching in order:
    1. Explicitly supplied CLI token (--api-token / -k)
    2. Server-specific directory token file (<repo_root>/<host>/.api_token or ./<host>/.api_token)
    3. Central repository root tokens mapping (<repo_root>/.dataverse_tokens.json)
    4. Current working directory tokens (.dataverse_tokens.json or .tokens.json)
    5. Server-specific environment variable (e.g. DATAVERSE_API_TOKEN_DATAVERSE_UNC_EDU)
    6. Global environment variable (DATAVERSE_API_TOKEN or DATAVERSE_KEY)
    """
    if explicit_token and explicit_token.strip():
        return explicit_token.strip()

    if not host:
        return os.environ.get("DATAVERSE_API_TOKEN") or os.environ.get("DATAVERSE_KEY")

    clean_host = host.replace("https://", "").replace("http://", "").strip("/")

    # 1. Check server-specific directory (.api_token)
    search_dirs = []
    if repo_root:
        search_dirs.append(repo_root)
    env_repo = os.environ.get("DARTFX_DATAVERSE_REPOSITORY")
    if env_repo:
        search_dirs.append(Path(env_repo))
    search_dirs.append(Path.cwd())
    for d in search_dirs:
        if d:
            stf = Path(d) / clean_host / ".api_token"
            if stf.exists():
                try:
                    t = stf.read_text("utf-8").strip()
                    if t:
                        return t
                except Exception:
                    pass

    # 2. Check central .dataverse_tokens.json / .tokens.json
    for d in search_dirs:
        if d:
            for token_filename in [".dataverse_tokens.json", ".tokens.json"]:
                ctf = Path(d) / token_filename
                if ctf.exists():
                    try:
                        m = json.loads(ctf.read_text("utf-8"))
                        if isinstance(m, dict):
                            for k, v in m.items():
                                k_clean = k.replace("https://", "").replace("http://", "").strip("/")
                                if k_clean.lower() == clean_host.lower() and v:
                                    return str(v).strip()
                    except Exception:
                        pass

    # 3. Server-specific environment variable (e.g. DATAVERSE_API_TOKEN_DATAVERSE_UNC_EDU)
    clean_env_name = re.sub(r"[^A-Za-z0-9]", "_", clean_host).upper()
    env_server_key = f"DATAVERSE_API_TOKEN_{clean_env_name}"
    if os.environ.get(env_server_key):
        return os.environ[env_server_key].strip()

    # 4. Global environment variable
    if os.environ.get("DATAVERSE_API_TOKEN"):
        return os.environ["DATAVERSE_API_TOKEN"].strip()
    if os.environ.get("DATAVERSE_KEY"):
        return os.environ["DATAVERSE_KEY"].strip()

    return None


def save_server_token(host: str, token: str, repo_root: Path | None = None) -> None:
    """Save an API token for a server to both its server directory (.api_token) and central .dataverse_tokens.json."""
    clean_host = host.replace("https://", "").replace("http://", "").strip("/")
    clean_token = token.strip()
    if not clean_token:
        return

    # 1. Save to central .dataverse_tokens.json in repo_root (or current dir)
    central_dir = repo_root if repo_root else Path.cwd()
    central_file = central_dir / ".dataverse_tokens.json"
    tokens_map = {}
    if central_file.exists():
        try:
            tokens_map = json.loads(central_file.read_text("utf-8"))
        except Exception:
            tokens_map = {}
    tokens_map[clean_host] = clean_token
    try:
        central_file.write_text(json.dumps(tokens_map, indent=2) + "\n", encoding="utf-8")
    except Exception:
        pass

    # 2. Save to server-specific directory (.api_token)
    if repo_root:
        server_dir = repo_root / clean_host
        server_dir.mkdir(parents=True, exist_ok=True)
        token_file = server_dir / ".api_token"
        try:
            token_file.write_text(clean_token + "\n", encoding="utf-8")
        except Exception:
            pass


def get_request_headers(
    host: str | None = None,
    api_token: str | None = None,
    repo_root: Path | None = None,
) -> dict[str, str]:
    """Return standard headers with browser User-Agent and resolved Dataverse API key."""
    headers = dict(DEFAULT_REQUEST_HEADERS)
    resolved_token = resolve_server_token(host, repo_root=repo_root, explicit_token=api_token)
    if resolved_token:
        headers["X-Dataverse-key"] = resolved_token.strip()
    return headers


def parse_date_to_iso(date_str: str) -> str:
    """Convert various date formats (YYYY-MM-DD, 7d, 30d) into ISO format or Solr format."""
    date_str = date_str.strip().lower()
    now = datetime.now(UTC)

    if date_str.endswith("d") and date_str[:-1].isdigit():
        days = int(date_str[:-1])
        start_date = now - timedelta(days=days)
        return start_date.strftime("%Y-%m-%d")

    # If YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return date_str

    # If already full ISO
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return date_str


# Raw Country Name to ISO 3166-1 Alpha-2 Code Crosswalk (Alphabetical)
COUNTRY_TO_ISO2: dict[str, str] = {
    "ARGENTINA": "AR",
    "AUSTRALIA": "AU",
    "AUSTRIA": "AT",
    "BELGIUM": "BE",
    "BRAZIL": "BR",
    "CANADA": "CA",
    "CHILE": "CL",
    "CHINA": "CN",
    "COLOMBIA": "CO",
    "COSTA RICA": "CR",
    "CZECH REPUBLIC": "CZ",
    "CZECHIA": "CZ",
    "DENMARK": "DK",
    "DEUTSCHLAND": "DE",
    "ESTONIA": "EE",
    "FINLAND": "FI",
    "FRANCE": "FR",
    "GERMANY": "DE",
    "GREAT BRITAIN": "GB",
    "GREECE": "GR",
    "HOLLAND": "NL",
    "HUNGARY": "HU",
    "INDIA": "IN",
    "INDONESIA": "ID",
    "IRELAND": "IE",
    "ITALY": "IT",
    "JAPAN": "JP",
    "KENYA": "KE",
    "KOREA": "KR",
    "LATVIA": "LV",
    "LEBANON": "LB",
    "LITHUANIA": "LT",
    "MALAYSIA": "MY",
    "MEXICO": "MX",
    "NETHERLANDS": "NL",
    "NORWAY": "NO",
    "PERU": "PE",
    "POLAND": "PL",
    "PORTUGAL": "PT",
    "RUSSIA": "RU",
    "SINGAPORE": "SG",
    "SLOVAKIA": "SK",
    "SOUTH AFRICA": "ZA",
    "SOUTH KOREA": "KR",
    "SPAIN": "ES",
    "SWEDEN": "SE",
    "SWITZERLAND": "CH",
    "TURKEY": "TR",
    "TÜRKIYE": "TR",
    "UK": "GB",
    "UNITED KINGDOM": "GB",
    "UNITED STATES": "US",
    "UNITED STATES OF AMERICA": "US",
    "USA": "US",
}


def get_iso2_code(raw_country: str, existing_code: str = "") -> str:
    """Resolve raw country string to 2-letter ISO 3166-1 Alpha-2 code."""
    if existing_code and len(existing_code.strip()) == 2:
        return existing_code.strip().upper()

    clean_country = raw_country.strip().upper()
    if clean_country in COUNTRY_TO_ISO2:
        return COUNTRY_TO_ISO2[clean_country]

    if len(clean_country) == 2:
        return clean_country

    return ""


def matches_country(target_filter: str, raw_country: str, existing_code: str = "") -> bool:
    """Check if user filter matches 2-letter ISO country code or raw country name."""
    tf = target_filter.strip().upper()
    server_iso2 = get_iso2_code(raw_country, existing_code)

    # 1. If target filter is a 2-letter code, strictly match server ISO2 code only (do not substring match names)
    if len(tf) == 2:
        return tf == server_iso2

    # 2. Compare target filter resolved ISO2 vs server ISO2
    filter_iso2 = COUNTRY_TO_ISO2.get(tf)
    if filter_iso2 and server_iso2 and filter_iso2 == server_iso2:
        return True

    # 3. Fallback substring matching on raw country string ONLY for filters longer than 2 characters
    tf_low = target_filter.strip().lower()
    if len(tf_low) > 2 and tf_low in raw_country.lower():
        return True

    return False


def fetch_raw_installations() -> list[dict]:
    """Fetch raw installations list from remote registry endpoints."""
    for url in DATAVERSES_DIRECTORY_URLS:
        if not url:
            continue
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if "installations" in data:
                    return data["installations"]
                elif isinstance(data, list):
                    return data
        except Exception:
            continue
    return []


def get_global_installations(
    target_server: str | None = None, country_filter: str | None = None
) -> list[dict[str, str]]:
    """Fetch global Dataverse installations registry and apply server/country filters."""
    console.print("[bold blue]Fetching global Dataverse installations registry...[/bold blue]")
    installations = fetch_raw_installations()

    clean_target = (
        target_server.replace("https://", "").replace("http://", "").strip("/")
        if target_server and target_server.upper() != "ALL"
        else None
    )

    filtered = []
    for inst in installations:
        if isinstance(inst, dict):
            hostname = inst.get("hostname") or inst.get("host") or inst.get("url", "")
            hostname = hostname.replace("https://", "").replace("http://", "").strip("/")
            if not hostname:
                continue

            # If explicit target server specified, match hostname!
            if clean_target and hostname.lower() != clean_target.lower():
                continue

            raw_country = (inst.get("country") or "").strip()
            raw_code = (inst.get("country_code") or "").strip()
            name = (inst.get("name") or "").strip()

            iso2_code = get_iso2_code(raw_country, raw_code)

            # Filter by country if specified using 2-letter ISO crosswalk
            if country_filter:
                if not matches_country(country_filter, raw_country, raw_code):
                    continue

            filtered.append(
                {
                    "hostname": hostname,
                    "name": name,
                    "country": raw_country or "Global",
                    "country_code": iso2_code or "-",
                }
            )

    # Fallback if target server was not found in registry
    if clean_target and not filtered:
        iso2 = get_iso2_code(country_filter or "")
        filtered.append(
            {
                "hostname": clean_target,
                "name": clean_target,
                "country": country_filter or "Global",
                "country_code": iso2 or "-",
            }
        )

    return filtered


def normalize_doi(doi_str: str) -> str:
    """Normalize DOI input, converting directory-style underscores back to slashes if needed."""
    raw = doi_str.strip()
    if raw.lower().startswith("doi_"):
        raw = "doi:" + raw[4:]
    elif not raw.lower().startswith("doi:") and not raw.lower().startswith("hdl:"):
        raw = "doi:" + raw

    # Replace directory-style underscores after 10.xxxx with slashes
    if "10." in raw and "_" in raw:
        prefix, rest = raw.split("10.", 1)
        raw = f"{prefix}10.{rest.replace('_', '/')}"

    return raw


def is_format_unsupported_error(err_msg: str | None) -> bool:
    """Determine if an error indicates that a metadata format exporter is completely unavailable."""
    if not err_msg:
        return False
    msg_low = err_msg.lower()
    return any(
        k in msg_low
        for k in (
            "not supported",
            "module not found",
            "exporter not found",
            "unsupported format",
            "http 404",
        )
    )


def is_non_recoverable_error(err_msg: str | None) -> bool:
    """Determine if an error is non-recoverable (format validation failure, 404, 400, 422, unsupported format)."""
    if not err_msg:
        return False
    msg_low = err_msg.lower()

    # Format validation errors (pyDataverse Croissant exceptions, XML/JSON parse errors)
    if any(
        k in msg_low for k in ["croissant exception", "validation", "mandatory", "parseerror", "unsupported format"]
    ):
        return True

    # Deterministic HTTP response codes
    if any(code in msg_low for code in ["http 404", "http 400", "http 422", "http 403"]):
        return True

    return False


def find_registry_suggestions(target: str, raw_installations: list[dict]) -> list[dict[str, str]]:
    """Find close matches or substring suggestions in the installations registry."""
    clean = target.lower().replace("https://", "").replace("http://", "").strip("/")
    suggestions = []

    # Extract distinct non-generic keywords from target (skip 'dataverse', 'data', 'datasets', 'lib', 'library')
    generic_words = {
        "dataverse",
        "data",
        "dataset",
        "datasets",
        "lib",
        "library",
        "open",
        "repo",
        "repository",
        "org",
        "edu",
        "gov",
        "com",
        "net",
        "nl",
        "ca",
        "us",
        "fr",
        "de",
    }
    parts = [p for p in re.split(r"[^a-z0-9]", clean) if len(p) >= 3 and p not in generic_words]
    root_name = parts[0] if parts else ""

    for inst in raw_installations:
        if isinstance(inst, dict):
            host = (
                (inst.get("hostname") or inst.get("host") or inst.get("url", ""))
                .lower()
                .replace("https://", "")
                .replace("http://", "")
                .strip("/")
            )
            name = (inst.get("name") or "").lower()
            if not host:
                continue
            matches = False
            if root_name and (root_name in host or root_name in name):
                matches = True
            elif len(clean) >= 5 and (clean in host or host in clean):
                matches = True

            if matches:
                entry = {
                    "hostname": host,
                    "name": inst.get("name", ""),
                    "country": inst.get("country", "") or "Global",
                }
                if entry not in suggestions:
                    suggestions.append(entry)
    return suggestions


def fetch_server_stats(
    host: str,
    query: str | None = None,
    api_token: str | None = None,
    timeout: int = 15,
    repo_root: Path | None = None,
    refresh_cache: bool = False,
    cache_ttl_hours: float = 24.0,
) -> dict[str, int | bool | str | None]:
    """Retrieve counts of datasets, total files, and tabular data files from a Dataverse server."""
    clean_host = host.replace("https://", "").replace("http://", "").strip("/")
    base_url = f"https://{host}" if not host.startswith("http") else host
    solr_query = query if query else "*"
    encoded_query = urllib.parse.quote(solr_query)
    headers = get_request_headers(host=host, api_token=api_token, repo_root=repo_root)

    target_repo = repo_root
    if not target_repo:
        env_repo = os.environ.get("DARTFX_DATAVERSE_REPOSITORY")
        if env_repo:
            target_repo = Path(env_repo)
        else:
            target_repo = Path.cwd() / ".cache"

    cache_file = (target_repo / clean_host / ".stats_cache.json") if target_repo else None

    # Check 24h local cache
    if cache_file and cache_file.exists() and not refresh_cache:
        try:
            with open(cache_file, encoding="utf-8") as f:
                cdata = json.load(f)
                cached_at_str = cdata.get("cached_at")
                if cached_at_str and cdata.get("query") == solr_query:
                    dt = datetime.fromisoformat(cached_at_str)
                    age_hours = (datetime.now(UTC) - dt).total_seconds() / 3600.0
                    if age_hours < cache_ttl_hours and (cdata.get("is_dataverse") or cdata.get("requires_token")):
                        cdata["cached"] = True
                        return cdata
        except Exception:
            pass

    stats: dict[str, int | bool | str | None] = {
        "datasets": 0,
        "files": 0,
        "tabular_files": 0,
        "is_dataverse": False,
        "requires_token": False,
        "error": None,
        "version": None,
    }

    try:
        r_ds = requests.get(
            f"{base_url}/api/search?q={encoded_query}&type=dataset&per_page=1",
            headers=headers,
            timeout=timeout,
        )
        if r_ds.status_code == 200:
            try:
                data = r_ds.json()
                if isinstance(data, dict) and data.get("status") == "OK" and "data" in data:
                    stats["is_dataverse"] = True
                    stats["datasets"] = data.get("data", {}).get("total_count", 0)
                    try:
                        r_ver = requests.get(f"{base_url}/api/info/version", headers=headers, timeout=min(timeout, 5))
                        if r_ver.status_code == 200:
                            vdata = r_ver.json()
                            if isinstance(vdata, dict) and vdata.get("status") == "OK":
                                stats["version"] = vdata.get("data", {}).get("version")
                    except Exception:
                        pass
                else:
                    stats["error"] = "Not a Dataverse server (invalid API response)"
                    return stats
            except Exception:
                text_low = r_ds.text.lower()
                if (
                    "security check" in text_low
                    or "not a bot" in text_low
                    or "cloudflare" in text_low
                    or "challenge" in text_low
                ):
                    stats["error"] = "WAF / Bot Protection Interstitial"
                else:
                    stats["error"] = "Not a Dataverse server (HTML response)"
                return stats
        elif r_ds.status_code == 401:
            # Check /api/info/version to verify if active Dataverse node with token requirement
            try:
                r_ver = requests.get(f"{base_url}/api/info/version", headers=headers, timeout=timeout)
                if r_ver.status_code == 200 and r_ver.json().get("status") == "OK":
                    stats["is_dataverse"] = True
                    stats["requires_token"] = True
                    ver = r_ver.json().get("data", {}).get("version", "")
                    stats["version"] = ver
                    stats["error"] = "Requires Token (pass -k/--api-token)"
                    return stats
            except Exception:
                pass
            stats["error"] = "HTTP 401 (Authentication Required)"
            return stats
        elif r_ds.status_code == 403:
            # Check if Dataverse version responds or Cloudflare WAF
            try:
                r_ver = requests.get(f"{base_url}/api/info/version", headers=headers, timeout=timeout)
                if r_ver.status_code == 200 and r_ver.json().get("status") == "OK":
                    stats["is_dataverse"] = True
                    stats["requires_token"] = True
                    ver = r_ver.json().get("data", {}).get("version", "")
                    stats["version"] = ver
                    stats["error"] = "Requires Token (pass -k/--api-token)"
                    return stats
            except Exception:
                pass
            if "just a moment" in r_ds.text.lower() or "cloudflare" in r_ds.text.lower():
                stats["error"] = "Cloudflare WAF / Bot Protection"
            else:
                stats["error"] = "HTTP 403 (Access Denied / WAF)"
            return stats
        elif r_ds.status_code == 202:
            stats["error"] = "AWS ELB / WAF (HTTP 202)"
            return stats
        elif r_ds.status_code in (404, 502, 503):
            stats["error"] = f"HTTP {r_ds.status_code} (Inactive / Not Found)"
            return stats
        else:
            stats["error"] = f"HTTP {r_ds.status_code}"
            return stats
    except requests.exceptions.SSLError:
        stats["error"] = "SSL / TLS Certificate Error"
        return stats
    except requests.exceptions.ConnectionError:
        stats["error"] = "Unreachable (DNS / Connection Failure)"
        return stats
    except requests.exceptions.Timeout:
        stats["error"] = "Connection Timed Out"
        return stats
    except Exception as e:
        stats["error"] = str(e)
        return stats

    try:
        r_files = requests.get(
            f"{base_url}/api/search?q={encoded_query}&type=file&per_page=1",
            headers=headers,
            timeout=timeout,
        )
        if r_files.status_code == 200:
            stats["files"] = r_files.json().get("data", {}).get("total_count", 0)
    except Exception:
        pass

    try:
        r_tab = requests.get(
            f"{base_url}/api/search?q={encoded_query}&type=file&fq=fileTypeGroupFacet:%22Tabular%20Data%22&per_page=1",
            headers=headers,
            timeout=timeout,
        )
        if r_tab.status_code == 200:
            stats["tabular_files"] = r_tab.json().get("data", {}).get("total_count", 0)
    except Exception:
        pass

    if cache_file and (stats.get("is_dataverse") or stats.get("requires_token")):
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            save_payload = dict(stats)
            save_payload["server"] = clean_host
            save_payload["query"] = solr_query
            save_payload["cached_at"] = datetime.now(UTC).isoformat()
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(save_payload, f, indent=2)
        except Exception:
            pass

    return stats


def fetch_active_datasets(
    host: str,
    query: str | None = None,
    since_date: str | None = None,
    limit: int | None = None,
    target_doi: str | None = None,
    server_dir: Path | None = None,
    refresh_catalog: bool = False,
    cache_ttl_hours: float = 24.0,
    per_page: int = 100,
    verbose: bool = False,
    tabular_only: bool = True,
    api_token: str | None = None,
) -> dict[str, dict]:
    """Search for active datasets using Search API or DOI target with local 24h catalog caching."""
    effective_limit = None if limit == 0 else limit
    base_url = f"https://{host}" if not host.startswith("http") else host
    headers = get_request_headers(host=host, api_token=api_token, repo_root=server_dir.parent if server_dir else None)

    # Check local catalog cache if server_dir is provided and refresh_catalog is False
    if server_dir and not refresh_catalog:
        cache_file = server_dir / ".catalog_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, encoding="utf-8") as f:
                    cache_data = json.load(f)

                cached_at_iso = cache_data.get("cached_at")
                cached_query = cache_data.get("query")
                cached_since = cache_data.get("since_date")
                cached_doi = cache_data.get("target_doi")
                cached_limit = cache_data.get("limit")
                cached_tabular = cache_data.get("tabular_only", False)
                cached_datasets = cache_data.get("datasets", {})

                if cached_at_iso:
                    cached_dt = datetime.fromisoformat(cached_at_iso)
                    now_dt = datetime.now(UTC)
                    age_hours = (now_dt - cached_dt).total_seconds() / 3600.0

                    criteria_matches = (
                        cached_query == query
                        and cached_since == since_date
                        and cached_doi == target_doi
                        and cached_tabular == tabular_only
                    )
                    limit_valid = (limit is not None and cached_limit is not None and cached_limit >= limit) or (
                        cached_limit is None
                    )

                    if age_hours < cache_ttl_hours and criteria_matches and limit_valid and cached_datasets:
                        result_datasets = {}
                        for pid, d_info in cached_datasets.items():
                            result_datasets[pid] = d_info
                            if effective_limit and len(result_datasets) >= effective_limit:
                                break

                        msg = (
                            f"[CACHE] Using cached catalog from {cache_file.name} ("
                            f"{len(result_datasets)} records, cached {age_hours:.1f}h ago, TTL {cache_ttl_hours}h)"
                        )
                        if verbose:
                            console.print(f"[bold cyan]  {msg}[/bold cyan]")
                        file_logger.log(msg, level="CACHE")
                        return result_datasets
            except Exception as e:
                file_logger.log(f"[CACHE] Could not read cache file {cache_file}: {e}", level="WARNING")

    active_datasets = {}

    if target_doi:
        clean_doi = normalize_doi(target_doi)
        solr_query = f'dsPersistentId:"{clean_doi}" OR "{clean_doi}" OR "{target_doi.strip()}"'
    else:
        solr_query = query if query else "*"

    if since_date and not target_doi:
        solr_date = parse_date_to_iso(since_date)
        solr_query += f" AND publicationDate:[{solr_date}T00:00:00Z TO NOW]"

    search_type = "file" if tabular_only else "dataset"
    fq_param = '&fq=fileTypeGroupFacet:"Tabular%20Data"' if tabular_only else ""

    start = 0
    while True:
        encoded_query = urllib.parse.quote(solr_query)
        url = f"{base_url}/api/search?q={encoded_query}&type={search_type}{fq_param}&per_page={per_page}&start={start}"
        if verbose:
            console.print(f"[dim]  [API] GET {url}[/dim]")
        file_logger.log(f"[API] GET {url}")

        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code != 200:
                msg = f"[API] Search API error HTTP {r.status_code}"
                if verbose:
                    console.print(f"[bold red]  {msg}[/bold red]")
                file_logger.log(msg, level="ERROR")
                break
            res = r.json().get("data", {})
            items = res.get("items", [])
            total_count = res.get("total_count", 0)

            if start == 0:
                target_type_str = "tabular files" if tabular_only else "datasets"
                match_info = f"Found {total_count:,} total matching {target_type_str} on {host}"
                if effective_limit:
                    match_info += f" (harvesting up to limit of {effective_limit:,} datasets)"
                console.print(f"  [dim cyan]• {match_info}[/dim cyan]")
                file_logger.log(f"[API] {match_info}")

            if not items:
                break

            for item in items:
                if tabular_only:
                    global_id = item.get("dataset_persistent_id")
                    item_name = item.get("dataset_name") or item.get("name")
                    updated_at = item.get("published_at") or item.get("updated_at")
                else:
                    global_id = item.get("global_id")
                    item_name = item.get("name")
                    updated_at = item.get("updated_at")

                if global_id and global_id not in active_datasets:
                    active_datasets[global_id] = {
                        "global_id": global_id,
                        "name": item_name,
                        "updated_at": updated_at,
                        "published_at": item.get("published_at"),
                    }
                    if effective_limit and len(active_datasets) >= effective_limit:
                        msg = f"[API] Reached record limit ({effective_limit})"
                        if verbose:
                            console.print(f"[dim]  {msg}[/dim]")
                        file_logger.log(msg)
                        break

            if effective_limit and len(active_datasets) >= effective_limit:
                break

            start += per_page
            if start >= total_count:
                break
        except Exception as e:
            msg = f"[API] Exception querying Search API: {e}"
            if verbose:
                console.print(f"[bold red]  {msg}[/bold red]")
            file_logger.log(msg, level="ERROR")
            break

    # Direct fallback if Search API didn't return items for an explicit DOI query
    if target_doi and not active_datasets:
        clean_doi = normalize_doi(target_doi)
        active_datasets[clean_doi] = {
            "global_id": clean_doi,
            "name": clean_doi,
            "updated_at": None,
            "published_at": None,
        }

    msg = f"[API] Active datasets retrieved: {len(active_datasets)}"
    if verbose:
        console.print(f"[dim]  {msg}[/dim]")
    file_logger.log(msg)

    # Save to server root catalog cache
    if server_dir and active_datasets:
        try:
            server_dir.mkdir(parents=True, exist_ok=True)
            cache_file = server_dir / ".catalog_cache.json"
            cache_content = {
                "cached_at": datetime.now(UTC).isoformat(),
                "server": host,
                "query": query,
                "since_date": since_date,
                "target_doi": target_doi,
                "limit": effective_limit,
                "tabular_only": tabular_only,
                "count": len(active_datasets),
                "datasets": active_datasets,
            }
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_content, f, indent=2)
            msg = f"[CACHE] Saved server dataset catalog cache to {cache_file.name} ({len(active_datasets)} records)"
            if verbose:
                console.print(f"[dim]  {msg}[/dim]")
            file_logger.log(msg, level="CACHE")
        except Exception as e:
            file_logger.log(f"[CACHE] Failed writing catalog cache to {cache_file}: {e}", level="WARNING")

    return active_datasets


ALL_SUPPORTED_FORMATS = ["croissant", "native", "ddi", "schema.org", "datacite"]


def normalize_formats(formats_input: str | list[str] | None) -> list[str]:
    """Parse comma-separated or list of metadata formats into a clean list."""
    if not formats_input:
        return []
    if isinstance(formats_input, str):
        raw_list = [formats_input]
    else:
        raw_list = list(formats_input)

    parsed = []
    for entry in raw_list:
        for fmt in entry.split(","):
            fmt_clean = fmt.strip().lower()
            if not fmt_clean:
                continue
            if fmt_clean == "all":
                return list(ALL_SUPPORTED_FORMATS)
            if fmt_clean == "schemaorg":
                fmt_clean = "schema.org"
            if fmt_clean in ALL_SUPPORTED_FORMATS and fmt_clean not in parsed:
                parsed.append(fmt_clean)
    return parsed


def fetch_metadata_record(
    host: str,
    pid: str,
    metadata_format: str = "croissant",
    verbose: bool = False,
    api_token: str | None = None,
) -> tuple[bytes | None, str, str | None]:
    """
    Fetch dataset metadata in the specified format.
    Returns (content_bytes, file_extension, error_reason).
    """
    base_host = f"https://{host}" if not host.startswith("http") else host
    fmt = metadata_format.strip().lower()
    headers = get_request_headers(host=host, api_token=api_token)

    if fmt == "croissant":
        if verbose:
            console.print(f"[dim]  [API] Fetching Croissant ML record for PID: {pid}[/dim]")
        url = f"{base_host}/api/datasets/export?exporter=croissant&persistentId={urllib.parse.quote(pid)}"
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 200:
                return r.content, ".croissant.json", None
            elif r.status_code in (400, 404) and Croissant is not None:
                croissant = Croissant(doi=pid, host=base_host)
                rec = croissant.get_record()
                if rec and "error" not in rec:
                    return json.dumps(rec, indent=2, ensure_ascii=False).encode("utf-8"), ".croissant.json", None
            err_msg = f"Croissant export not supported on server (HTTP {r.status_code})"
            return None, ".croissant.json", err_msg
        except Exception as e:
            if Croissant is not None:
                try:
                    croissant = Croissant(doi=pid, host=base_host)
                    rec = croissant.get_record()
                    if rec and "error" not in rec:
                        return json.dumps(rec, indent=2, ensure_ascii=False).encode("utf-8"), ".croissant.json", None
                except Exception:
                    pass
            return None, ".croissant.json", f"Croissant export error: {e}"

    elif fmt == "native":
        url = f"{base_host}/api/datasets/:persistentId/?persistentId={urllib.parse.quote(pid)}"
        if verbose:
            console.print(f"[dim]  [API] GET {url}[/dim]")
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 200:
                return r.content, ".dataverse.json", None
            else:
                err_msg = f"HTTP {r.status_code}"
                if verbose:
                    console.print(f"[bold red]  [API] {err_msg} for {url}[/bold red]")
                return None, ".dataverse.json", err_msg
        except Exception as e:
            err_msg = str(e)
            if verbose:
                console.print(f"[bold red]  [API] Exception for {url}: {e}[/bold red]")
            return None, ".dataverse.json", err_msg

    elif fmt == "ddi":
        url = f"{base_host}/api/datasets/export?exporter=ddi&persistentId={urllib.parse.quote(pid)}"
        if verbose:
            console.print(f"[dim]  [API] GET {url}[/dim]")
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 200:
                return r.content, ".ddi-c.xml", None
            else:
                err_msg = f"HTTP {r.status_code}"
                if verbose:
                    console.print(f"[bold red]  [API] {err_msg} for {url}[/bold red]")
                return None, ".ddi-c.xml", err_msg
        except Exception as e:
            err_msg = str(e)
            if verbose:
                console.print(f"[bold red]  [API] Exception for {url}: {e}[/bold red]")
            return None, ".ddi-c.xml", err_msg

    elif fmt in ("schema.org", "schemaorg"):
        url = f"{base_host}/api/datasets/export?exporter=schema.org&persistentId={urllib.parse.quote(pid)}"
        if verbose:
            console.print(f"[dim]  [API] GET {url}[/dim]")
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 200:
                return r.content, ".schema.json", None
            else:
                err_msg = f"HTTP {r.status_code}"
                if verbose:
                    console.print(f"[bold red]  [API] {err_msg} for {url}[/bold red]")
                return None, ".schema.json", err_msg
        except Exception as e:
            err_msg = str(e)
            if verbose:
                console.print(f"[bold red]  [API] Exception for {url}: {e}[/bold red]")
            return None, ".schema.json", err_msg

    elif fmt == "datacite":
        url = f"{base_host}/api/datasets/export?exporter=oai_datacite&persistentId={urllib.parse.quote(pid)}"
        if verbose:
            console.print(f"[dim]  [API] GET {url}[/dim]")
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 200:
                return r.content, ".datacite.xml", None
            else:
                err_msg = f"HTTP {r.status_code}"
                if verbose:
                    console.print(f"[bold red]  [API] {err_msg} for {url}[/bold red]")
                return None, ".datacite.xml", err_msg
        except Exception as e:
            err_msg = str(e)
            if verbose:
                console.print(f"[bold red]  [API] Exception for {url}: {e}[/bold red]")
            return None, ".datacite.xml", err_msg

    return None, ".croissant.json", "Unsupported format"


def fetch_oai_deletions(
    host: str,
    since_date: str | None = None,
    verbose: bool = False,
    api_token: str | None = None,
) -> set[str]:
    """Query Dataverse OAI-PMH endpoint to find deleted dataset PIDs."""
    deleted_pids = set()
    base_url = f"https://{host}" if not host.startswith("http") else host
    oai_url = f"{base_url}/oai?verb=ListRecords&metadataPrefix=oai_dc"
    headers = get_request_headers(api_token)

    if since_date:
        oai_url += f"&from={parse_date_to_iso(since_date)}"

    if verbose:
        console.print(f"[dim]  [OAI] GET {oai_url}[/dim]")

    try:
        r = requests.get(oai_url, headers=headers, timeout=20)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            # Namespace map for OAI-PMH
            ns = {"oai": "http://www.openarchives.org/OAI/2.0/"}
            for header in root.findall(".//oai:header", ns):
                status = header.attrib.get("status")
                if status == "deleted":
                    identifier = header.findtext("oai:identifier", namespaces=ns)
                    if identifier:
                        deleted_pids.add(identifier)
    except Exception as e:
        if verbose:
            console.print(f"[dim]  [OAI] OAI-PMH check skipped/failed: {e}[/dim]")

    if verbose and deleted_pids:
        console.print(f"[dim]  [OAI] Found {len(deleted_pids)} deletion tombstone(s)[/dim]")
    return deleted_pids


class ServerHarvester:
    """Manages harvesting, diff detection, and file persistence for a single Dataverse server."""

    def __init__(self, host: str, repo_root: Path):
        self.host = host.replace("https://", "").replace("http://", "").strip("/")
        self.server_dir = repo_root / self.host
        self.server_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.server_dir / ".manifest.json"
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict:
        if self.manifest_file.exists():
            try:
                with open(self.manifest_file, encoding="utf-8") as f:
                    data = json.load(f)
                    if "errors" not in data:
                        data["errors"] = {}
                    return data
            except Exception:
                pass
        return {
            "server": self.host,
            "last_synced_at": None,
            "records": {},
            "errors": {},
        }

    def _save_manifest(self):
        self.server_dir.mkdir(parents=True, exist_ok=True)
        self.manifest["last_synced_at"] = datetime.now(UTC).isoformat()
        with open(self.manifest_file, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, indent=2)

    def sync(
        self,
        query: str | None = None,
        since_date: str | None = None,
        dry_run: bool = False,
        limit: int | None = None,
        metadata_formats: str | list[str] = "croissant",
        verbose: bool = False,
        target_doi: str | None = None,
        refresh_catalog: bool = False,
        cache_ttl_hours: float = 24.0,
        retry_errors: bool = False,
        force_verify: bool = False,
        tabular_only: bool = True,
        api_token: str | None = None,
        progress_callback=None,
    ) -> dict[str, list[Any]]:
        """Perform intelligent incremental sync (Additions, Updates, Deletions)."""
        effective_limit = None if limit == 0 else limit
        stats: dict[str, list[Any]] = {"added": [], "updated": [], "deleted": [], "unchanged": [], "errors": []}
        target_formats = normalize_formats(metadata_formats)

        if verbose:
            console.print(f"[bold cyan]── Syncing Server: {self.host} ──[/bold cyan]")

        active_datasets = fetch_active_datasets(
            self.host,
            query=query,
            since_date=since_date,
            limit=effective_limit,
            target_doi=target_doi,
            server_dir=self.server_dir,
            refresh_catalog=refresh_catalog,
            cache_ttl_hours=cache_ttl_hours,
            verbose=verbose,
            tabular_only=tabular_only,
            api_token=api_token,
        )
        if not active_datasets and not target_doi:
            server_check = fetch_server_stats(self.host, api_token=api_token)
            if not server_check.get("is_dataverse"):
                err_msg = str(server_check.get("error") or "Unreachable or not a valid Dataverse server")
                stats["errors"].append(
                    {
                        "key": self.host,
                        "pid": self.host,
                        "format": "-",
                        "reason": err_msg,
                    }
                )
                msg = f"Host '{self.host}' is unreachable or not a valid Dataverse server: {err_msg}"
                console.print(f"  [bold red][!] {msg}[/bold red]")
                file_logger.log(msg, level="ERROR")
                return stats

        manifest_records = self.manifest.get("records", {})
        existing_keys = set(manifest_records.keys())
        current_active_pids = set(active_datasets.keys())

        # Determine Deletions (only if not targeting a single specific DOI):
        if not target_doi:
            for key in list(existing_keys):
                rec_info = manifest_records.get(key, {})
                pid = rec_info.get("global_id") or key.split("::")[0]
                if pid not in current_active_pids:
                    rel_path = rec_info.get("path") or rec_info.get("filename")
                    file_path = self.server_dir / rel_path if rel_path else None

                    stats["deleted"].append(key)
                    msg = f"DELETED: {key} -> removing {rel_path}"
                    if verbose:
                        console.print(f"  [bold red][-] {msg}[/bold red]")
                    file_logger.log(msg, level="DELETE")

                    if not dry_run:
                        if file_path and file_path.exists():
                            file_path.unlink()
                            # Clean up metadata directory if empty
                            metadata_dir = file_path.parent
                            if metadata_dir.exists() and not any(metadata_dir.iterdir()):
                                metadata_dir.rmdir()
                            # Clean up parent dataset directory if empty
                            dataset_dir = metadata_dir.parent
                            if (
                                dataset_dir.exists()
                                and dataset_dir != self.server_dir
                                and not any(dataset_dir.iterdir())
                            ):
                                dataset_dir.rmdir()

                        if key in self.manifest["records"]:
                            del self.manifest["records"][key]

        # Determine Additions and Updates across all requested formats:
        total_items = len(active_datasets) * len(target_formats)
        current_item = 0
        unsupported_formats: set[str] = set()

        for pid, meta in active_datasets.items():
            for fmt in target_formats:
                if fmt in unsupported_formats:
                    continue
                current_item += 1
                if progress_callback:
                    progress_callback(current_item, total_items, pid, fmt, meta)

                rec_key = f"{pid}::{fmt}"

                # Check if this record is already flagged with a non-recoverable error in manifest
                manifest_errors = self.manifest.get("errors", {})
                if rec_key in manifest_errors and not retry_errors:
                    cached_err_reason = manifest_errors[rec_key].get("reason", "Non-recoverable error")
                    error_item = {
                        "key": rec_key,
                        "pid": pid,
                        "name": meta.get("name"),
                        "format": fmt,
                        "reason": f"[Manifest Cached Error] {cached_err_reason}",
                    }
                    stats["errors"].append(error_item)
                    msg = f"SKIPPED (flagged non-recoverable error in manifest): {rec_key}"
                    if verbose:
                        console.print(f"  [dim yellow][!] {msg}[/dim yellow]")
                    file_logger.log(msg, level="SKIP_ERR")
                    continue

                ext = get_format_extension(fmt)
                file_path, rel_path = get_dataset_metadata_path(self.server_dir, pid, ext=ext)
                is_new = rec_key not in existing_keys or not file_path.exists()

                # Fast Timestamp Check: If dataset file exists and Search API timestamp matches manifest,
                # skip HTTP download entirely!
                meta_updated_at = meta.get("updated_at") or meta.get("published_at")
                prev_record = manifest_records.get(rec_key, {})
                prev_updated_at = prev_record.get("updated_at")

                if (
                    not is_new
                    and meta_updated_at
                    and prev_updated_at
                    and meta_updated_at == prev_updated_at
                    and not force_verify
                ):
                    stats["unchanged"].append(rec_key)
                    msg = f"UNCHANGED: {rec_key} (timestamp match: {meta_updated_at})"
                    if verbose:
                        console.print(f"  [dim][=] UNCHANGED: {rec_key} (timestamp match)[/dim]")
                    file_logger.log(msg, level="SKIP")
                    continue

                if is_new:
                    action = "added"
                else:
                    action = "updated"

                if dry_run:
                    stats[action].append(rec_key)
                    msg = f"{action.upper()} (dry-run): {rec_key} -> {rel_path}"
                    if verbose:
                        symbol = (
                            "[bold green][+] ADDED (dry-run):[/bold green]"
                            if is_new
                            else "[bold yellow][Δ] UPDATED (dry-run):[/bold yellow]"
                        )
                        console.print(f"  {symbol} {rec_key} -> {rel_path}")
                    file_logger.log(msg, level="DRYRUN")
                    continue

                # Fetch Metadata Record with retry for rate limits (HTTP 429 / 503)
                max_retries = 3
                content_bytes = None
                last_err_msg = None

                for attempt in range(max_retries):
                    content_bytes, _, last_err_msg = fetch_metadata_record(
                        self.host, pid, metadata_format=fmt, verbose=verbose
                    )
                    if content_bytes:
                        break
                    # If error is non-recoverable (Croissant validation, 404, 400), abort retries immediately
                    if is_non_recoverable_error(last_err_msg):
                        if verbose:
                            console.print(
                                f"  [dim red]  [API] Non-recoverable error for {rec_key}; skipping retries.[/dim red]"
                            )
                        break
                    time.sleep(2 * (attempt + 1))

                try:
                    if content_bytes:
                        content_hash = hashlib.sha256(content_bytes).hexdigest()

                        # Check if updated content actually changed
                        previous_hash = manifest_records.get(rec_key, {}).get("sha256")
                        if not is_new and previous_hash == content_hash:
                            stats["unchanged"].append(rec_key)
                            # Store updated_at for future fast timestamp checks
                            self.manifest["records"][rec_key]["updated_at"] = meta_updated_at
                            msg = f"UNCHANGED: {rec_key} (SHA-256 match)"
                            if verbose:
                                console.print(f"  [dim][=] UNCHANGED: {rec_key} (SHA-256 match)[/dim]")
                            file_logger.log(msg, level="SKIP")
                            continue  # Content unchanged, skip re-write

                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(file_path, "wb") as f:
                            f.write(content_bytes)

                        self.manifest["records"][rec_key] = {
                            "global_id": pid,
                            "path": rel_path,
                            "dataset_dir": file_path.parent.name,
                            "filename": file_path.name,
                            "format": fmt,
                            "harvested_at": datetime.now(UTC).isoformat(),
                            "updated_at": meta_updated_at,
                            "sha256": content_hash,
                            "name": meta.get("name"),
                        }
                        if "errors" in self.manifest and rec_key in self.manifest["errors"]:
                            del self.manifest["errors"][rec_key]

                        stats[action].append(rec_key)
                        action_label = "ADDED" if is_new else "UPDATED"
                        msg = f"{action_label}: {rec_key} -> {rel_path}"
                        if verbose:
                            symbol = (
                                "[bold green][+] ADDED:[/bold green]"
                                if is_new
                                else "[bold yellow][Δ] UPDATED:[/bold yellow]"
                            )
                            console.print(f"  {symbol} {rec_key} -> {rel_path}")
                        file_logger.log(msg, level=action_label)
                    else:
                        if is_format_unsupported_error(last_err_msg) and fmt not in unsupported_formats:
                            unsupported_formats.add(fmt)
                            error_item = {
                                "key": f"{self.host}::{fmt}",
                                "pid": f"{self.host} (all datasets)",
                                "name": "-",
                                "format": fmt,
                                "reason": (
                                    f"Format '{fmt}' not supported on server ({last_err_msg}) "
                                    "- skipped remaining datasets."
                                ),
                            }
                            stats["errors"].append(error_item)
                            msg = (
                                f"Format '{fmt}' is not supported on {self.host} ({last_err_msg}) "
                                "- skipping remaining records."
                            )
                            console.print(f"  [bold yellow][!] {msg}[/bold yellow]")
                            file_logger.log(msg, level="WARNING")
                        elif fmt not in unsupported_formats:
                            error_item = {
                                "key": rec_key,
                                "pid": pid,
                                "name": meta.get("name"),
                                "format": fmt,
                                "reason": last_err_msg or "Empty metadata response",
                            }
                            stats["errors"].append(error_item)
                            msg = f"ERROR: {rec_key} ({error_item['reason']})"
                            if verbose:
                                console.print(f"  [bold red][!] ERROR:[/bold red] {rec_key} ({error_item['reason']})")
                            file_logger.log(msg, level="ERROR")

                            if is_non_recoverable_error(last_err_msg) and not dry_run:
                                if "errors" not in self.manifest:
                                    self.manifest["errors"] = {}
                                self.manifest["errors"][rec_key] = {
                                    "global_id": pid,
                                    "format": fmt,
                                    "failed_at": datetime.now(UTC).isoformat(),
                                    "reason": last_err_msg,
                                    "non_recoverable": True,
                                }
                except Exception as e:
                    error_item = {
                        "key": rec_key,
                        "pid": pid,
                        "name": meta.get("name"),
                        "format": fmt,
                        "reason": str(e),
                    }
                    stats["errors"].append(error_item)
                    msg = f"ERROR: {rec_key} ({e})"
                    if verbose:
                        console.print(f"  [bold red][!] ERROR:[/bold red] {rec_key} ({e})")
                    file_logger.log(msg, level="ERROR")

                    if is_non_recoverable_error(str(e)) and not dry_run:
                        if "errors" not in self.manifest:
                            self.manifest["errors"] = {}
                        self.manifest["errors"][rec_key] = {
                            "global_id": pid,
                            "format": fmt,
                            "failed_at": datetime.now(UTC).isoformat(),
                            "reason": str(e),
                            "non_recoverable": True,
                        }

        if not dry_run:
            self._save_manifest()
            if verbose:
                console.print(f"[dim]  Saved manifest: {self.manifest_file}[/dim]")

        return stats


@app.command()
def harvest(
    output_dir: Annotated[
        Path | None,
        typer.Argument(
            help="Repository root directory on local disk where server subdirectories will be created.",
        ),
    ] = None,
    server: Annotated[
        str,
        typer.Option(
            "--server",
            "-s",
            envvar="DATAVERSE_SERVER",
            help="Target Dataverse server hostname (e.g. dataverse.nl, dataverse.harvard.edu) or ALL.",
        ),
    ] = "ALL",
    country: Annotated[
        str | None,
        typer.Option(
            "--country",
            "-c",
            help="Filter servers by 2-letter ISO code (e.g. NL, US, FR, DE, CA, GB) via ISO crosswalk.",
        ),
    ] = None,
    doi: Annotated[
        str | None,
        typer.Option(
            "--doi",
            "--pid",
            "-p",
            help="Target specific dataset DOI or Persistent ID (e.g. doi:10.34894/EOUMOE).",
        ),
    ] = None,
    since: Annotated[
        str | None,
        typer.Option(
            "--since",
            "--start-date",
            help="Harvest datasets added/updated since specified date (YYYY-MM-DD or 7d / 30d).",
        ),
    ] = None,
    query: Annotated[
        str | None,
        typer.Option(
            "--query",
            "-q",
            help="Filter datasets by keyword search query (e.g. climate, archaeology).",
        ),
    ] = None,
    metadata_format: Annotated[
        list[str] | None,
        typer.Option(
            "--format",
            "-f",
            help="[REQUIRED] Target metadata format(s): croissant, native, ddi, schema.org, datacite, or 'all'.",
        ),
    ] = None,
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            "-n",
            help="Maximum number of dataset records to harvest per server (default: 10, set to 0 for no limit).",
        ),
    ] = 10,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Preview additions, updates, and deletions without modifying local files.",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable detailed activity logging (HTTP requests, file paths, diff actions).",
        ),
    ] = False,
    refresh_catalog: Annotated[
        bool,
        typer.Option(
            "--refresh-catalog",
            "--refresh",
            "-r",
            help="Force a live catalog refresh from the Dataverse Search API, bypassing local 24-hour cache.",
        ),
    ] = False,
    cache_ttl: Annotated[
        int,
        typer.Option(
            "--cache-ttl",
            help="Server dataset catalog cache expiration time in hours (default: 24).",
        ),
    ] = 24,
    retry_errors: Annotated[
        bool,
        typer.Option(
            "--retry-errors",
            help="Force re-harvesting records previously flagged with non-recoverable errors in .manifest.json.",
        ),
    ] = False,
    force_verify: Annotated[
        bool,
        typer.Option(
            "--verify-sha256",
            "--force-download",
            help="Force downloading metadata and verifying SHA-256 for all records, bypassing fast timestamp check.",
        ),
    ] = False,
    all_datasets: Annotated[
        bool,
        typer.Option(
            "--all-datasets",
            "--all",
            "-a",
            help="Harvest all datasets (by default, only datasets containing tabular data files are harvested).",
        ),
    ] = False,
    tabular_only: Annotated[
        bool,
        typer.Option(
            "--tabular",
            "-t",
            help="Harvest only datasets containing rectangular/tabular data files with variables (default behavior).",
        ),
    ] = True,
    list_servers: Annotated[
        bool,
        typer.Option(
            "--list-servers",
            "-l",
            help="List available Dataverse servers matching filters and exit.",
        ),
    ] = False,
    show_stats: Annotated[
        bool,
        typer.Option(
            "--stats",
            "--server-stats",
            help="Display dataset, total file, and tabular data file counts for matching Dataverse servers and exit.",
        ),
    ] = False,
    api_token: Annotated[
        str | None,
        typer.Option(
            "--api-token",
            "--key",
            "-k",
            help="Dataverse API Token (or set DATAVERSE_API_TOKEN env var) for repositories requiring authentication.",
        ),
    ] = None,
):
    """
    Harvest and incrementally sync Dataverse metadata records across servers into local directory structures.
    """
    if show_stats:
        fetch_target = None if server.upper() == "ALL" else server
        installations = get_global_installations(target_server=fetch_target, country_filter=country)
        if not installations:
            console.print("[bold red]No matching Dataverse servers found.[/bold red]")
            raise typer.Exit(code=1)

        table = Table(
            title=f"Dataverse Server Statistics ({len(installations)} server(s))",
            header_style="bold magenta",
            expand=False,
        )
        table.add_column("Hostname", style="cyan", no_wrap=True)
        table.add_column("Country", style="green", no_wrap=True)
        table.add_column("Version", style="dim magenta", justify="center", no_wrap=True)
        table.add_column("Datasets", style="bold yellow", justify="right", no_wrap=True)
        table.add_column("Files", style="white", justify="right", no_wrap=True)
        table.add_column("Tabular", style="bold green", justify="right", no_wrap=True)
        table.add_column("Tabular %", style="dim cyan", justify="right", no_wrap=True)
        table.add_column("Status / Note", style="italic")

        suggestions_to_show = []
        raw_installations = fetch_raw_installations()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[bold cyan]Fetching repository statistics...", total=len(installations))
            for inst in installations:
                host = inst.get("hostname", "")
                progress.update(task, description=f"[bold yellow]Querying {host}...[/bold yellow]")
                if api_token and fetch_target:
                    save_server_token(host, api_token, None)
                counts = fetch_server_stats(
                    host,
                    query=query,
                    api_token=api_token,
                    repo_root=output_dir,
                    refresh_cache=refresh_catalog,
                    cache_ttl_hours=float(cache_ttl),
                )
                is_dv = counts.get("is_dataverse", False)
                err = counts.get("error")

                url = f"https://{host}" if not host.startswith("http") else host
                clickable_host = f"[link={url}]{host}[/link]"

                ver_raw = str(counts["version"]).strip() if counts.get("version") else ""
                ver_val = f"v{ver_raw.split()[0]}" if ver_raw else "-"
                country_val = inst.get("country", "") or "Global"

                if counts.get("requires_token") and not counts.get("datasets"):
                    table.add_row(
                        clickable_host,
                        country_val,
                        ver_val,
                        "-",
                        "-",
                        "-",
                        "-",
                        "[bold yellow]Requires Token (-k)[/bold yellow]",
                    )
                elif not is_dv:
                    err_msg = str(err) if err else "Not a Dataverse server"
                    table.add_row(
                        clickable_host,
                        country_val,
                        ver_val,
                        "-",
                        "-",
                        "-",
                        "-",
                        f"[bold red]{err_msg}[/bold red]",
                    )
                    if fetch_target:
                        suggs = find_registry_suggestions(fetch_target, raw_installations)
                        for s in suggs:
                            if s["hostname"].lower() != host.lower() and s not in suggestions_to_show:
                                suggestions_to_show.append(s)
                else:
                    ds_count = int(counts["datasets"] or 0)
                    files_count = int(counts["files"] or 0)
                    tab_count = int(counts["tabular_files"] or 0)
                    pct_str = f"{(tab_count / files_count * 100):.1f}%" if files_count > 0 else "0.0%"
                    table.add_row(
                        clickable_host,
                        country_val,
                        ver_val,
                        f"{ds_count:,}",
                        f"{files_count:,}",
                        f"{tab_count:,}",
                        pct_str,
                        "[bold green]Online[/bold green] [dim](cached)[/dim]"
                        if counts.get("cached")
                        else "[bold green]Online[/bold green]",
                    )
                progress.advance(task)

        console.print()
        console.print(table)

        if suggestions_to_show:
            console.print()
            console.print(
                "[bold yellow]Did you mean one of these known Dataverse installations from the registry?[/bold yellow]"
            )
            for s in suggestions_to_show:
                console.print(f"  • [bold cyan]{s['hostname']}[/bold cyan] ({s['name']} - {s['country']})")
            console.print()

        raise typer.Exit(code=0)

    if list_servers:
        # Override target_server if ALL so we fetch global list
        fetch_target = None if server.upper() == "ALL" else server
        installations = get_global_installations(target_server=fetch_target, country_filter=country)
        if not installations:
            console.print("[bold red]No matching Dataverse servers found.[/bold red]")
            raise typer.Exit(code=1)

        table = Table(title=f"Global Dataverse Servers ({len(installations)} found)", header_style="bold magenta")
        table.add_column("Hostname", style="cyan", no_wrap=True)
        table.add_column("Institution / Name", style="white")
        table.add_column("Country", style="green", no_wrap=True)
        table.add_column("Country Code", style="yellow", justify="center")

        for inst in installations:
            host = inst.get("hostname", "")
            url = f"https://{host}" if not host.startswith("http") else host
            clickable_host = f"[link={url}]{host}[/link]"
            table.add_row(
                clickable_host,
                inst.get("name", ""),
                inst.get("country", "") or "Global",
                inst.get("country_code", "") or "-",
            )

        console.print(table)
        raise typer.Exit(code=0)

    if not output_dir:
        env_repo = os.environ.get("DARTFX_DATAVERSE_REPOSITORY")
        if env_repo:
            output_dir = Path(env_repo)

    if not output_dir:
        console.print(
            "[bold red]Error: Missing required argument 'OUTPUT_DIR' "
            "(or set DARTFX_DATAVERSE_REPOSITORY env var).[/bold red]"
        )
        console.print(
            "[yellow]Usage: uv run python utils/harvester.py <OUTPUT_DIR> --format <FORMAT> [OPTIONS][/yellow]"
        )
        raise typer.Exit(code=1)

    parsed_formats = normalize_formats(metadata_format)
    if not parsed_formats:
        console.print("[bold red]Error: Missing required option '--format' / '-f'.[/bold red]")
        console.print(
            "[yellow]Usage: uv run python utils/harvester.py <OUTPUT_DIR> --format <FORMAT> [OPTIONS][/yellow]"
        )
        console.print("[yellow]Available formats: croissant, native, ddi, schema.org, datacite, or 'all'[/yellow]")
        raise typer.Exit(code=1)

    # Initialize Repository Root File Logger
    timestamp_str = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    log_file_path = output_dir.resolve() / f"harvester-{timestamp_str}.log"
    global file_logger
    file_logger = HarvesterFileLogger(log_file_path)

    file_logger.log("================================================================================")
    file_logger.log("Dataverse Metadata Harvester & Sync Execution Started")
    file_logger.log(f"Execution Log File: {log_file_path}")
    file_logger.log("--------------------------------------------------------------------------------")
    file_logger.log(f"Output Directory: {output_dir.resolve()}")
    file_logger.log(f"Target Server: {server}")
    file_logger.log(f"Target Dataset DOI: {doi if doi else '(None)'}")
    file_logger.log(f"Country Filter: {country if country else '(None)'}")
    file_logger.log(f"Metadata Formats: {', '.join(parsed_formats)}")
    file_logger.log(f"Since Date Filter: {since if since else '(All Time)'}")
    file_logger.log(f"Search Query Filter: {query if query else '(None)'}")
    effective_tabular = False if all_datasets else tabular_only
    file_logger.log(f"Tabular Data Only Filter: {effective_tabular}")
    effective_limit = None if limit == 0 else limit
    file_logger.log(f"Record Limit: {effective_limit if effective_limit is not None else '(Unlimited)'}")
    file_logger.log(f"Catalog Cache: {'Refreshed (forced)' if refresh_catalog else f'Enabled ({cache_ttl}h TTL)'}")
    file_logger.log(
        f"Incremental Verification: {'Full SHA-256 Download' if force_verify else 'Fast Search API Timestamp Match'}"
    )
    file_logger.log(f"Retry Manifest Errors: {retry_errors}")
    file_logger.log(f"Dry Run Mode: {dry_run}")
    file_logger.log(f"Verbose Logging: {verbose}")
    file_logger.log("================================================================================")

    console.print(
        Panel.fit(
            "[bold green]Dataverse Metadata Harvester & Sync CLI[/bold green]\n"
            "[dim]Powered by Typer, Rich, pyDataverse & MCP[/dim]",
            border_style="cyan",
        )
    )

    # Summary table of execution configuration
    config_table = Table(show_header=False, box=None)
    config_table.add_column("Key", style="bold cyan")
    config_table.add_column("Value", style="yellow")
    config_table.add_row("Repository Root Output", str(output_dir.resolve()))
    config_table.add_row("Execution Log File", str(log_file_path))
    config_table.add_row("Target Server", server)
    config_table.add_row("Target Dataset DOI", doi if doi else "(None)")
    config_table.add_row("Country Filter", country if country else "(None)")
    config_table.add_row("Metadata Formats", ", ".join(parsed_formats))
    config_table.add_row("Since Date Filter", since if since else "(All Time)")
    config_table.add_row("Search Query Filter", query if query else "(None)")
    config_table.add_row("Tabular Data Only Filter", str(effective_tabular))
    config_table.add_row(
        "Record Limit / Server", str(effective_limit) if effective_limit is not None else "(Unlimited)"
    )
    config_table.add_row("Catalog Cache", "Refreshed (forced)" if refresh_catalog else f"Enabled ({cache_ttl}h TTL)")
    config_table.add_row(
        "Incremental Check", "Full SHA-256 Download Verification" if force_verify else "Fast Timestamp Match"
    )
    config_table.add_row("Retry Manifest Errors", str(retry_errors))
    config_table.add_row("Dry Run Mode", str(dry_run))
    config_table.add_row("Verbose Logging", str(verbose))

    console.print(config_table)
    console.print()

    # Discover Servers
    installations = get_global_installations(target_server=server, country_filter=country)
    if not installations:
        console.print("[bold red]No matching Dataverse servers found for given criteria.[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"[bold green]Found {len(installations)} Dataverse server(s) matching criteria.[/bold green]\n")

    overall_stats = {"added": 0, "updated": 0, "deleted": 0, "unchanged": 0, "errors": 0}
    summary_rows = []
    all_errors = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        server_task = progress.add_task("[bold cyan]Syncing Servers...", total=len(installations))

        for inst in installations:
            host = inst["hostname"]
            progress.update(server_task, description=f"[bold yellow]Syncing {host}...[/bold yellow]")

            dataset_task = progress.add_task(
                f"  [dim cyan]Querying dataset catalog on {host}...[/dim cyan]", total=1, visible=True
            )

            def on_progress(
                current: int,
                total: int,
                pid: str,
                _fmt: str,
                meta: dict | None = None,
                task_id=dataset_task,
            ):
                if total > 0:
                    dataset_name = (meta.get("name") if meta else None) or pid
                    clean_name = dataset_name.strip() if dataset_name else pid
                    display_name = (clean_name[:42] + "...") if len(clean_name) > 45 else clean_name
                    progress.update(
                        task_id,
                        total=total,
                        completed=current - 1,
                        description=f"  [cyan]Processing {display_name}[/cyan]",
                        visible=True,
                    )

            try:
                if api_token:
                    save_server_token(host, api_token, output_dir)
                harvester = ServerHarvester(host, output_dir)
                stats = harvester.sync(
                    query=query,
                    since_date=since,
                    dry_run=dry_run,
                    limit=effective_limit,
                    metadata_formats=parsed_formats,
                    verbose=verbose,
                    target_doi=doi,
                    refresh_catalog=refresh_catalog,
                    cache_ttl_hours=cache_ttl,
                    retry_errors=retry_errors,
                    force_verify=force_verify,
                    tabular_only=tabular_only,
                    api_token=api_token,
                    progress_callback=on_progress,
                )
            except Exception as e:
                stats = {
                    "added": [],
                    "updated": [],
                    "deleted": [],
                    "unchanged": [],
                    "errors": [{"key": host, "pid": host, "format": "-", "reason": str(e)}],
                }

            num_added = len(stats["added"])
            num_updated = len(stats["updated"])
            num_unchanged = len(stats.get("unchanged", []))
            num_deleted = len(stats["deleted"])
            num_errors = len(stats["errors"])

            overall_stats["added"] += num_added
            overall_stats["updated"] += num_updated
            overall_stats["unchanged"] += num_unchanged
            overall_stats["deleted"] += num_deleted
            overall_stats["errors"] += num_errors

            all_errors.extend(stats.get("errors", []))

            summary_rows.append((host, inst["country"], num_added, num_updated, num_unchanged, num_deleted, num_errors))
            total_cnt = int(progress.tasks[dataset_task].total or 1)
            progress.update(dataset_task, completed=max(1, total_cnt), visible=False)
            progress.advance(server_task)

    # Display final sync summary table
    console.print("\n[bold green]================ Sync Summary Report ================[/bold green]\n")
    results_table = Table(show_header=True, header_style="bold magenta")
    results_table.add_column("Dataverse Server", style="cyan")
    results_table.add_column("Country", style="dim")
    results_table.add_column("Added (+)", style="green", justify="right")
    results_table.add_column("Updated (Δ)", style="yellow", justify="right")
    results_table.add_column("Unchanged (=)", style="dim cyan", justify="right")
    results_table.add_column("Deleted (-)", style="red", justify="right")
    results_table.add_column("Errors (!)", style="bold red", justify="right")

    file_logger.log("================ Sync Summary Report ================")
    for host, country_name, added, updated, unchanged, deleted, errors in summary_rows:
        url = f"https://{host}" if not host.startswith("http") else host
        clickable_host = f"[link={url}]{host}[/link]"
        results_table.add_row(
            clickable_host,
            country_name or "Global",
            str(added),
            str(updated),
            str(unchanged),
            str(deleted),
            str(errors),
        )
        file_logger.log(
            f"Server: {host} ({country_name or 'Global'}) | Added: {added} | "
            f"Updated: {updated} | Unchanged: {unchanged} | Deleted: {deleted} | Errors: {errors}"
        )

    console.print(results_table)

    summary_panel_text = (
        f"[bold green]Total Added (+): {overall_stats['added']}[/bold green]  |  "
        f"[bold yellow]Total Updated (Δ): {overall_stats['updated']}[/bold yellow]  |  "
        f"[dim cyan]Total Unchanged (=): {overall_stats['unchanged']}[/dim cyan]  |  "
        f"[bold red]Total Deleted (-): {overall_stats['deleted']}[/bold red]  |  "
        f"[bold red]Total Errors (!): {overall_stats['errors']}[/bold red]"
    )

    console.print(
        Panel(
            summary_panel_text,
            title="[bold]Harvest Completed[/bold]",
            border_style="green" if overall_stats["errors"] == 0 else "yellow",
        )
    )
    file_logger.log(
        f"Total Added (+): {overall_stats['added']} | Total Updated (Δ): {overall_stats['updated']} | "
        f"Total Unchanged (=): {overall_stats['unchanged']} | Total Deleted (-): {overall_stats['deleted']} | "
        f"Total Errors (!): {overall_stats['errors']}"
    )

    # Print detailed error log table if errors occurred
    if all_errors:
        console.print(f"\n[bold red]==== Harvesting Errors Report ({len(all_errors)} Failed) ====[/bold red]\n")
        err_table = Table(show_header=True, header_style="bold red")
        err_table.add_column("Dataset PID / Record", style="cyan")
        err_table.add_column("Format", style="yellow", justify="center")
        err_table.add_column("Error Reason / Details", style="bold red")

        file_logger.log(f"==== Harvesting Errors Report ({len(all_errors)} Failed) ====")

        for err in all_errors:
            if isinstance(err, dict):
                pid_display = err.get("pid") or err.get("key", "Unknown")
                fmt_display = err.get("format", "-")
                reason_display = err.get("reason", "Unknown error")
            else:
                pid_display = str(err)
                fmt_display = "-"
                reason_display = "Error occurred"

            err_table.add_row(pid_display, fmt_display, reason_display)
            file_logger.log(f"PID: {pid_display} | Format: {fmt_display} | Reason: {reason_display}", level="ERROR")

        console.print(err_table)
        console.print()

    file_logger.log("Harvesting process completed.")


if __name__ == "__main__":
    app()
