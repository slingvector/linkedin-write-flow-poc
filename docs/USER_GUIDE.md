# WriteFlow User Guide

Welcome to the `linkedin-write-flow` v1.0 User Guide!

## 1. Authentication
The library uses OAuth 2.0 to authenticate on behalf of your LinkedIn user profile. 
You must provide the following environment variables (usually via a `.env` file at the root of your project):

- `LINKEDIN_CLIENT_ID`
- `LINKEDIN_CLIENT_SECRET`
- `LINKEDIN_REDIRECT_URI`

On first run, the system will prompt you in the terminal to visit an authorization URL and paste back the redirected code. The resulting token is cached locally in `.oauth_token_cache.json`.

## 2. Basic Usage

### Initialization
```python
from write_flow import WriteFlow

# The constructor automatically handles token resolution and lazy-loads your Author URN
writer = WriteFlow()
```

### Publishing Text
```python
response = writer.publish_post(
    text="Hello World!",
    visibility="PUBLIC" # or "CONNECTIONS"
)
```

### Publishing Images
```python
from pathlib import Path

response = writer.publish_image_post(
    text="Look at this picture!",
    image_path=Path("media/my_image.jpg"),
    visibility="CONNECTIONS"
)
```

### Publishing Videos
```python
response = writer.publish_video_post(
    text="Check out this video!",
    video_path="media/my_video.mp4",
    visibility="PUBLIC"
)
```

## 3. Graceful Error Handling
Unlike many scripts that crash when APIs fail, `WriteFlow` is designed for high-reliability pipelines.

Every publish method returns a dictionary of the exact same shape:
```python
{
    "success": bool,
    "post_id": str | None, # Generated urn:li:share or urn:li:ugcPost string
    "post_url": str | None, # Direct browser link
    "error": str | None # Readable message outlining the failure
}
```

If you provide invalid inputs (e.g., text > 3000 chars, empty text, invalid visibility enum, or missing files), the system will safely return `success: False` with the exact `error` reason **without making unnecessary API calls**.

If the LinkedIn API experiences a transient outage (5xx error), the native HTTP client will automatically retry using exponential backoff (via `tenacity`) before ultimately cascading into a clean `False` return state instead of crashing.

## 4. Observability & Logging
For production environments, `WriteFlow` emits structured JSON logs automatically. Every log entry includes a dynamically injected `correlation_id` allowing your DevOps team to trace requests precisely through the application stack. You do not need to configure complex logging infrastructure; this handles it directly interacting with STDOUT.
