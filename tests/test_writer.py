from unittest.mock import MagicMock


from write_flow.writer import WriteFlow


def test_write_flow_init(mocker):
    """Test WriteFlow orchestration initialization."""
    mocker.patch("write_flow.writer.get_oauth_token", return_value="token123")

    # Mock the client fetch response
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"sub": "123"}
    mocker.patch(
        "write_flow.clients.linkedin_client.LinkedInClient.get", return_value=mock_resp
    )

    wf = WriteFlow()
    assert wf._oauth_token == "token123"
    assert wf._author_urn == "urn:li:person:123"


def test_write_flow_publish_post(mocker):
    """Test WriteFlow.publish_post orchestration calls the service."""
    mocker.patch("write_flow.writer.get_oauth_token", return_value="token123")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"sub": "123"}
    mocker.patch(
        "write_flow.clients.linkedin_client.LinkedInClient.get", return_value=mock_resp
    )

    mock_create = mocker.patch(
        "write_flow.services.post_service.PostService.publish_text_post",
        return_value={"success": True},
    )

    wf = WriteFlow()
    result = wf.publish_post("Hi")
    assert result["success"] is True
    mock_create.assert_called_once_with(
        author_urn="urn:li:person:123", text="Hi", visibility="PUBLIC"
    )
