import inspect
import json
import logging
from typing import Literal

import requests
import requests_cache
from pydantic import BaseModel, Field

from .__about__ import __version__


class ServerInstallation(BaseModel):
    """Represents a dataverse installation.
    Based on the content of the data.json file in the dataverse-installations
    repository at https://github.com/IQSS/dataverse-installations
    """
    name: str | None = None
    description: str | None = None
    lat: float | None = None
    lng: float | None = None
    hostname: str | None = None
    metrics: bool | None = False
    launch_year: str | None = None
    country: str | None = None
    continent: str | None = None
    harvesting_sets: list[str] | None = None
    core_trust_seals: list[str] | None = None
    gdcc_member: bool | None = None
    doi_authority: str | None = None
    board: str | None = None
    contact_email: str | None = None

def fetch_dataverse_installations() -> list[ServerInstallation]:
    """Returns a list of dataverse installations from the main branch of the dataverse-installations GitHub repo"""
    url = "https://raw.githubusercontent.com/IQSS/dataverse-installations/refs/heads/main/data/data.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    servers = []
    for item in data.get("installations"):
        servers.append(ServerInstallation(**item))
    return servers

class DataverseApiError(Exception):
    """Custom exception for Dataverse API errors."""

    def __init__(self, message, url, status_code=None, response=None):
        super().__init__(message)
        self.message = message
        self.url = url
        self.status_code = status_code
        self.response = response

    def __str__(self):
        base_message = f"{self.message}"
        base_message += f"; URL: {self.url}"
        if self.status_code is not None:
            base_message += f"; Status Code: {self.status_code}"
        return base_message

class SearchParameters(BaseModel):
    """Represents the parameters that can be passed to the search endpoint.
    See https://guides.dataverse.org/en/latest/api/search.html
    """
    q: str = Field(default='*', description='The search term or terms. Using “title:data” will search only the “title” field. “*” can be used as a wildcard either alone or adjacent to a term (i.e. “bird*”).')
    type: Literal["dataverse", "dataset", "file"] | list[Literal["dataverse", "dataset", "file"]] | None = Field(default=None, description='Can be either “dataverse”, “dataset”, or “file”. Multiple “type” parameters can be used to include multiple types')
    subtree: str | None = Field(default=None, description='The identifier of the Dataverse collection to which the search should be narrowed. The subtree of this Dataverse collection and all its children will be searched. Multiple “subtree” parameters can be used to include multiple Dataverse collections.')
    sort: Literal["name","date"] | None = Field(default=None, description='The sort field. Supported values include “name” and “date”.')
    order: Literal["asc","desc"] | None = Field(default=None, description='The order in which to sort. Can either be “asc” or “desc”')
    per_page: int | None = Field(default=None, ge=1, le=1000, description='The number of results to return per request. The default is 10. The max is 1000.')
    start: int | None = Field(default=None, description='A cursor for paging through search results.')
    show_relevance: bool | None = Field(default=None, description='Whether or not to show details of which fields were matched by the query. False by default.')
    show_facets: bool | None = Field(default=None, description='Whether or not to show facets that can be operated on by the “fq” parameter. False by default.')
    fq: list[str] | None = Field(default=None, description='A filter query on the search term. Multiple “fq” parameters can be used.')
    show_entity_ids: bool | None = Field(default=None, description='Whether or not to show the database IDs of the search results (for developer use).')
    geo_point: str | None = Field(default=None, description='Latitude and longitude in the form geo_point=42.3,-71.1. You must supply geo_radius as well.')
    geo_radius: str | None = Field(default=None, description='Radial distance in kilometers from geo_point (which must be supplied as well) such as geo_radius=1.5.')
    metadata_fields: list[str] | None = Field(default=None, description='Includes the requested fields for each dataset in the response. Multiple “metadata_fields” parameters can be used to include several fields.')


def _get_caller_name() -> str:
    """Returns the name of the function that called the current function."""
    frame = inspect.currentframe()
    if frame is None:
        return "<unknown>"
    try:
        caller_frame = frame.f_back.f_back if frame.f_back else None  # f_back of the current frame's caller
        return caller_frame.f_code.co_name if caller_frame else "<unknown>"
    finally:
        # Clean up to avoid reference cycles
        del frame

