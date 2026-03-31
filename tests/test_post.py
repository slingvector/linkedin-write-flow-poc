from unittest.mock import MagicMock


from write_flow.clients.linkedin_client import LinkedInAPIError, LinkedInClient
from write_flow.services.post_service import PostService


def test_api_client_success(mocker):
    # Test LinkedInClient raw success
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.ok = True

    mocker.patch("requests.Session.post", return_value=mock_resp)
    client = LinkedInClient("fake_token")
    resp = client.post("test", {"data": 1})
    assert resp.status_code == 200


def test_post_service_success(mocker):
    # Test PostService publishes correctly
    mock_resp = MagicMock()
    mock_resp.headers = {"X-RestLi-Id": "urn:li:ugcPost:12345"}

    mocker.patch(
        "write_flow.clients.linkedin_client.LinkedInClient.post", return_value=mock_resp
    )
    client = LinkedInClient("fake_token")
    service = PostService(client)

    result = service.publish_text_post("urn:li:person:123", "Hello world")
    assert result["success"] is True
    assert result["post_id"] == "urn:li:ugcPost:12345"
    assert (
        result["post_url"]
        == "https://www.linkedin.com/feed/update/urn:li:ugcPost:12345/"
    )


def test_post_service_failure(mocker):
    mocker.patch(
        "write_flow.clients.linkedin_client.LinkedInClient.post",
        side_effect=LinkedInAPIError("Unauthorized"),
    )
    client = LinkedInClient("fake_token")
    service = PostService(client)

    result = service.publish_text_post("urn:li:person:123", "Hello world")
    assert result["success"] is False
    assert "Unauthorized" in result["error"]

def test_publish_image_post_success(mocker, tmp_path):
    # Setup mock image file
    mock_img = tmp_path / "test.jpg"
    mock_img.write_bytes(b"dummy")

    # Mock client POST (register upload AND publish post both hit POST)
    def mock_post_side_effect(endpoint, json_data):
        resp = MagicMock()
        if "action=registerUpload" in endpoint:
            resp.json.return_value = {
                "value": {
                    "asset": "urn:li:digitalmediaAsset:123",
                    "uploadMechanism": {
                        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest": {
                            "uploadUrl": "https://upload.url"
                        }
                    }
                }
            }
        else:
            resp.headers = {"X-RestLi-Id": "urn:li:ugcPost:999"}
        return resp

    mocker.patch("write_flow.clients.linkedin_client.LinkedInClient.post", side_effect=mock_post_side_effect)
    mocker.patch("write_flow.clients.linkedin_client.LinkedInClient.put_binary")
    
    client = LinkedInClient("fake_token")
    service = PostService(client)
    
    result = service.publish_image_post("urn:li:person:123", "Hello", mock_img)
    assert result["success"] is True
    assert result["post_id"] == "urn:li:ugcPost:999"
