"""
write_flow/writer.py
--------------------
Orchestrator (Controller facade) for all write operations.
Ties together auth and service logic.
"""

import logging
import uuid
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

        # Lazy load Author URN
        self._author_urn = None
        logger.info("[WriteFlow] OAuth ready — lazy-loading author URN")

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

    @property
    def author_urn(self) -> str:
        """Lazy loads and returns the authenticated user's URN."""
        if self._author_urn is None:
            self._author_urn = self._fetch_user_urn()
        return self._author_urn

    def publish_post(self, text: str, visibility: str = "PUBLIC") -> dict:
        """
        Publish a text post.
        """
        correlation_id = str(uuid.uuid4())
        logger.info(
            "publish_post called",
            extra={"correlation_id": correlation_id, "char_count": len(text), "visibility": visibility, "layer": "controller"}
        )

        if not text or not text.strip():
            return {"success": False, "post_id": None, "post_url": None, "error": "Post text cannot be empty"}
        if len(text) > 3000:
            return {"success": False, "post_id": None, "post_url": None, "error": f"Post text exceeds 3000 char limit ({len(text)} chars)"}
        if visibility not in ("PUBLIC", "CONNECTIONS"):
            return {"success": False, "post_id": None, "post_url": None, "error": f"Invalid visibility: {visibility}"}

        return self._post_service.publish_text_post(
            author_urn=self.author_urn,
            text=text,
            visibility=visibility,
            correlation_id=correlation_id,
        )

    def publish_image_post(self, text: str, image_path: Union[Path, str], visibility: str = "PUBLIC") -> dict:
        """
        Publish a post containing an image by executing the strict 3-step upload protocol.
        """
        correlation_id = str(uuid.uuid4())
        image_file = Path(image_path) if isinstance(image_path, str) else image_path
        
        logger.info(
            "publish_image_post called",
            extra={
                "correlation_id": correlation_id,
                "char_count": len(text),
                "image_path": str(image_file),
                "visibility": visibility,
                "layer": "controller",
            }
        )

        if not text or not text.strip():
            return {"success": False, "post_id": None, "post_url": None, "error": "Post text cannot be empty"}
        if len(text) > 3000:
            return {"success": False, "post_id": None, "post_url": None, "error": f"Post text exceeds 3000 char limit ({len(text)} chars)"}
        if visibility not in ("PUBLIC", "CONNECTIONS"):
            return {"success": False, "post_id": None, "post_url": None, "error": f"Invalid visibility: {visibility}"}

        return self._post_service.publish_image_post(
            author_urn=self.author_urn,
            text=text,
            image_path=image_file,
            visibility=visibility,
            correlation_id=correlation_id,
        )

    def publish_video_post(self, text: str, video_path: Union[Path, str], visibility: str = "PUBLIC") -> dict:
        """
        Publish a post containing a video by executing the strict media upload protocol.
        """
        correlation_id = str(uuid.uuid4())
        video_file = Path(video_path) if isinstance(video_path, str) else video_path
        
        logger.info(
            "publish_video_post called",
            extra={
                "correlation_id": correlation_id,
                "char_count": len(text),
                "video_path": str(video_file),
                "visibility": visibility,
                "layer": "controller",
            }
        )

        if not text or not text.strip():
            return {"success": False, "post_id": None, "post_url": None, "error": "Post text cannot be empty"}
        if len(text) > 3000:
            return {"success": False, "post_id": None, "post_url": None, "error": f"Post text exceeds 3000 char limit ({len(text)} chars)"}
        if visibility not in ("PUBLIC", "CONNECTIONS"):
            return {"success": False, "post_id": None, "post_url": None, "error": f"Invalid visibility: {visibility}"}

        return self._post_service.publish_video_post(
            author_urn=self.author_urn,
            text=text,
            video_path=video_file,
            visibility=visibility,
            correlation_id=correlation_id,
        )
