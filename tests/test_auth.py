import json
import time
from unittest.mock import patch


from write_flow.auth import (
    _load_cached_token,
    _save_token,
    get_oauth_token,
)


def test_save_and_load_token(tmp_path):
    """Test saving and loading a token from the cache file."""
    token_data = {"access_token": "test_token", "expires_in": 3600}

    with patch("write_flow.auth.TOKEN_CACHE_FILE", str(tmp_path / "token.json")):
        _save_token(token_data)
        loaded = _load_cached_token()
        assert loaded["access_token"] == "test_token"
        assert loaded["expires_at"] > time.time()


def test_load_expired_token(tmp_path):
    """Test that an expired token is not loaded."""
    token_data = {"access_token": "old_token", "expires_at": time.time() - 1000}
    cache_file = tmp_path / "token.json"
    with open(cache_file, "w") as f:
        json.dump(token_data, f)

    with patch("write_flow.auth.TOKEN_CACHE_FILE", str(cache_file)):
        assert _load_cached_token() is None


def test_get_oauth_token_cached(mocker):
    """Test get_oauth_token when a valid token is cached."""
    mocker.patch(
        "write_flow.auth._load_cached_token",
        return_value={"access_token": "cached_one"},
    )
    assert get_oauth_token() == "cached_one"
