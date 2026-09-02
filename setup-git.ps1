[CmdletBinding()]
param(
    [switch]$SkipRemotePrompt
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Section {
    param([string]$Message)
    Write-Host ""
    Write-Host $Message -ForegroundColor Cyan
}

function Set-Utf8NoBom {
    param(
        [Parameter(Mandatory = $true)] [string]$Path,
        [Parameter(Mandatory = $true)] [string]$Content
    )

    $fullPath = if ([System.IO.Path]::IsPathRooted($Path)) {
        $Path
    }
    else {
        Join-Path $ProjectRoot $Path
    }

    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($fullPath, $Content, $utf8NoBom)
}

function Test-CommandAvailable {
    param([Parameter(Mandatory = $true)] [string]$Name)

    try {
        & $Name --version *> $null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Ensure-Directory {
    param([Parameter(Mandatory = $true)] [string]$Path)
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Ensure-FileContent {
    param(
        [Parameter(Mandatory = $true)] [string]$RelativePath,
        [Parameter(Mandatory = $true)] [string]$Content
    )

    if (-not (Test-Path $RelativePath)) {
        Set-Utf8NoBom -Path $RelativePath -Content $Content
        Write-Host "[OK] Created $RelativePath" -ForegroundColor Green
    }
    else {
        Write-Host "[OK] Existing $RelativePath preserved." -ForegroundColor Green
    }
}

$ProjectRoot = (Get-Location).Path

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "        UNIVERSAL GIT + SECURITY PIPELINE SETUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] Project root: $ProjectRoot" -ForegroundColor Gray

# 1. Verify Git and initialize repository if needed
$RepoWasJustInitialized = $false
if (-not (Test-Path ".git")) {
    Write-Section "[INFO] Initializing Git repository..."
    git init | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Git initialization failed."
    }
    $RepoWasJustInitialized = $true
    Write-Host "[OK] Git repository initialized." -ForegroundColor Green
}
else {
    Write-Host "[OK] Git repository already exists." -ForegroundColor Green
}

if (-not (Test-CommandAvailable -Name "git")) {
    throw "Git is not installed or not available in PATH."
}
Write-Host "[OK] Git detected." -ForegroundColor Green

# 2. Configure remote if missing
$oldPref = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$ExistingRemote = git remote get-url origin 2>$null
$ErrorActionPreference = $oldPref
if (-not $ExistingRemote -and -not $SkipRemotePrompt) {
    Write-Section "[INFO] No origin remote is configured."
    $RemoteUrl = Read-Host "Enter the remote repository URL (leave blank to skip)"
    if ($RemoteUrl -and $RemoteUrl.Trim() -ne "") {
        git remote add origin $RemoteUrl.Trim() | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[WARN] Failed to add remote. You can add it manually later." -ForegroundColor Yellow
        }
        else {
            Write-Host "[OK] Remote 'origin' set." -ForegroundColor Green
        }
    }
    else {
        Write-Host "[INFO] Remote setup skipped. Add it later with: git remote add origin <url>" -ForegroundColor Gray
    }
}
elseif ($ExistingRemote) {
    Write-Host "[OK] Remote 'origin' already set: $ExistingRemote" -ForegroundColor Green
}
else {
    Write-Host "[INFO] Remote setup skipped by parameter." -ForegroundColor Gray
}

# 3. Detect Python
$PythonCommand = $null
foreach ($candidate in @("python", "py")) {
    if (Test-CommandAvailable -Name $candidate) {
        $PythonCommand = $candidate
        break
    }
}

if (-not $PythonCommand) {
    throw "Python 3 is required. Install Python 3.10+ and ensure 'python' or 'py' is available."
}
Write-Host "[OK] Python detected: $PythonCommand" -ForegroundColor Green

# 4. Install Python tooling
Write-Section "[INFO] Installing Git and security tooling..."
& $PythonCommand -m pip install --user --disable-pip-version-check `
    "pre-commit==3.7.0" `
    "codespell==2.2.2"
if ($LASTEXITCODE -ne 0) {
    throw "Tool installation failed."
}
Write-Host "[OK] Python tooling installed." -ForegroundColor Green

# 5. Enable Git LFS globally and locally
$gitLfsInstalled = $false
try {
    git lfs version *> $null
    if ($LASTEXITCODE -eq 0) {
        $gitLfsInstalled = $true
    }
}
catch {}

if (-not $gitLfsInstalled) {
    Write-Host "[WARN] Git LFS is not installed. Please install Git LFS and rerun the script." -ForegroundColor Yellow
}
else {
    git lfs install --local | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Git LFS initialization failed."
    }
    Write-Host "[OK] Git LFS enabled for this repository." -ForegroundColor Green
}

# 6. Create directories
Ensure-Directory ".github/workflows"
Ensure-Directory "scripts"

$HooksDir = [System.IO.Path]::Combine($env:USERPROFILE, ".githooks", "autogo")
Ensure-Directory $HooksDir

# 6. Configure Git to use a hooks directory without spaces in the path
$legacyHookPath = Join-Path $ProjectRoot ".git/hooks/pre-push"
$legacyLegacyHookPath = Join-Path $ProjectRoot ".git/hooks/pre-push.legacy"
if (Test-Path $legacyHookPath) {
    Remove-Item $legacyHookPath -Force
}
if (Test-Path $legacyLegacyHookPath) {
    Remove-Item $legacyLegacyHookPath -Force
}

& git config --global core.hooksPath $HooksDir | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Failed to configure global Git hooks path."
}
& git config --local core.hooksPath $HooksDir | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Failed to configure local Git hooks path."
}
Write-Host "[OK] Git hooks path configured to $HooksDir" -ForegroundColor Green