class DataverseServer:
    api_key: str | None
    installation: ServerInstallation
    on_api_error: str # controls how to handle API errors: 'raise' | 'none'
    on_api_success_return: str # controls how to handle API success: 'json' | 'text' | 'response'
    session: requests_cache.CachedSession
    user_agent: str = f"dartfx-dataverse/{__version__}"
    ssl_verify: bool = True # whether to verify SSL certificates when calling the API. Can also be set on request-cache session.

    def __init__(self,
            server: str | ServerInstallation, # hostname or ServerInstallation
            api_key: str | None = None,
            on_api_error: str = 'raise', # 'raise' | 'none'
            on_api_success_return: str = 'json', # 'json' | 'text' | 'response'
            session: requests_cache.CachedSession | None = None, # requests_cache.CachedSession
            lookup_installation: bool = True # if true and server is a hostname, look up the installation
        ) -> None:
        # server
        if isinstance(server, str):
            # convert hostname to a ServerInstallation
            server = server.replace("https://", "").replace("http://", "")
            server = ServerInstallation(hostname=server)
            if lookup_installation:
                for installation in fetch_dataverse_installations():
                    if installation.hostname == server.hostname:
                        server = installation
        if not isinstance(server, ServerInstallation):
            raise TypeError("server must be either a hostname or a ServerInstallation")
        self.installation = server
        if self.installation.hostname and self.installation.hostname.startswith("https://"):
                self.installation.hostname = self.installation.hostname[8:]
        # session
        if session is None:
            # Create a new session if one is not provided
            session = requests_cache.CachedSession(backend='memory', cache_name='dataverse')
        self.session = session
        # other params
        self.api_key = api_key
        self.on_api_error = on_api_error
        self.on_api_success_return = on_api_success_return
        self.session = session

    #
    # API REQUESTS
    #
    def request(self, method, path, description=None, headers=None, success=200, **kwargs):
        """Call the API."""
        # prepare headers
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": self.user_agent
        }
        if self.api_key:
            default_headers["X-Dataverse-key"] = self.api_key
        if headers is None:
            headers = {}
        headers = default_headers | headers
        # call the API
        url = f"https://{self.installation.hostname}/api/{path}"
        response = self.session.request(method, url, headers=headers, verify=self.ssl_verify,  **kwargs)
        # handle response
        if response.status_code == success:
            if self.on_api_success_return == 'json':
                try:
                    return response.json()
                except json.JSONDecodeError as e:
                    message = f"{description} -- JSONDecodeError: {e.msg}"
                    logging.error(message)
                    if self.on_api_error != 'none':
                        raise DataverseApiError(message, path, response.status_code, response) from e
                    return None
            elif self.on_api_success_return == 'text':
                return response.text
            return response
        logging.error(f"{description} -- {response.status_code}")
        logging.error(response.text)
        if self.on_api_error != 'none':
            raise DataverseApiError(description, path, response.status_code, response)
        return None

    def get_request(self, path, description=None, headers=None, success=200, **kwargs):
        """Call the API using the GET method."""
        if headers is None:
            headers = {}
        if not description:
            description = _get_caller_name()
        return self.request(
            "get", path, description, headers=headers, success=success, **kwargs
        )

    def post_request(self, path, description=None, headers=None, success=200, **kwargs):
        """Call the API using the POST method."""
        if headers is None:
            headers = {}
        if not description:
            description = _get_caller_name()
        return self.request(
            "post", path, description, headers=headers, success=success, **kwargs
        )

    #
    # INFO
    #
    def get_info_api_terms(self):
        """Get API Terms of Use. The response contains the text value inserted as API Terms of use which uses the database setting :ApiTermsOfUse:."""
        return self.get_request("info/apiTermsOfUse")

    def get_info_export_formats(self):
        """Get the available export formats, including custom formats.
        Introduced in version 6.5
        """
        return self.get_request("info/exportFormats")

    def get_info_server(self):
        """Get the server name. This is useful when a Dataverse installation is composed of multiple app servers behind a load balancer."""
        return self.get_request("info/server")

    def get_info_version(self):
        """Get the Dataverse installation version. The response contains the version and build numbers:."""
        return self.get_request("info/version")

    def get_info_zip_download_limit(self):
        """Get the configured zip file download limit. The response contains the long value of the limit in bytes."""
        return self.get_request("info/zipDownloadLimit")

    #
    # METADATA BLOCKS
    #

    def get_metadatablocks(self):
        """Lists brief info about all metadata blocks registered in the system."""
        return self.get_request("metadatablocks")


    def get_metadatablock(self, identifier: str):
        """Return data about the block whose identifier is passed, including allowed controlled vocabulary values. identifier can either be the block’s database id, or its name (i.e. “citation”)."""
        return self.get_request(f"metadatablocks/{identifier}")

    #
    # SEARCH
    #

    def search(self, parameters: SearchParameters):
        """ Search for dataverses, datasets, and files.

        References:
        - https://guides.dataverse.org/en/latest/api/search.html
        - https://github.com/IQSS/dataverse/issues/2558

        """
        return self.get_request("search", description="Search", params=parameters.model_dump())
