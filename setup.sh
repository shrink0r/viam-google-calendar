#!/bin/sh
set -eu

cd "$(dirname "$0")"

VENV_NAME="${VENV_NAME:-venv}"
PYTHON="$VENV_NAME/bin/python"
REQ_FILE="${REQ_FILE:-requirements.txt}"

ENV_ERROR="This module requires Python >= 3.10 and python3-venv (or equivalent) to be installed."

# --- Check Python version (>= 3.10) ---
if ! command -v python3 >/dev/null 2>&1; then
  echo "$ENV_ERROR" >&2
  exit 1
fi

PY_OK="$(python3 -c 'import sys; print(int(sys.version_info >= (3,10)))' 2>/dev/null || echo 0)"
if [ "$PY_OK" != "1" ]; then
  echo "$ENV_ERROR" >&2
  python3 -V >&2 || true
  exit 1
fi

# --- Create venv if missing ---
if [ ! -x "$PYTHON" ]; then
  if ! python3 -m venv "$VENV_NAME" >/dev/null 2>&1; then
    echo "Failed to create virtualenv. You may need to install python3-venv." >&2
    echo "$ENV_ERROR" >&2
    exit 1
  fi
fi

# --- Compute a fingerprint so we only reinstall when inputs change ---
# Uses sha256sum if available, else falls back to shasum; if neither exist, always install.
fingerprint() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    echo "NOHASH"
  fi
}

REQ_HASH="$(fingerprint "$REQ_FILE")"
PY_VER="$($PYTHON -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}")')"
STAMP_FILE="$VENV_NAME/.deps_stamp"
NEW_STAMP="py=$PY_VER req=$REQ_HASH"

OLD_STAMP=""
if [ -f "$STAMP_FILE" ]; then
  OLD_STAMP="$(cat "$STAMP_FILE" 2>/dev/null || true)"
fi

# --- Install deps if needed ---
if [ "$REQ_HASH" = "NOHASH" ] || [ "$NEW_STAMP" != "$OLD_STAMP" ]; then
  echo "Installing Python dependencies into $VENV_NAME (python $PY_VER)..."

  # Ensure pip tooling is present and current-ish (quietly)
  $PYTHON -m pip install -U pip setuptools wheel -qq

  # Install runtime deps; pip is idempotent and will skip already-satisfied wheels.
  $PYTHON -m pip install -r "$REQ_FILE" -qq

  echo "$NEW_STAMP" > "$STAMP_FILE"
else
  echo "Dependencies already up to date (stamp match)."
fi
