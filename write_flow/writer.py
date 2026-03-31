"""
write_flow/writer.py
--------------------
Orchestrator (Controller facade) for all write operations.
Ties together auth and service logic.
"""

import logging
from pathlib import Path
from typing import Union

from .auth import get_oauth_token
from .clients.linkedin_client import LinkedInAPIError, LinkedInClient
from .services.post_service import PostService

logger = logging.getLogger(__name__)


class WriteFlow:
    """
    Single entry point for all LinkedIn write operations.
    Initialises once, call methods as needed.
    """

    def __init__(self):
        logger.info("[WriteFlow] Initialising write clients ...")

        # Provide Auth Token
        self._oauth_token = get_oauth_token()

        # Initialize Repository Layer
        self._linkedin_client = LinkedInClient(self._oauth_token)

        # Fetch current User URN (with automatic retries via the client)
        self._author_urn = self._fetch_user_urn()
        logger.info(f"[WriteFlow] OAuth ready — author URN: {self._author_urn}")

        # Initialize Service Layer
        self._post_service = PostService(self._linkedin_client)

    def _fetch_user_urn(self) -> str:
        """Fetches the authenticated user's URN via the robust client."""
        resp = self._linkedin_client.get("userinfo")
        sub = resp.json().get("sub", "")
        if not sub:
            raise LinkedInAPIError(
                "Could not retrieve 'sub' field from userinfo response."
            )
        return f"urn:li:person:{sub}"

    def publish_post(self, text: str, visibility: str = "PUBLIC") -> dict:
        """
        Publish a text post.
        """
        return self._post_service.publish_text_post(
            author_urn=self._author_urn,
            text=text,
            visibility=visibility,
        )

    def publish_image_post(self, text: str, image_path: Union[Path, str], visibility: str = "PUBLIC") -> dict:
        """
        Publish a post containing an image by executing the strict 3-step upload protocol.
        """
        # Strictly enforce pathlib.Path within the core services for cross-platform determinism
        image_file = Path(image_path) if isinstance(image_path, str) else image_path
        
        return self._post_service.publish_image_post(
            author_urn=self._author_urn,
            text=text,
            image_path=image_file,
            visibility=visibility,
        )
