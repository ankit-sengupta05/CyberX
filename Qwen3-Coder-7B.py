"""
Resumable downloader for Qwen2.5-Coder-7B (or any HF repo).

Key idea: huggingface_hub's snapshot_download() ALREADY does chunked,
resumable downloads under the hood (it downloads into the HF cache using
range-requests, and since huggingface_hub >= 0.23 the local_dir download
path also resumes partial files automatically). You don't need manual
cache-recovery hacks or the old resume_download / local_dir_use_symlinks
flags -- both are deprecated and now no-ops.

So the whole "resumable" problem reduces to: catch every kind of failure
(network drop, HTTP error, Ctrl+C) and just call snapshot_download again.
Every retry picks up exactly where it left off, file by file.
"""

import os
import sys
import time
from pathlib import Path

from huggingface_hub import snapshot_download
from huggingface_hub.utils import HfHubHTTPError
from requests.exceptions import ConnectionError, Timeout, ChunkedEncodingError

# ========== CONFIG ==========
MODEL_NAME = "Qwen/Qwen2.5-Coder-7B"
SAVE_DIR = r"C:\SDE Projects\CyberHackerOS\root_llm"

MAX_RETRIES = 100  # network can drop many times over a large download
RETRY_WAIT_SECONDS = 20  # base backoff
MAX_WORKERS = 4  # parallel file downloads; drop to 1 on very flaky links

# Optional: fine-tuning usually doesn't need every file in the repo.
# Uncomment to skip .bin duplicates if the repo ships both .bin and .safetensors,
# or to skip GGUF/quantized variants you don't need.
# ALLOW_PATTERNS = ["*.json", "*.safetensors", "*.txt", "*.model", "tokenizer*"]
ALLOW_PATTERNS = None

os.makedirs(SAVE_DIR, exist_ok=True)

# Optional speed boost: pip install hf_transfer, then this env var turns on
# a faster Rust-based transfer backend. Safe to leave on; falls back silently
# if the package isn't installed on older versions.
os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "1")


def download_with_resume() -> bool:
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            path = snapshot_download(
                repo_id=MODEL_NAME,
                local_dir=SAVE_DIR,
                max_workers=MAX_WORKERS,
                allow_patterns=ALLOW_PATTERNS,
            )
            print(f"\nDownload complete: {path}")
            return True

        except KeyboardInterrupt:
            print(
                "\nStopped by user (Ctrl+C). Partial files are safe on disk — "
                "just rerun this script to resume from where you left off."
            )
            return False

        except (HfHubHTTPError, ConnectionError, Timeout, ChunkedEncodingError) as e:
            attempt += 1
            wait = min(RETRY_WAIT_SECONDS * attempt, 300)  # backoff, capped at 5 min
            print(f"[ERROR] attempt {attempt}/{MAX_RETRIES}: {e}")
            print(f"Retrying in {wait}s...")
            time.sleep(wait)

        except Exception as e:
            # Catch-all so a weird transient error doesn't kill the whole run
            attempt += 1
            print(f"[UNEXPECTED ERROR] attempt {attempt}/{MAX_RETRIES}: {e}")
            time.sleep(RETRY_WAIT_SECONDS)

    print("Max retries reached. Rerun the script later to keep resuming.")
    return False


def verify(save_dir: str) -> None:
    print(f"\n{'='*60}")
    print("Verifying local files...")
    print(f"{'='*60}")
    local_files = [f for f in Path(save_dir).rglob("*") if f.is_file()]
    total_size = sum(f.stat().st_size for f in local_files) / (1024**3)
    print(f"Files in {save_dir}: {len(local_files)}")
    print(f"Total size: {total_size:.2f} GB")

    critical = ["config.json", "tokenizer.json", "tokenizer_config.json"]
    for c in critical:
        found = any(f.name == c for f in local_files)
        print(f"  [{'OK' if found else 'MISSING'}] {c}")

    # Check for any .incomplete leftovers, which mean a file is still partial
    incomplete = [f for f in local_files if f.suffix == ".incomplete"]
    if incomplete:
        print(
            f"\n{len(incomplete)} file(s) still incomplete — rerun the script to finish them:"
        )
        for f in incomplete:
            print(f"  - {f.name}")


if __name__ == "__main__":
    ok = download_with_resume()
    verify(SAVE_DIR)
    sys.exit(0 if ok else 1)
