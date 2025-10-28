from dotenv import load_dotenv
from pathlib import Path
import pytest

from dartfx.dataverse.dataverse import DataverseServer

@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv_path = Path(__file__).parent / "../.env"  # Construct path from current test file dir
    load_dotenv(dotenv_path=dotenv_path)

@pytest.fixture(scope="session", autouse=True)
def test_server():
    return DataverseServer("demo.dataverse.org", lookup_installation=False)