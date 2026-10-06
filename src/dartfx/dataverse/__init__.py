# SPDX-FileCopyrightText: 2024-present kulnor <pascal@codata.org>
#
# SPDX-License-Identifier: MIT
from dotenv import find_dotenv, load_dotenv

from .dataverse import (
    COUNTRY_TO_ISO2,
    DATAVERSES_DIRECTORY_URLS,
    DataverseApiError,
    DataverseServer,
    SearchParameters,
    ServerInstallation,
    fetch_dataverse_installations,
    get_iso2_code,
    matches_country,
)
from .harvester import (
    ServerHarvester,
    analyze_harvest_errors,
    classify_harvest_error,
    fetch_active_datasets,
    fetch_server_stats,
    format_response_latency,
    format_version,
    resolve_server_token,
    save_server_token,
)

# Auto-load environment variables from .env file
load_dotenv(find_dotenv(usecwd=True))

__all__ = [
    "COUNTRY_TO_ISO2",
    "DATAVERSES_DIRECTORY_URLS",
    "DataverseApiError",
    "DataverseServer",
    "SearchParameters",
    "ServerInstallation",
    "fetch_dataverse_installations",
    "get_iso2_code",
    "matches_country",
    "ServerHarvester",
    "fetch_active_datasets",
    "fetch_server_stats",
    "format_response_latency",
    "format_version",
    "resolve_server_token",
    "save_server_token",
    "classify_harvest_error",
    "analyze_harvest_errors",
]
