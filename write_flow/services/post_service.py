import logging
from pathlib import Path
from typing import Optional

from ..clients.linkedin_client import LinkedInAPIError, LinkedInClient

logger = logging.getLogger(__name__)


class PostService:
    """Service layer for managing LinkedIn posts (creating, formatting, publishing)."""

    def __init__(self, linkedin_client: LinkedInClient):
        self.client = linkedin_client

    def publish_text_post(
        self, author_urn: str, text: str, visibility: str = "PUBLIC"
    ) -> dict:
        """
        Creates and immediately publishes a text post on LinkedIn.
        """
        payload = {
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

        logger.info(
            f"[PostService] Publishing post ({len(text)} chars, visibility={visibility})"
        )

        try:
            resp = self.client.post("ugcPosts", json_data=payload)
            post_id = resp.headers.get("X-RestLi-Id", "")
            post_url = self._build_post_url(post_id) if post_id else None

            logger.info(f"[PostService] Published successfully — id: {post_id}")

            return {
                "success": True,
                "post_id": post_id,
                "post_url": post_url,
                "error": None,
            }
        except LinkedInAPIError as exc:
            logger.error(f"[PostService] Failed to publish post: {exc}")
            return {
                "success": False,
                "post_id": None,
                "post_url": None,
                "error": str(exc),
            }

    def _register_image_upload(self, author_urn: str) -> dict:
        """Registers an image upload against LinkedIn returning the upload URL and internal asset URN."""
        payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": author_urn,
                "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]
            }
        }
        resp = self.client.post("assets?action=registerUpload", json_data=payload)
        data = resp.json()
        
        asset = data["value"]["asset"]
        upload_url = data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        
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

    def publish_image_post(self, author_urn: str, text: str, image_path: Path, visibility: str = "PUBLIC") -> dict:
        """
        Executes the 3-step media upload sequence:
        1. Register upload to get asset URN and Upload URL.
        2. Upload binary payload directly to Upload URL.
        3. Publish final post metadata anchoring the Asset.
        """
        try:
            logger.info("[PostService] Step 1: Registering media upload...")
            upload_registration = self._register_image_upload(author_urn)
            asset_urn = upload_registration["asset_urn"]
            upload_url = upload_registration["upload_url"]
            
            logger.info("[PostService] Step 2: Uploading image binary...")
            self._upload_binary_data(upload_url, image_path)
            
            logger.info("[PostService] Step 3: Publishing post payload...")
            payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text,
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {"text": "Image uploaded via WriteFlow automation"},
                                "media": asset_urn,
                                "title": {"text": image_path.name}
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility,
                },
            }

            resp = self.client.post("ugcPosts", json_data=payload)
            post_id = resp.headers.get("X-RestLi-Id", "")
            post_url = self._build_post_url(post_id) if post_id else None
            
            logger.info(f"[PostService] Image Post Published successfully — id: {post_id}")
            
            return {
                "success": True,
                "post_id": post_id,
                "post_url": post_url,
                "error": None,
            }

        except Exception as exc:
            logger.error(f"[PostService] Failed to publish image post: {exc}")
            return {
                "success": False,
                "post_id": None,
                "post_url": None,
                "error": str(exc),
            }

    def _build_post_url(self, post_id: str) -> Optional[str]:
        """Converts a URN activity ID into a browsable LinkedIn URL."""
        if not post_id:
            return None
        return f"https://www.linkedin.com/feed/update/{post_id}/"
