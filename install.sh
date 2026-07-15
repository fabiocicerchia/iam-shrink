#!/usr/bin/env bash
set -euo pipefail
# One-line installer for iam-shrink
# Usage: curl -fsSL https://raw.githubusercontent.com/fabiocicerchia/iam-shrink/main/install.sh | bash

if command -v pipx &>/dev/null; then
  pipx install git+https://github.com/fabiocicerchia/iam-shrink
else
  pip install --user git+https://github.com/fabiocicerchia/iam-shrink
fi
echo "iam-shrink installed. Run: iam-shrink --help"
