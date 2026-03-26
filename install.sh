#!/usr/bin/env bash
set -euo pipefail

LOTUS_REPO="EhlOps/lotus"
MINIMUM_PYTHON="3.11"

echo "=== Lotus Installer ==="

# ── Check Python ──
if ! command -v python3 &>/dev/null; then
    echo "Error: Python 3 is required. Install it first:"
    echo "  macOS:  brew install python@3.12"
    echo "  Ubuntu: sudo apt install python3.12 python3.12-venv"
    exit 1
fi

PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
MIN_MINOR=$(echo "$MINIMUM_PYTHON" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt "$MIN_MINOR" ]; }; then
    echo "Error: Python >= ${MINIMUM_PYTHON} required. Found ${PY_VERSION}."
    exit 1
fi
echo "✓ Python ${PY_VERSION}"

# ── Check gh CLI ──
if ! command -v gh &>/dev/null; then
    echo "Error: GitHub CLI (gh) is required."
    echo "  Install: https://cli.github.com/"
    exit 1
fi

if ! gh auth status &>/dev/null 2>&1; then
    echo "Error: gh CLI is not authenticated. Run: gh auth login"
    exit 1
fi
echo "✓ GitHub CLI authenticated"

# ── Check git ──
if ! command -v git &>/dev/null; then
    echo "Error: git is required."
    exit 1
fi
echo "✓ git"

# ── Install via pip ──
# Prefer system Python's pip over any activated venv to avoid stale pip versions.
if [ -n "${VIRTUAL_ENV:-}" ]; then
    PIP="$VIRTUAL_ENV/../../../bin/pip3"
    [ -x "$PIP" ] || PIP=$(command -v pip3 || command -v pip)
else
    PIP=$(command -v pip3 || command -v pip)
fi

if [ -z "$PIP" ]; then
    echo "Error: pip required."
    exit 1
fi

echo "Upgrading pip..."
"$PIP" install --upgrade pip --break-system-packages 2>/dev/null || "$PIP" install --upgrade pip

echo "Installing Lotus via pip..."
"$PIP" install "git+https://github.com/${LOTUS_REPO}.git" --break-system-packages 2>/dev/null \
  || "$PIP" install "git+https://github.com/${LOTUS_REPO}.git"
echo "✓ Lotus installed via pip"

# ── Verify ──
if command -v lotus &>/dev/null; then
    echo ""
    echo "✓ Lotus $(lotus --version) installed successfully."
    echo ""
    echo "Next: cd into your project repo and run:"
    echo "  lotus init"
else
    echo ""
    echo "⚠ Lotus installed but 'lotus' command not found on PATH."
    echo "  If you used pip, try: python3 -m lotus --help"
    echo "  Or add ~/.local/bin to your PATH."
fi