"""
write_flow/auth.py
------------------
Auth client for the write account.

  OAuth token   → used for create/publish post (official API)

OAuth token is fetched automatically using the authorization_code flow
and cached in .oauth_token_cache.json.

.env keys needed for write account:
    LINKEDIN_CLIENT_ID=86xyz...
    LINKEDIN_CLIENT_SECRET=abc123...
    LINKEDIN_REDIRECT_URI=http://localhost:8000/callback
    LINKEDIN_OAUTH_TOKEN=           # auto-filled after first OAuth run
"""

import json
import logging
import os
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

TOKEN_CACHE_FILE = ".oauth_token_cache.json"

OAUTH_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
OAUTH_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# Scopes needed for posting
OAUTH_SCOPES = ["openid", "profile", "w_member_social"]


# ---------------------------------------------------------------------------
# OAuth token management
# ---------------------------------------------------------------------------
def _load_cached_token() -> dict | None:
    if not os.path.exists(TOKEN_CACHE_FILE):
        return None
    try:
        with open(TOKEN_CACHE_FILE) as f:
            data = json.load(f)
        # check expiry with 5-minute buffer
        if data.get("expires_at", 0) > time.time() + 300:
            return data
        logger.info("[auth] Cached OAuth token expired")
    except Exception:
        pass
    return None


def _save_token(token_data: dict) -> None:
    token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600)
    with open(TOKEN_CACHE_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    os.chmod(TOKEN_CACHE_FILE, 0o600)  # owner-read only
    logger.info("[auth] OAuth token cached to %s", TOKEN_CACHE_FILE)


def _exchange_code_for_token(code: str, redirect_uri: str) -> dict:
    resp = requests.post(
        OAUTH_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": os.environ["LINKEDIN_CLIENT_ID"],
            "client_secret": os.environ["LINKEDIN_CLIENT_SECRET"],
        },
    )
    resp.raise_for_status()
    return resp.json()


def _run_local_oauth_flow(redirect_uri: str) -> str:
    """
    Opens browser for LinkedIn consent, spins up a local HTTP server
    to catch the callback, returns the authorization code.
    Only needed once — token is cached after first run.
    """
    client_id = os.environ["LINKEDIN_CLIENT_ID"]
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(OAUTH_SCOPES),
        "state": "write_flow_auth",
    }
    auth_url = f"{OAUTH_AUTH_URL}?{urlencode(params)}"
    logger.info("[auth] Opening browser for LinkedIn OAuth consent...")
    logger.info("[auth] If browser doesn't open, visit: %s", auth_url)
    webbrowser.open(auth_url)

    # parse port from redirect_uri
    parsed = urlparse(redirect_uri)
    port = parsed.port or 8000
    code_holder: list[str] = []

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            qs = parse_qs(urlparse(self.path).query)
            if "code" in qs:
                code_holder.append(qs["code"][0])
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"<h2>Auth complete. You can close this tab.</h2>")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"<h2>Auth failed - no code in callback.</h2>")

        def log_message(self, *args):
            pass  # suppress server logs

    server = HTTPServer(("localhost", port), CallbackHandler)
    logger.info("[auth] Waiting for OAuth callback on port %d ...", port)
    server.handle_request()  # handles exactly one request then exits

    if not code_holder:
        raise RuntimeError("OAuth callback received no authorization code")

    return code_holder[0]


def get_oauth_token() -> str:
    """
    Returns a valid OAuth access token.
    Priority:
      1. Cached token file (if not expired)
      2. LINKEDIN_OAUTH_TOKEN env var (if set manually)
      3. Full browser OAuth flow (first-time setup)
    """
    # 1. cache
    cached = _load_cached_token()
    if cached:
        logger.info("[auth] Using cached OAuth token")
        return cached["access_token"]

    # 2. env var (manual paste)
    env_token = os.environ.get("LINKEDIN_OAUTH_TOKEN", "").strip()
    if env_token:
        logger.info("[auth] Using OAuth token from env var")
        return env_token

    # 3. browser flow
    redirect_uri = os.environ.get(
        "LINKEDIN_REDIRECT_URI", "http://localhost:8000/callback"
    )
    code = _run_local_oauth_flow(redirect_uri)
    token_data = _exchange_code_for_token(code, redirect_uri)
    _save_token(token_data)
    return token_data["access_token"]
