"""
Downloads raw Hugging Face models into:

    <ROOT>/llms/<model_name>/

where <model_name> is the repo id with "/" replaced by "__"
(e.g. "vidore/colqwen2-v1.0" -> "llms/vidore__colqwen2-v1.0/").

This covers models you need as RAW WEIGHTS (not GGUF), i.e.:
  - ColPali / ColQwen2 (visual embedder — no GGUF support exists)
  - Qwen2.5 base model for fine-tuning (training needs safetensors, not GGUF)

GGUF models (generation/critic/routing LLMs run through LM Studio) are
handled separately — see the note at the bottom of this file, since those
are pulled by LM Studio itself, not this script.

Requires:
    pip install huggingface_hub
"""

import logging
import os
import time
from pathlib import Path

from huggingface_hub import snapshot_download
from huggingface_hub.utils import HfHubHTTPError
from requests.exceptions import ChunkedEncodingError, ConnectionError, Timeout

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Set your root here. Use an absolute path so this works regardless of
# which directory you run the script from.
# ---------------------------------------------------------------------------
ROOT = Path(r"C:\llms")  # Windows example
# ROOT = Path("/home/you/llms")  # Linux example

MODELS_TO_DOWNLOAD = [
    "vidore/colqwen2-v1.0",  # visual page embedder
    "Qwen/Qwen2.5-Coder-7B-Instruct",  # fine-tuning base — coder variant, better tool/command fidelity
    # add more repo ids here
]

MAX_RETRIES = 8
BASE_BACKOFF_SECONDS = 10  # doubles each retry: 10, 20, 40, 80... capped below
MAX_BACKOFF_SECONDS = 300

# hf_transfer gives much faster, more reliable multi-threaded downloads with
# better resume behavior on large files. `pip install hf_transfer` then this
# env var turns it on automatically for every download below.
os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "1")

RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    ChunkedEncodingError,
    Timeout,
    HfHubHTTPError,  # covers transient 5xx / rate-limit responses from the Hub
)


def folder_name_for(repo_id: str) -> str:
    """vidore/colqwen2-v1.0 -> vidore__colqwen2-v1.0"""
    return repo_id.replace("/", "__")


def download_model(repo_id: str) -> Path:
    """
    Resumable download with automatic retry on transient failures.

    Resume itself is handled by snapshot_download: each file downloads into
    a `<file>.<hash>.incomplete` sidecar and, on re-invocation, continues
    from the last confirmed byte rather than restarting — this works whether
    the previous run ended by exception, Ctrl+C, power loss, or a killed
    process. The retry loop here just makes sure a transient network drop
    doesn't require YOU to be the one who notices and reruns it.
    """
    target_dir = ROOT / folder_name_for(repo_id)
    target_dir.mkdir(parents=True, exist_ok=True)

    attempt = 0
    while True:
        attempt += 1
        try:
            log.info(f"Downloading {repo_id} -> {target_dir}  (attempt {attempt})")
            snapshot_download(
                repo_id=repo_id,
                local_dir=target_dir,
                local_dir_use_symlinks=False,  # real files, not symlinks into the HF cache
                max_workers=4,  # parallel file downloads within the repo
                # revision="main",               # pin a specific commit/tag for reproducibility
                # token="hf_...",                # only needed for gated models
            )
            log.info(f"Done: {repo_id}")
            return target_dir

        except RETRYABLE_EXCEPTIONS as e:
            if attempt >= MAX_RETRIES:
                log.error(f"Giving up on {repo_id} after {attempt} attempts: {e}")
                raise
            backoff = min(
                BASE_BACKOFF_SECONDS * (2 ** (attempt - 1)), MAX_BACKOFF_SECONDS
            )
            log.warning(
                f"{repo_id}: transient error ({e!r}). Retrying in {backoff}s..."
            )
            time.sleep(backoff)

        except KeyboardInterrupt:
            log.warning(
                f"Interrupted by user. Progress for {repo_id} is saved — "
                f"just rerun the script to resume from where it left off."
            )
            raise


if __name__ == "__main__":
    ROOT.mkdir(parents=True, exist_ok=True)
    failed = []
    for repo_id in MODELS_TO_DOWNLOAD:
        try:
            download_model(repo_id)
        except Exception as e:  # noqa: BLE001
            log.error(f"Failed permanently: {repo_id} — {e}")
            failed.append(repo_id)

    if failed:
        log.warning(f"Rerun the script to retry these: {failed}")
    else:
        log.info("All models downloaded successfully.")

# ---------------------------------------------------------------------------
# For GGUF models (LM Studio):
# LM Studio does not go through this script — it manages its own downloads.
# To make LM Studio save into the SAME llms/ root instead of its default
# location:
#
#   LM Studio -> Settings (gear icon) -> "Models Directory" (or under the
#   "My Models" tab, top-right folder icon) -> point it at:
#
#       C:\llms
#
#   LM Studio will then create its own subfolder structure under that root
#   per publisher/model, e.g. C:\llms\lmstudio-community\Qwen2.5-7B-Instruct-GGUF\
#   which keeps everything under the same parent directory as the raw
#   HF downloads above, even though the internal naming convention differs
#   slightly (LM Studio uses publisher/repo, this script uses repo_id with
#   "__" substitution).
# ---------------------------------------------------------------------------
