from unittest.mock import MagicMock

import pytest
from linkedin_api import Linkedin


@pytest.fixture
def mock_linkedin_api():
    """Returns a mocked Linkedin API client."""
    mock = MagicMock(spec=Linkedin)
    mock.client = MagicMock()
    mock.client.session = MagicMock()
    return mock


@pytest.fixture
def mock_requests(mocker):
    """Returns a mocked requests module."""
    return mocker.patch("requests.post")


@pytest.fixture
def mock_env(mocker):
    """Mocks common environment variables."""
    mocker.patch.dict(
        "os.environ",
        {
            "LINKEDIN_CLIENT_ID": "test_id",
            "LINKEDIN_CLIENT_SECRET": "test_secret",
            "LINKEDIN_REDIRECT_URI": "http://localhost:8000/callback",
            "WRITE_LI_AT": "test_li_at",
        },
    )
