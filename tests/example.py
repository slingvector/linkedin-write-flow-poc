"""
example.py
----------
Shows how to securely wire your content generation engine into the write flow.
Now strictly structured adhering to SOLID principles with robust error handling.
"""

import logging

from write_flow.writer import WriteFlow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

GENERATED_POST_TEXT = """
Just shipped a new feature using Claude + Python 🚀

Refactored the architecture to be clean, scalable, and fully typed.
SOLID principles FTW!

#ai #python #llm #buildinpublic
""".strip()


def main():
    try:
        wf = WriteFlow()

        print("\n── Publishing post ─────────────────────")
        import time

        post_text = GENERATED_POST_TEXT + f"\n\n(Snapshot: {int(time.time())})"

        result = wf.publish_post(post_text)

        print(f"  Success  : {result['success']}")
        print(f"  Post URL : {result['post_url']}")
        if result["error"]:
            print(f"  Error    : {result['error']}")

    except Exception as e:
        logging.error(f"Application failed: {e}")


if __name__ == "__main__":
    main()
