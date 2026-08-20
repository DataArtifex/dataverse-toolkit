# SPDX-FileCopyrightText: 2024-present kulnor <pascal@codata.org>
#
# SPDX-License-Identifier: MIT
from dotenv import find_dotenv, load_dotenv

from .dataverse import (
    DataverseApiError,
    DataverseServer,
    SearchParameters,
    ServerInstallation,
    fetch_dataverse_installations,
)
from .harvester import (
    ServerHarvester,
    fetch_active_datasets,
    fetch_server_stats,
    resolve_server_token,
    save_server_token,
)

# Auto-load environment variables from .env file
load_dotenv(find_dotenv(usecwd=True))

__all__ = [
    "DataverseApiError",
    "DataverseServer",
    "SearchParameters",
    "ServerInstallation",
    "fetch_dataverse_installations",
    "ServerHarvester",
    "fetch_active_datasets",
    "fetch_server_stats",
    "resolve_server_token",
    "save_server_token",
]