# 7. Create environment files
$envContent = @'
# Local environment variables
# NEVER commit this file. Copy values from .env.example and fill them in.

'@
Ensure-FileContent -RelativePath ".env" -Content $envContent

$envExampleContent = @'
# Example environment variables
# Safe to commit. Replace placeholders with real values locally.

# APP_ENV=development
# API_BASE_URL=
# API_KEY=
# DATABASE_URL=
'@
Ensure-FileContent -RelativePath ".env.example" -Content $envExampleContent

# 7. Create Git ignore rules
$gitignoreContent = @'
# Environment / secrets
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx
*.crt

# Python
__pycache__/
**/__pycache__/
*.py[cod]
*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
.venv/
venv/
env/

# Node
node_modules/
**/node_modules/
.npm/
.yarn/
.pnpm-store/
*.log

# Framework build outputs
.next/
.nuxt/
dist/
build/
out/
.cache/
.vite/
.expo/
.expo-shared/
.metro-health-check*
.dart_tool/
.flutter-plugins
.flutter-plugins-dependencies
.packages
.pub-cache/
.gradle/
*.class
*.jar
*.war
*.apk
*.aab
captures/

# Native / compiled artifacts
*.o
*.obj
*.so
*.dll
*.exe
*.out

# Rust / Go
/target/
/vendor/

