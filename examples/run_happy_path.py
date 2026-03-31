import os
import sys
from pathlib import Path

# Add project root to path so we can import write_flow
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Important: ensure logging setup is triggered early to capture all events
from write_flow import WriteFlow

def run():
    print("Initializing WriteFlow (JSON structured logging will appear)...")
    writer = WriteFlow()
    
    media_dir = Path("media")
    test_image = media_dir / "test_image.jpg"
    test_video = media_dir / "test_video.mp4"
    
    # We will publish to "CONNECTIONS" to avoid spamming the public feed during tests.
    
    # 1. Text Post
    print("\n--- 1. Publishing Text Post ---")
    resp = writer.publish_post(
        text="Hello from WriteFlow! Running an automated integration test for a raw text post. 🚀", 
        visibility="CONNECTIONS"
    )
    print(f"Result: {resp}")
    
    # 2. Image Post
    if test_image.exists():
        print("\n--- 2. Publishing Image Post ---")
        resp = writer.publish_image_post(
            text="Hello from WriteFlow! Running an automated integration test for a post with image attachment. 📸", 
            image_path=test_image, 
            visibility="CONNECTIONS"
        )
        print(f"Result: {resp}")
    else:
        print(f"\nSkipping Image Post — missing {test_image}")
        
    # 3. Video Post
    if test_video.exists():
        print("\n--- 3. Publishing Video Post ---")
        resp = writer.publish_video_post(
            text="Hello from WriteFlow! Running an automated integration test for a post with video attachment. 🎥", 
            video_path=test_video, 
            visibility="CONNECTIONS"
        )
        print(f"Result: {resp}")
    else:
        print(f"\nSkipping Video Post — missing {test_video}")

if __name__ == "__main__":
    run()
