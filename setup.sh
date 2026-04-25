#!/usr/bin/env bash
set -euo pipefail

echo "==> Hindi OCR — Setup"

# check python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 is required (3.8+). Install it first."
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "    python $PY_VER ✓"

# check internet (for first-run bootstrap)
if command -v curl &>/dev/null; then
    if curl -s --connect-timeout 3 https://github.com &>/dev/null; then
        echo "    internet ✓"
    else
        echo "    internet ✗ (needed for first run only)"
        echo "    WARNING: First run downloads ~50 MB (tesseract + Hindi model)"
    fi
fi

# make ocr.py executable
chmod +x "$(dirname "$0")/ocr.py"

echo ""
echo "Ready. Usage:"
echo "  python3 ocr.py /path/to/photos"
echo "  python3 ocr.py /path/to/photos -o /path/to/output"
echo ""
