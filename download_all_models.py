"""
Master script to download all Hugging Face models required by the CyberHackerOS Factory PRD.
Uses the custom robust HTTP downloader to survive severe network conditions.
"""

import os
import sys

from scripts.robust_downloader import download_repo_robustly

# Base directory for all downloaded models
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "models"))

# Define the models required by the PRD
MODELS_TO_DOWNLOAD = [
    {
        "repo_id": "vidore/colqwen2-v1.0",
        "description": "Visual Indexing Model (ColPali/ColQwen2)",
    },
    {
        "repo_id": "Qwen/Qwen2.5-7B-Instruct",
        "description": "Primary Text LLM (Knowledge & Scenario Generation)",
    },
    {
        "repo_id": "Qwen/Qwen2.5-VL-7B-Instruct",
        "description": "Primary VLM (Full-Page Extraction & Routing)",
    },
]


def main() -> int:
    print(f"Models will be saved to: {MODELS_DIR}")
    os.makedirs(MODELS_DIR, exist_ok=True)

    success_all = True
    for model in MODELS_TO_DOWNLOAD:
        repo_id = model["repo_id"]
        desc = model["description"]
        print(f"\nDownloading: {desc} ({repo_id})")

        # Save each model in its own subdirectory
        local_dir = os.path.join(MODELS_DIR, repo_id.replace("/", "--"))

        if not download_repo_robustly(repo_id, local_dir):
            print(f"[ERROR] Failed to completely download {repo_id}")
            success_all = False

    if success_all:
        print("\n[SUCCESS] All models downloaded successfully.")
        return 0
    else:
        print("\n[ERROR] Some models failed to download. Rerun the script to resume.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
