# LinkedIn Write Flow 🚀

A highly resilient, SOLID-compliant Python orchestration package for safely publishing and automating content to LinkedIn via the official OAuth 2.0 API. 

## Features
- **Official API Integrity**: Bypasses brittle automated scraping (Voyager/li_at API) entirely by manually and strictly utilizing the official LinkedIn `v2` network graph.
- **SOLID Architecture**: Strict decoupling of logical concerns safely wrapped internally into an isolated HTTP Repository (`LinkedInClient`) and Business Rules engine (`PostService`).
- **Resilient & Fault Tolerant**: Built-in exponential backoff retries via `tenacity` natively catch, handle, and retry network timeouts safely without shutting down scripts.
- **Advanced Media Handling**: Natively interfaces with complex multi-domain 3-step Asset uploading protocols (AWS/Azure) so developers can seamlessly attach images and videos over the `ugcPosts` graph.
- **Production Observability**: Built-in structured JSON logging with injected distributed tracing IDs (`correlation_id`) securely tracking execution bounds.
- **Graceful Failure State**: Implements rigorous fail-fast input validation bounds and safe fallback handling preventing any mid-flight fatal crashes.

---

## 📖 User Guide
For complete documentation on Authentication, Exception Handling, Logging, and specific feature capabilities—please view the [docs/USER_GUIDE.md](docs/USER_GUIDE.md).

---

## 📦 Installation

Since the repository defines a fully structured Python application locally inside `setup.py`, you can instantly drop it directly into any other custom pipeline using pip!

```bash
pip install git+https://github.com/slingvector/linkedin-write-flow-poc.git
```

---

## ⚙️ Configuration

Your application relies exclusively on an active OAuth 2.0 token environment. You will need to build an `.env` authentication file exactly where you trigger your code:

```env
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_REDIRECT_URI=your_redirect_uri
```

*Note: The system intelligently caches the result silently inside a `.oauth_token_cache.json` securely hidden from your Git pushes so that repetitive prompts won't interrupt ongoing jobs.*

---

## 🛠️ Usage Example

The entire application runs behind an intuitive facade `WriteFlow`. Here is exactly how easy it is to securely interact natively with your timeline:

```python
from pathlib import Path
from write_flow.writer import WriteFlow

# Automatically bootstraps logic, resolves tokens natively, and registers your LinkedIn Author identity!
wf = WriteFlow()

# ----------------------------------------------
# 1. Publishing a standard Text Post
# ----------------------------------------------
result = wf.publish_post(
    text="Checking out my brand new automated LinkedIn Write Flow! 🚀"
)

print(result["success"]) # True
print(result["post_url"]) # https://www.linkedin.com/feed/update/urn:li:share:...

# ----------------------------------------------
# 2. Publishing a Complex Media Post
# ----------------------------------------------
img_path = Path("path/to/my/image.jpg")

result = wf.publish_image_post(
    text="Here is a visual snippet of today's work! 📸",
    image_path=img_path
)

print(result["success"]) # True

# ----------------------------------------------
# 3. Publishing a Video Post
# ----------------------------------------------
video_path = Path("path/to/demo.mp4")

result = wf.publish_video_post(
    text="Look at our brand new video walkthrough! 🎥",
    video_path=video_path
)

print(result["success"]) # True
```

---

## 🧪 Testing Constraints

All underlying business behaviors, exception triggers, and HTTP logic flows are securely boxed conceptually down by extensive mocking layers preventing unauthorized leakage to real networks! 

If you are expanding functionality:
```bash
# Verify architectural behaviors completely isolated across native mocks
PYTHONPATH=. pytest tests/
```
