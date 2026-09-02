"""
Robust, truly resumable Hugging Face model downloader.
Bypasses standard caching by executing manual HTTP Range requests directly to the target directory.
Guarantees continuation from the exact byte where it left off, regardless of network stability.
"""

import fnmatch
import os
import sys
import time

import requests
from huggingface_hub import HfApi, hf_hub_url


def is_allowed(filename: str, allow_patterns: list[str] | None) -> bool:
    if not allow_patterns:
        return True
    return any(fnmatch.fnmatch(filename, pat) for pat in allow_patterns)


def download_file_robustly(
    repo_id: str, filename: str, local_dir: str, max_retries: int = 10000
) -> bool:
    url = hf_hub_url(repo_id, filename)
    local_path = os.path.join(local_dir, filename)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    attempt = 0
    while attempt < max_retries:
        try:
            local_size = (
                os.path.getsize(local_path) if os.path.exists(local_path) else 0
            )

            # Get remote size
            head_resp = requests.head(url, allow_redirects=True, timeout=15)
            if head_resp.status_code == 404:
                print(f"[ERROR] File {filename} not found.")
                return False

            remote_size_str = head_resp.headers.get("content-length")
            remote_size = int(remote_size_str) if remote_size_str else None

            if remote_size is not None and local_size == remote_size:
                print(f"[OK] {filename} is already fully downloaded.")
                return True

            if remote_size is not None and local_size > remote_size:
                print(f"[WARN] Local file {filename} is larger than remote. Resetting.")
                os.remove(local_path)
                local_size = 0

            headers = {"Range": f"bytes={local_size}-"} if local_size > 0 else {}
            action = "Resuming" if local_size > 0 else "Starting"
            progress_pct = (local_size / remote_size * 100) if remote_size else 0
            print(
                f"[{action}] {filename} at {local_size} bytes ({progress_pct:.1f}%)..."
            )

            with requests.get(
                url, headers=headers, stream=True, allow_redirects=True, timeout=30
            ) as r:
                # If server ignores Range request, it returns 200 instead of 206
                if local_size > 0 and r.status_code == 200:
                    print(
                        f"[WARN] Server ignored Range request for {filename}. Restarting file."
                    )
                    open(local_path, "wb").close()
                    local_size = 0
                else:
                    r.raise_for_status()

                with open(local_path, "ab") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                            os.fsync(f.fileno())

            # Verify size
            final_size = os.path.getsize(local_path)
            if remote_size is not None and final_size != remote_size:
                raise ValueError(
                    f"Size mismatch after download: {final_size} != {remote_size}"
                )

            print(f"[SUCCESS] {filename} downloaded completely.")
            return True

        except KeyboardInterrupt:
            print("\n[STOPPED] Download stopped by user. Progress is saved safely.")
            sys.exit(1)
        except Exception as e:  # noqa: BLE001
            attempt += 1
            print(f"\n[NETWORK ERROR] {e}")
            print(f"Retrying in 5 seconds (Attempt {attempt}/{max_retries})...")
            time.sleep(5)

    print(f"[FAILED] Could not download {filename} after {max_retries} attempts.")
    return False


def download_repo_robustly(
    repo_id: str, local_dir: str, allow_patterns: list[str] | None = None
) -> bool:
    print(f"\n{'=' * 60}")
    print(f"Starting robust download for {repo_id}")
    print(f"Target directory: {local_dir}")
    print(f"{'=' * 60}")

    api = HfApi()
    try:
        all_files = api.list_repo_files(repo_id)
    except Exception as e:  # noqa: BLE001
        print(f"Failed to list repo {repo_id}: {e}")
        return False

    success = True
    for filename in all_files:
        if is_allowed(filename, allow_patterns) and not download_file_robustly(
            repo_id, filename, local_dir
        ):
            success = False

    if success:
        print(f"\n[COMPLETED] Entire repository {repo_id} successfully downloaded.")
    else:
        print(f"\n[WARNING] Some files in {repo_id} failed to download.")
    return success
