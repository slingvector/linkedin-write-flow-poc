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
    missing_image = media_dir / "does_not_exist.jpg"
    
    print("\n=============================================")
    print("UNHAPPY PATH TESTS (EXPECTED FAILURES)")
    print("=============================================\n")

    # 1. Controller Validation: Empty Text
    print("--- 1. Testing Empty Text ---")
    resp = writer.publish_post(text="   ", visibility="CONNECTIONS")
    print(f"Result: {resp}\n")
    
    # 2. Controller Validation: Text > 3000 Chars
    print("--- 2. Testing Text Over 3000 Characters ---")
    massive_text = "A" * 3005
    resp = writer.publish_post(text=massive_text, visibility="CONNECTIONS")
    print(f"Result: {resp}\n")
    
    # 3. Controller Validation: Invalid Visibility
    print("--- 3. Testing Invalid Visibility Enum ---")
    resp = writer.publish_post(text="Valid text", visibility="SECRET_NETWORK")
    print(f"Result: {resp}\n")
    
    # 4. Service Layer Validation: Missing File (Image Step 2 Failure)
    print("--- 4. Testing Missing File Upload ---")
    resp = writer.publish_image_post(
        text="Valid text", 
        image_path=missing_image, 
        visibility="CONNECTIONS"
    )
    print(f"Result: {resp}\n")

if __name__ == "__main__":
    run()