# IDE / OS
.vscode/*
!.vscode/settings.json
!.vscode/extensions.json
.idea/
*.iml
.DS_Store
Thumbs.db
desktop.ini

# Temporary files
tmp/
temp/
*.tmp
*.bak
*.swp
'@
Ensure-FileContent -RelativePath ".gitignore" -Content $gitignoreContent

# 8. Create .gitattributes for normalized line endings
$gitattributesContent = @'
* text=auto eol=lf

*.ps1 text eol=crlf
*.bat text eol=crlf
*.cmd text eol=crlf

*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.webp binary
*.ico binary
*.pdf binary

# Large media files should be stored with Git LFS
*.avi filter=lfs diff=lfs merge=lfs -text
*.mp4 filter=lfs diff=lfs merge=lfs -text
*.mov filter=lfs diff=lfs merge=lfs -text
*.mkv filter=lfs diff=lfs merge=lfs -text
*.zip filter=lfs diff=lfs merge=lfs -text
'@
Ensure-FileContent -RelativePath ".gitattributes" -Content $gitattributesContent

# 9. Create pre-commit configuration
$preCommitConfig = @"
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: check-added-large-files
        args: ["--maxkb=20000"]
      - id: check-json
      - id: check-yaml
      - id: check-case-conflict
      - id: mixed-line-ending
        args: ["--fix=lf"]
      - id: detect-private-key

  - repo: https://github.com/codespell-project/codespell
    rev: v2.2.2
    hooks:
      - id: codespell
        args: ["--skip=*.lock,*.min.js,*.map"]

  - repo: local
    hooks:
      - id: repo-secret-scan
        name: repo-secret-scan
        entry: python scripts/scan_secrets.py
        language: system
        pass_filenames: false
"@
Ensure-FileContent -RelativePath ".pre-commit-config.yaml" -Content $preCommitConfig

# 10. Create secret scan script
$scanSecretsContent = @'
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
    except Exception:
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
'@
Ensure-FileContent -RelativePath "scripts/scan_secrets.py" -Content $scanSecretsContent

# 12. Create a Windows-safe pre-push hook
$HookPath = Join-Path $HooksDir "pre-push"
$prePushHook = @'
#!/usr/bin/env sh
set -eu

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if command -v python >/dev/null 2>&1; then
    PYTHON=python
elif command -v py >/dev/null 2>&1; then
    PYTHON=py
else
    echo "Python not found." >&2
    exit 1
fi

echo ""
echo "Running full pre-push quality pipeline..."
echo ""

"$PYTHON" -m pre_commit run --all-files
"$PYTHON" scripts/scan_secrets.py
'@
Set-Utf8NoBom -Path $HookPath -Content $prePushHook
Write-Host "[OK] Created pre-push hook at $HookPath" -ForegroundColor Green

# 13. Install pre-commit hooks
Write-Section "[INFO] Installing git hooks..."
$PreCommitHookPath = Join-Path $HooksDir "pre-commit"
$preCommitHookContent = @'
#!/usr/bin/env sh
set -eu

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if command -v python >/dev/null 2>&1; then
    PYTHON=python
elif command -v py >/dev/null 2>&1; then
    PYTHON=py
else
    echo "Python not found." >&2
    exit 1
fi

exec "$PYTHON" -m pre_commit run
'@
Set-Utf8NoBom -Path $PreCommitHookPath -Content $preCommitHookContent
Write-Host "[OK] Git hooks installed." -ForegroundColor Green

# 14. Create GitHub Actions workflow
$qualityWorkflowContent = @'
name: Code Quality

on:
  push:
    branches:
      - "**"
  pull_request:
    branches:
      - "**"

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install tooling
        run: |
          python -m pip install --upgrade pip
          python -m pip install pre-commit codespell

      - name: Run pre-commit
        run: |
          python -m pre_commit run --all-files

      - name: Full repository secret scan
        run: |
          python scripts/scan_secrets.py
'@
Ensure-FileContent -RelativePath ".github/workflows/quality.yml" -Content $qualityWorkflowContent

# 15. Summary
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " SETUP COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  python -m pre_commit run --all-files" -ForegroundColor White
Write-Host "  python scripts/scan_secrets.py" -ForegroundColor White
Write-Host "  git add -A && git commit -m \"your message\"" -ForegroundColor White
Write-Host "  git push" -ForegroundColor White
Write-Host ""

if ($RepoWasJustInitialized -and -not $ExistingRemote) {
    Write-Host "Reminder: set a remote later with: git remote add origin <url>" -ForegroundColor Yellow
}

Write-Host "Done." -ForegroundColor Green
