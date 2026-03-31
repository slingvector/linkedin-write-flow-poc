import logging

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class LinkedInAPIError(Exception):
    """Custom exception for LinkedIn API failures."""



class LinkedInClient:
    """Repository Layer for interacting with the official LinkedIn API."""

    BASE_URL = "https://api.linkedin.com/v2"

    def __init__(self, oauth_token: str):
        self.oauth_token = oauth_token
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.oauth_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            }
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (requests.ConnectionError, requests.Timeout, requests.HTTPError)
        ),
    )
    def post(self, endpoint: str, json_data: dict) -> requests.Response:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        logger.info(f"[LinkedInClient] POST {url}")
        resp = self.session.post(url, json=json_data, timeout=10)

        # Only retry on 5xx server errors, not 4xx client errors
        if resp.status_code >= 500:
            resp.raise_for_status()

        if not resp.ok:
            error_body = resp.text
            try:
                error_body = resp.json()
            except Exception:
                pass
            raise LinkedInAPIError(f"API Error ({resp.status_code}): {error_body}")

        return resp

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (requests.ConnectionError, requests.Timeout, requests.HTTPError)
        ),
    )
    def get(self, endpoint: str) -> requests.Response:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        logger.info(f"[LinkedInClient] GET {url}")
        resp = self.session.get(url, timeout=10)

        if resp.status_code >= 500:
            resp.raise_for_status()

        if not resp.ok:
            try:
                error_body = resp.json()
            except Exception:
                error_body = resp.text
            raise LinkedInAPIError(f"API Error ({resp.status_code}): {error_body}")

        return resp

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (requests.ConnectionError, requests.Timeout, requests.HTTPError)
        ),
    )
    def put_binary(self, upload_url: str, binary_data: bytes) -> requests.Response:
        logger.info(f"[LinkedInClient] PUT (binary) {upload_url}")

        # Bypass self.session to avoid sending Authorization / JSON headers to the signed AWS/Azure blob URLs
        resp = requests.put(upload_url, data=binary_data, timeout=60)

        if resp.status_code >= 500:
            resp.raise_for_status()

        if not resp.ok:
            try:
                error_body = resp.json()
            except Exception:
                error_body = resp.text
            raise LinkedInAPIError(f"API Error ({resp.status_code}): {error_body}")

        return resp
