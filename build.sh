#!/bin/sh
set -eu

cd "$(dirname "$0")"

VENV_NAME="venv"
PYTHON="$VENV_NAME/bin/python"

# Create venv and install deps
python3 -m venv "$VENV_NAME"
$PYTHON -m pip install -U pip setuptools wheel -qq
$PYTHON -m pip install -r requirements.txt -qq
$PYTHON -m pip install pyinstaller -U -qq

# Build onefile binary
$PYTHON -m PyInstaller \
  --clean -y \
  --onefile \
  --name main \
  --collect-submodules googleapiclient \
  --collect-submodules google.auth \
  --collect-submodules google.oauth2 \
  --collect-submodules google_auth_oauthlib \
  --collect-submodules google_auth_httplib2 \
  --collect-submodules httplib2 \
  --collect-submodules uritemplate \
  --copy-metadata google-api-python-client \
  --copy-metadata google-auth \
  --copy-metadata google-auth-oauthlib \
  --copy-metadata httplib2 \
  --copy-metadata uritemplate \
  src/main.py

# Pick correct output name (Windows builds produce main.exe)
BIN="./dist/main"
if [ -f "./dist/main.exe" ]; then
  BIN="./dist/main.exe"
fi

# Package registry artifact
mkdir -p dist
tar -czvf dist/archive.tar.gz meta.json "$BIN"
