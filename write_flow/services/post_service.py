import logging
import uuid
from pathlib import Path

from ..clients.linkedin_client import LinkedInAPIError
from ..clients.base import LinkedInClientProtocol

logger = logging.getLogger(__name__)


class PostService:
    """Service layer for managing LinkedIn posts (creating, formatting, publishing)."""

    def __init__(self, linkedin_client: LinkedInClientProtocol):
        self.client = linkedin_client

    def publish_text_post(
        self, author_urn: str, text: str, visibility: str = "PUBLIC", correlation_id: str = None
    ) -> dict:
        """
        Creates and immediately publishes a text post on LinkedIn.
        """
        correlation_id = correlation_id or str(uuid.uuid4())
        payload = self._build_text_payload(author_urn, text, visibility)

        logger.info(
            "Publishing text post",
            extra={
                "correlation_id": correlation_id,
                "author_urn": author_urn,
                "char_count": len(text),
                "visibility": visibility,
            }
        )

        try:
            resp = self.client.post("ugcPosts", json_data=payload)
            post_id = resp.headers.get("X-RestLi-Id", "")
            post_url = self._build_post_url(post_id) if post_id else None

            logger.info("Published successfully", extra={"correlation_id": correlation_id, "post_id": post_id})

            return {
                "success": True,
                "post_id": post_id,
                "post_url": post_url,
                "error": None,
            }
        except LinkedInAPIError as exc:
            logger.error("Failed to publish post", extra={"correlation_id": correlation_id, "error": str(exc), "author_urn": author_urn, "status_code": getattr(exc, 'status_code', None)})
            return {
                "success": False,
                "post_id": None,
                "post_url": None,
                "error": str(exc),
            }

    def _register_media_upload(self, author_urn: str, recipe: str) -> dict:
        """Registers a media upload against LinkedIn returning the upload URL and internal asset URN."""
        payload = {
            "registerUploadRequest": {
                "recipes": [recipe],
                "owner": author_urn,
                "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]
            }
        }
        resp = self.client.post("assets?action=registerUpload", json_data=payload)
        data = resp.json()
        
        try:
            asset = data["value"]["asset"]
            upload_url = data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        except KeyError as exc:
            raise KeyError(f"Unexpected LinkedIn response shape — missing key: {exc}")
            
        return {
            "asset_urn": asset,
            "upload_url": upload_url
        }

    def _upload_binary_data(self, upload_url: str, file_path: Path):
        """Reads file locally and PUTs binary to the temporary upload URL."""
        logger.info(f"[PostService] Uploading binary file: {file_path}")
        
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"Media file not found at path: {file_path}")
            
        with open(file_path, "rb") as f:
            binary_data = f.read()
            
        self.client.put_binary(upload_url, binary_data)

    def publish_image_post(self, author_urn: str, text: str, image_path: Path, visibility: str = "PUBLIC", correlation_id: str = None) -> dict:
        """Publishes a post with an attached image."""
        correlation_id = correlation_id or str(uuid.uuid4())
        return self._publish_media_post(
            author_urn=author_urn,
            text=text,
            media_path=image_path,
            recipe="urn:li:digitalmediaRecipe:feedshare-image",
            media_category="IMAGE",
            visibility=visibility,
            correlation_id=correlation_id
        )

    def publish_video_post(self, author_urn: str, text: str, video_path: Path, visibility: str = "PUBLIC", correlation_id: str = None) -> dict:
        """Publishes a post with an attached video."""
        correlation_id = correlation_id or str(uuid.uuid4())
        return self._publish_media_post(
            author_urn=author_urn,
            text=text,
            media_path=video_path,
            recipe="urn:li:digitalmediaRecipe:feedshare-video",
            media_category="VIDEO",
            visibility=visibility,
            correlation_id=correlation_id
        )

    def _publish_media_post(self, author_urn: str, text: str, media_path: Path, recipe: str, media_category: str, visibility: str, correlation_id: str) -> dict:
        """Executes the 3-step media upload sequence."""
        try:
            logger.info(f"{media_category} post step 1: Registering media upload...", extra={"correlation_id": correlation_id})
            upload_registration = self._register_media_upload(author_urn, recipe)
            asset_urn = upload_registration["asset_urn"]
            upload_url = upload_registration["upload_url"]
        except Exception as exc:
            logger.error(f"{media_category} post step 1 failed — upload registration", extra={"correlation_id": correlation_id, "error": str(exc)})
            return {
                "success": False,
                "post_id": None,
                "post_url": None,
                "error": f"Upload registration failed: {exc}",
            }
            
        try:
            logger.info(f"{media_category} post step 2: Uploading media binary...", extra={"correlation_id": correlation_id})
            self._upload_binary_data(upload_url, media_path)
        except (LinkedInAPIError, FileNotFoundError) as exc:
            logger.error(f"{media_category} post step 2 failed — binary upload", extra={"correlation_id": correlation_id, "error": str(exc)})
            return {
                "success": False,
                "post_id": None,
                "post_url": None,
                "error": f"Binary upload failed: {exc}",
            }
            
        try:
            logger.info(f"{media_category} post step 3: Publishing post payload...", extra={"correlation_id": correlation_id})
            payload = self._build_media_payload(author_urn, text, visibility, asset_urn, media_path.name, media_category)

            resp = self.client.post("ugcPosts", json_data=payload)
            post_id = resp.headers.get("X-RestLi-Id", "")
            post_url = self._build_post_url(post_id) if post_id else None
            
            logger.info(f"{media_category} Post Published successfully", extra={"correlation_id": correlation_id, "post_id": post_id})
            
            return {
                "success": True,
                "post_id": post_id,
                "post_url": post_url,
                "error": None,
            }

        except Exception as exc:
            logger.error(f"{media_category} post step 3 failed — publish media post", extra={"correlation_id": correlation_id, "error": str(exc)})
            return {
                "success": False,
                "post_id": None,
                "post_url": None,
                "error": f"Publish media post failed: {exc}",
            }

    def _build_text_payload(self, author_urn: str, text: str, visibility: str) -> dict:
        return {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text,
                    },
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility,
            },
        }

    def _build_media_payload(self, author_urn: str, text: str, visibility: str, asset_urn: str, media_name: str, media_category: str) -> dict:
        return {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text,
                    },
                    "shareMediaCategory": media_category,
                    "media": [
                        {
                            "status": "READY",
                            "description": {"text": f"{media_category.capitalize()} uploaded via WriteFlow automation"},
                            "media": asset_urn,
                            "title": {"text": media_name}
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility,
            },
        }

    def _build_post_url(self, post_id: str) -> Optional[str]:
        """Converts a URN activity ID into a browsable LinkedIn URL."""
        if not post_id:
            return None
        return f"https://www.linkedin.com/feed/update/{post_id}/"
