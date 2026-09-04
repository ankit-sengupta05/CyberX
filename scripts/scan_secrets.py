import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."

EXCLUDED_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "env",
    ".expo",
    ".dart_tool",
    "build",
    "dist",
    "target",
    "__pycache__",
    ".next",
    ".gradle",
    # Large data / model directories — scanning these would hang on multi-GB files
    "models",
    "input",
    "output",
    "datasets",
    "data",
    "checkpoints",
    "artifacts",
    "cache",
    ".cache",
    "logs",
}

EXCLUDED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".svg",
    ".mp4",
    ".mov",
    ".avi",
    ".zip",
    ".7z",
    ".rar",
    ".exe",
    ".dll",
    ".so",
    ".class",
    ".jar",
    ".o",
    ".obj",
    ".pyc",
    ".lock",
}

PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r"AIza[0-9A-Za-z_-]{35}", "Google API Key"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub Personal Access Token"),
    (r"-----BEGIN [A-Z ]+ PRIVATE KEY-----", "Private Key"),
    (
        r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|client[_-]?secret)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
        "Possible hardcoded credential",
    ),
]


def should_skip(path: str) -> bool:
    lower = path.lower()
    for directory in EXCLUDED_DIRS:
        marker = os.sep + directory.lower() + os.sep
        if marker in lower:
            return True
    return os.path.splitext(path)[1].lower() in EXCLUDED_EXTENSIONS


def scan_file(path: str):
    findings = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            content = handle.read()
    except Exception:  # noqa: BLE001
        return findings

    for pattern, name in PATTERNS:
        for match in re.finditer(pattern, content):
            line = content.count("\n", 0, match.start()) + 1
            findings.append((path, line, name))
    return findings


def main() -> int:
    findings = []
    for directory, subdirs, files in os.walk(ROOT):
        subdirs[:] = [d for d in subdirs if d not in EXCLUDED_DIRS]
        for filename in files:
            path = os.path.join(directory, filename)
            if should_skip(path):
                continue
            findings.extend(scan_file(path))

    if not findings:
        print("[OK] Full repository secret scan passed.")
        return 0

    print()
    print("=" * 70)
    print("POSSIBLE SECRETS FOUND")
    print("=" * 70)

    for path, line, name in findings:
        print(f"{path}:{line} -> {name}")

    print()
    print("Move real secrets to .env or another secure secret store.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
