import inspect
import json
import logging
import os
from typing import Any, Literal

import requests
import requests_cache
from pydantic import BaseModel, ConfigDict, Field

from .__about__ import __version__

# Raw Country Name to ISO 3166-1 Alpha-2 Code Crosswalk (Alphabetical)
COUNTRY_TO_ISO2: dict[str, str] = {
    "AFGHANISTAN": "AF",
    "ALBANIA": "AL",
    "ALGERIA": "DZ",
    "ANDORRA": "AD",
    "ANGOLA": "AO",
    "ARGENTINA": "AR",
    "ARMENIA": "AM",
    "AUSTRALIA": "AU",
    "AUSTRIA": "AT",
    "AZERBAIJAN": "AZ",
    "BAHAMAS": "BS",
    "BAHRAIN": "BH",
    "BANGLADESH": "BD",
    "BARBADOS": "BB",
    "BELARUS": "BY",
    "BELGIUM": "BE",
    "BELIZE": "BZ",
    "BENIN": "BJ",
    "BHUTAN": "BT",
    "BOLIVIA": "BO",
    "BOSNIA AND HERZEGOVINA": "BA",
    "BOTSWANA": "BW",
    "BRAZIL": "BR",
    "BRUNEI": "BN",
    "BULGARIA": "BG",
    "BURKINA FASO": "BF",
    "BURUNDI": "BI",
    "CABO VERDE": "CV",
    "CAMBODIA": "KH",
    "CAMEROON": "CM",
    "CANADA": "CA",
    "CAPE VERDE": "CV",
    "CENTRAL AFRICAN REPUBLIC": "CF",
    "CHAD": "TD",
    "CHILE": "CL",
    "CHINA": "CN",
    "COLOMBIA": "CO",
    "COMOROS": "KM",
    "CONGO": "CG",
    "COSTA RICA": "CR",
    "CROATIA": "HR",
    "CUBA": "CU",
    "CYPRUS": "CY",
    "CZECH REPUBLIC": "CZ",
    "CZECHIA": "CZ",
    "DEMOCRATIC REPUBLIC OF THE CONGO": "CD",
    "DENMARK": "DK",
    "DEUTSCHLAND": "DE",
    "DJIBOUTI": "DJ",
    "DOMINICA": "DM",
    "DOMINICAN REPUBLIC": "DO",
    "ECUADOR": "EC",
    "EGYPT": "EG",
    "EL SALVADOR": "SV",
    "EQUATORIAL GUINEA": "GQ",
    "ERITREA": "ER",
    "ESTONIA": "EE",
    "ESWATINI": "SZ",
    "ETHIOPIA": "ET",
    "FIJI": "FJ",
    "FINLAND": "FI",
    "FRANCE": "FR",
    "GABON": "GA",
    "GAMBIA": "GM",
    "GEORGIA": "GE",
    "GERMANY": "DE",
    "GHANA": "GH",
    "GREAT BRITAIN": "GB",
    "GREECE": "GR",
    "GRENADA": "GD",
    "GUATEMALA": "GT",
    "GUINEA": "GN",
    "GUINEA-BISSAU": "GW",
    "GUYANA": "GY",
    "HAITI": "HT",
    "HOLLAND": "NL",
    "HONDURAS": "HN",
    "HONG KONG": "HK",
    "HUNGARY": "HU",
    "ICELAND": "IS",
    "INDIA": "IN",
    "INDONESIA": "ID",
    "IRAN": "IR",
    "IRAQ": "IQ",
    "IRELAND": "IE",
    "ISRAEL": "IL",
    "ITALY": "IT",
    "IVORY COAST": "CI",
    "JAMAICA": "JM",
    "JAPAN": "JP",
    "JORDAN": "JO",
    "KAZAKHSTAN": "KZ",
    "KENYA": "KE",
    "KIRIBATI": "KI",
    "KOREA": "KR",
    "KUWAIT": "KW",
    "KYRGYZSTAN": "KG",
    "LAOS": "LA",
    "LATVIA": "LV",
    "LEBANON": "LB",
    "LESOTHO": "LS",
    "LIBERIA": "LR",
    "LIBYA": "LY",
    "LIECHTENSTEIN": "LI",
    "LITHUANIA": "LT",
    "LUXEMBOURG": "LU",
    "MADAGASCAR": "MG",
    "MALAWI": "MW",
    "MALAYSIA": "MY",
    "MALDIVES": "MV",
    "MALI": "ML",
    "MALTA": "MT",
    "MARSHALL ISLANDS": "MH",
    "MAURITANIA": "MR",
    "MAURITIUS": "MU",
    "MEXICO": "MX",
    "MICRONESIA": "FM",
    "MOLDOVA": "MD",
    "MONACO": "MC",
    "MONGOLIA": "MN",
    "MONTENEGRO": "ME",
    "MOROCCO": "MA",
    "MOZAMBIQUE": "MZ",
    "MYANMAR": "MM",
    "NAMIBIA": "NA",
    "NAURU": "NR",
    "NEPAL": "NP",
    "NETHERLANDS": "NL",
    "NEW ZEALAND": "NZ",
    "NICARAGUA": "NI",
    "NIGER": "NE",
    "NIGERIA": "NG",
    "NORTH KOREA": "KP",
    "NORTH MACEDONIA": "MK",
    "NORWAY": "NO",
    "OMAN": "OM",
    "PAKISTAN": "PK",
    "PALAU": "PW",
    "PALESTINE": "PS",
    "PANAMA": "PA",
    "PAPUA NEW GUINEA": "PG",
    "PARAGUAY": "PY",
    "PERU": "PE",
    "PHILIPPINES": "PH",
    "POLAND": "PL",
    "PORTUGAL": "PT",
    "QATAR": "QA",
    "ROMANIA": "RO",
    "RUSSIA": "RU",
    "RUSSIAN FEDERATION": "RU",
    "RWANDA": "RW",
    "SAINT KITTS AND NEVIS": "KN",
    "SAINT LUCIA": "LC",
    "SAINT VINCENT AND THE GRENADINES": "VC",
    "SAMOA": "WS",
    "SAN MARINO": "SM",
    "SAO TOME AND PRINCIPE": "ST",
    "SAUDI ARABIA": "SA",
    "SENEGAL": "SN",
    "SERBIA": "RS",
    "SEYCHELLES": "SC",
    "SIERRA LEONE": "SL",
    "SINGAPORE": "SG",
    "SLOVAKIA": "SK",
    "SLOVENIA": "SI",
    "SOLOMON ISLANDS": "SB",
    "SOMALIA": "SO",
    "SOUTH AFRICA": "ZA",
    "SOUTH KOREA": "KR",
    "SOUTH SUDAN": "SS",
    "SPAIN": "ES",
    "SRI LANKA": "LK",
    "SUDAN": "SD",
    "SURINAME": "SR",
    "SWEDEN": "SE",
    "SWITZERLAND": "CH",
    "SYRIA": "SY",
    "TAIWAN": "TW",
    "TAIWAN (ROC)": "TW",
    "TAJIKISTAN": "TJ",
    "TANZANIA": "TZ",
    "THAILAND": "TH",
    "TIMOR-LESTE": "TL",
    "TOGO": "TG",
    "TONGA": "TO",
    "TRINIDAD AND TOBAGO": "TT",
    "TUNISIA": "TN",
    "TURKEY": "TR",
    "TURKMENISTAN": "TM",
    "TUVALU": "TV",
    "TÜRKIYE": "TR",
    "UGANDA": "UG",
    "UK": "GB",
    "UKRAINE": "UA",
    "UNITED ARAB EMIRATES": "AE",
    "UNITED KINGDOM": "GB",
    "UNITED STATES": "US",
    "UNITED STATES OF AMERICA": "US",
    "URUGUAY": "UY",
    "USA": "US",
    "UZBEKISTAN": "UZ",
    "VANUATU": "VU",
    "VATICAN CITY": "VA",
    "VENEZUELA": "VE",
    "VIETNAM": "VN",
    "YEMEN": "YE",
    "ZAMBIA": "ZM",
    "ZIMBABWE": "ZW",
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


DATAVERSES_DIRECTORY_URLS: list[str] = [
    "https://raw.githubusercontent.com/IQSS/dataverse-installations/refs/heads/main/data/data.json",
]


class ServerInstallation(BaseModel):
    """Represents a dataverse installation.
    Based on the content of the data.json file in the dataverse-installations
    repository at https://github.com/IQSS/dataverse-installations
    """

    model_config = ConfigDict(extra="ignore")

    name: str | None = None
    description: str | None = None
    lat: float | None = None
    lng: float | None = None
    hostname: str | None = None
    metrics: bool | None = False
    launch_year: str | None = None
    country: str | None = None
    country_code: str | None = None
    continent: str | None = None
    harvesting_sets: list[str] | None = None
    core_trust_seals: list[str] | None = None
    gdcc_member: bool | None = None
    doi_authority: str | None = None
    board: str | None = None
    contact_email: str | None = None
    about_url: str | None = None
    dv_hub_id: str | None = None

    def model_post_init(self, __context: Any) -> None:
        """Derive country_code and clean hostname if not provided."""
        if not self.country_code and self.country:
            self.country_code = get_iso2_code(self.country)
        if self.hostname:
            self.hostname = self.hostname.replace("https://", "").replace("http://", "").strip("/")

    @property
    def clean_hostname(self) -> str:
        """Return cleaned hostname without protocol or trailing slash."""
        if not self.hostname:
            return ""
        return self.hostname.replace("https://", "").replace("http://", "").strip("/")

    @property
    def url(self) -> str:
        """Return HTTPS URL for the installation."""
        if not self.hostname:
            return ""
        return f"https://{self.clean_hostname}"


def fetch_dataverse_installations(
    target_server: str | None = None,
    country: str | None = None,
    timeout: float = 10.0,
    urls: list[str] | None = None,
    fallback_unlisted: bool = False,
) -> list[ServerInstallation]:
    """Returns a list of dataverse installations from remote registry endpoints.

    Supports optional filtering by server hostname or country (ISO-2 code or country name).
    If fallback_unlisted is True and a specific target_server is requested but not found in the
    registry, a fallback ServerInstallation is synthesized to support private/unlisted servers.
    """
    directory_urls = urls or DATAVERSES_DIRECTORY_URLS
    raw_list: list[dict[str, Any]] = []

    for url in directory_urls:
        if not url:
            continue
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and "installations" in data:
                    raw_list = data["installations"]
                    break
                elif isinstance(data, list):
                    raw_list = data
                    break
        except Exception:
            continue

    clean_target = (
        target_server.replace("https://", "").replace("http://", "").strip("/")
        if target_server and target_server.upper() != "ALL"
        else None
    )

    servers: list[ServerInstallation] = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        inst = ServerInstallation(**item)
        if not inst.hostname:
            continue

        # Target server filter
        if clean_target and inst.clean_hostname.lower() != clean_target.lower():
            continue

        # Country filter
        if country:
            if not matches_country(country, inst.country or "", inst.country_code or ""):
                continue

        servers.append(inst)

    # Fallback if specific target server was not found in registry
    if clean_target and not servers and fallback_unlisted:
        servers.append(
            ServerInstallation(
                hostname=clean_target,
                name=clean_target,
                country="Target Server",
                country_code="-",
            )
        )

    return servers


class DataverseApiError(Exception):
    """Custom exception for Dataverse API errors."""

    def __init__(
        self,
        message: str,
        url: str,
        status_code: int | None = None,
        response: requests.Response | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.url = url
        self.status_code = status_code
        self.response = response

    def __str__(self) -> str:
        base_message = f"{self.message}"
        base_message += f"; URL: {self.url}"
        if self.status_code is not None:
            base_message += f"; Status Code: {self.status_code}"
        return base_message


class SearchParameters(BaseModel):
    """Represents the parameters that can be passed to the search endpoint.
    See https://guides.dataverse.org/en/latest/api/search.html
    """

    q: str = Field(
        default="*",
        description=(
            "The search term or terms. Using “title:data” will search only the “title” field. "
            "“*” can be used as a wildcard either alone or adjacent to a term (i.e. “bird*”)."
        ),
    )
    type: Literal["dataverse", "dataset", "file"] | list[Literal["dataverse", "dataset", "file"]] | None = Field(
        default=None,
        description=(
            "Can be either “dataverse”, “dataset”, or “file”. "
            "Multiple “type” parameters can be used to include multiple types"
        ),
    )
    subtree: str | None = Field(
        default=None,
        description=(
            "The identifier of the Dataverse collection to which the search should be narrowed. "
            "The subtree of this Dataverse collection and all its children will be searched. "
            "Multiple “subtree” parameters can be used to include multiple Dataverse collections."
        ),
    )
    sort: Literal["name", "date"] | None = Field(
        default=None, description="The sort field. Supported values include “name” and “date”."
    )
    order: Literal["asc", "desc"] | None = Field(
        default=None, description="The order in which to sort. Can either be “asc” or “desc”"
    )
    per_page: int | None = Field(
        default=None,
        ge=1,
        le=1000,
        description="The number of results to return per request. The default is 10. The max is 1000.",
    )
    start: int | None = Field(default=None, description="A cursor for paging through search results.")
    show_relevance: bool | None = Field(
        default=None,
        description="Whether or not to show details of which fields were matched by the query. False by default.",
    )
    show_facets: bool | None = Field(
        default=None,
        description="Whether or not to show facets that can be operated on by the “fq” parameter. False by default.",
    )
    fq: list[str] | None = Field(
        default=None, description="A filter query on the search term. Multiple “fq” parameters can be used."
    )
    show_entity_ids: bool | None = Field(
        default=None, description="Whether or not to show the database IDs of the search results (for developer use)."
    )
    geo_point: str | None = Field(
        default=None,
        description="Latitude and longitude in the form geo_point=42.3,-71.1. You must supply geo_radius as well.",
    )
    geo_radius: str | None = Field(
        default=None,
        description=(
            "Radial distance in kilometers from geo_point (which must be supplied as well) such as geo_radius=1.5."
        ),
    )
    metadata_fields: list[str] | None = Field(
        default=None,
        description=(
            "Includes the requested fields for each dataset in the response. "
            "Multiple “metadata_fields” parameters can be used to include several fields."
        ),
    )


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


class DataverseServer(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    installation: ServerInstallation
    api_key: str | None = None
    on_api_error: Literal["raise", "none"] = "raise"
    on_api_success_return: Literal["json", "text", "response"] = "json"
    session: requests_cache.CachedSession = Field(
        default_factory=lambda: requests_cache.CachedSession(backend="memory", cache_name="dataverse")
    )
    user_agent: str = Field(default=f"dartfx-dataverse/{__version__}")
    ssl_verify: bool = True

    def __init__(
        self,
        server: str | ServerInstallation | None = None,  # hostname or ServerInstallation
        api_key: str | None = None,
        on_api_error: Literal["raise", "none"] = "raise",
        on_api_success_return: Literal["json", "text", "response"] = "json",
        session: requests_cache.CachedSession | None = None,
        lookup_installation: bool = True,
        **kwargs: Any,
    ) -> None:
        if server is None:
            server = (
                os.environ.get("DATAVERSE_SERVER") or os.environ.get("DATAVERSE_HOSTNAME") or "dataverse.harvard.edu"
            )

        if api_key is None:
            api_key = os.environ.get("DARTFX_DATAVERSE_API_KEY") or os.environ.get("DATAVERSE_API_KEY")

        # server
        if isinstance(server, str):
            # convert hostname to a ServerInstallation
            clean_host = server.replace("https://", "").replace("http://", "").strip("/")
            server_inst = ServerInstallation(hostname=clean_host)
            if lookup_installation:
                for inst in fetch_dataverse_installations(target_server=clean_host, fallback_unlisted=False):
                    if inst.clean_hostname.lower() == clean_host.lower() or (
                        inst.hostname and inst.hostname.lower() == clean_host.lower()
                    ):
                        server_inst = inst
                        break
        else:
            server_inst = server

        if not isinstance(server_inst, ServerInstallation):
            raise TypeError("server must be either a hostname or a ServerInstallation")

        if server_inst.hostname and server_inst.hostname.startswith("https://"):
            server_inst.hostname = server_inst.hostname[8:]

        # Create session if not provided
        if session is None:
            session = requests_cache.CachedSession(backend="memory", cache_name="dataverse")

        super().__init__(
            installation=server_inst,
            api_key=api_key,
            on_api_error=on_api_error,
            on_api_success_return=on_api_success_return,
            session=session,
            **kwargs,
        )

    #
    # API REQUESTS
    #
    def request(
        self,
        method: str,
        path: str,
        description: str | None = None,
        headers: dict[str, str] | None = None,
        success: int = 200,
        return_type: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Call the API."""
        # prepare headers
        default_headers = {"Content-Type": "application/json", "User-Agent": self.user_agent}
        if self.api_key:
            default_headers["X-Dataverse-key"] = self.api_key
        if headers is None:
            headers = {}
        headers = default_headers | headers
        # call the API
        url = f"https://{self.installation.hostname}/api/{path}"
        response = self.session.request(method, url, headers=headers, verify=self.ssl_verify, **kwargs)
        # handle response
        actual_return_type = return_type or self.on_api_success_return
        if response.status_code == success:
            if actual_return_type == "json":
                try:
                    return response.json()
                except json.JSONDecodeError as e:
                    message = f"{description} -- JSONDecodeError: {e.msg}"
                    logging.error(message)
                    if self.on_api_error != "none":
                        raise DataverseApiError(message, path, response.status_code, response) from e
                    return None
            elif actual_return_type == "text":
                return response.text
            return response
        logging.error(f"{description} -- {response.status_code}")
        logging.error(response.text)
        if self.on_api_error != "none":
            raise DataverseApiError(description or "Dataverse API Error", path, response.status_code, response)
        return None

    def get_request(
        self,
        path: str,
        description: str | None = None,
        headers: dict[str, str] | None = None,
        success: int = 200,
        return_type: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Call the API using the GET method."""
        if headers is None:
            headers = {}
        if not description:
            description = _get_caller_name()
        return self.request(
            "get", path, description, headers=headers, success=success, return_type=return_type, **kwargs
        )

    def post_request(
        self,
        path: str,
        description: str | None = None,
        headers: dict[str, str] | None = None,
        success: int = 200,
        **kwargs: Any,
    ) -> Any:
        """Call the API using the POST method."""
        if headers is None:
            headers = {}
        if not description:
            description = _get_caller_name()
        return self.request("post", path, description, headers=headers, success=success, **kwargs)

    #
    # INFO
    #
    def get_info_api_terms(self) -> Any:
        """Get API Terms of Use.

        The response contains the text value inserted as API Terms of use
        which uses the database setting :ApiTermsOfUse:.
        """
        return self.get_request("info/apiTermsOfUse")

    def get_info_export_formats(self) -> Any:
        """Get the available export formats, including custom formats.
        Introduced in version 6.5
        """
        return self.get_request("info/exportFormats")

    def get_info_server(self) -> Any:
        """Get the server name.

        This is useful when a Dataverse installation is composed of multiple app
        servers behind a load balancer.
        """
        return self.get_request("info/server")

    def get_server_info(self) -> Any:
        """Alias for get_info_server."""
        return self.get_info_server()

    def get_info_version(self) -> Any:
        """Get the Dataverse installation version. The response contains the version and build numbers:."""
        return self.get_request("info/version")

    def get_info_zip_download_limit(self) -> Any:
        """Get the configured zip file download limit. The response contains the long value of the limit in bytes."""
        return self.get_request("info/zipDownloadLimit")

    #
    # METADATA BLOCKS
    #

    def get_metadatablocks(self) -> Any:
        """Lists brief info about all metadata blocks registered in the system."""
        return self.get_request("metadatablocks")

    def get_metadatablock(self, identifier: str) -> Any:
        """Return data about the block whose identifier is passed, including
        allowed controlled vocabulary values. identifier can either be the
        block’s database id, or its name (i.e. “citation”).
        """
        return self.get_request(f"metadatablocks/{identifier}")

    #
    # DATASETS
    #

    def get_dataset(self, identifier: str) -> Any:
        """Get information about a specific dataset by its persistent identifier.

        Args:
            identifier: Persistent identifier (e.g., "doi:10.5683/SP3/FNS9EF")
        """
        return self.get_request("datasets/:persistentId/", params={"persistentId": identifier})

    def get_dataset_export(self, identifier: str, exporter: str) -> Any:
        """Get a dataset in a specific export format.

        Args:
            identifier: Persistent identifier (e.g., "doi:10.5683/SP3/FNS9EF")
            exporter: Name of the exporter (e.g., "ddi", "oai_dc", "schema.org")
        """
        return self.get_request(
            "datasets/export/", params={"exporter": exporter, "persistentId": identifier}, return_type="text"
        )

    #
    # SEARCH
    #

    def search_simple(self, q: str, **kwargs: Any) -> Any:
        """Search for dataverses, datasets, and files using a simple query string.

        Args:
            q: The search query string.
            **kwargs: Additional search parameters (type, sort, order, per_page, start, etc.)
        """
        params = SearchParameters(q=q, **kwargs)
        return self.search(params)

    def search(self, parameters: SearchParameters) -> Any:
        """Search for dataverses, datasets, and files.

        References:
        - https://guides.dataverse.org/en/latest/api/search.html
        - https://github.com/IQSS/dataverse/issues/2558

        """
        return self.get_request("search", description="Search", params=parameters.model_dump(exclude_none=True))
