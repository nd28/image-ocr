#!/usr/bin/env python3
"""
Hindi OCR — Zero-setup batch OCR for Hindi text in images.

Usage:
    python3 ocr.py /path/to/photos
    python3 ocr.py /path/to/photos -o /path/to/output
    python3 ocr.py /path/to/photos -l hin+eng

Single file. No pip install. No sudo. Just Python 3.8+.
Cross-platform: Linux, macOS (Intel + ARM), Windows.
Auto-bootstraps Tesseract on first run (~50MB one-time download).
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# platform detection
# ---------------------------------------------------------------------------

_PLATFORM_MAP = {
    ("Linux", "x86_64"):   "linux-64",
    ("Linux", "amd64"):    "linux-64",
    ("Linux", "aarch64"):  "linux-aarch64",
    ("Linux", "arm64"):    "linux-aarch64",
    ("Darwin", "x86_64"):  "osx-64",
    ("Darwin", "amd64"):   "osx-64",
    ("Darwin", "arm64"):   "osx-arm64",
    ("Darwin", "aarch64"): "osx-arm64",
    ("Windows", "amd64"):  "win-64",
    ("Windows", "x86_64"): "win-64",
}

_IS_WINDOWS = platform.system() == "Windows"


def _detect_platform() -> tuple[str, str]:
    """Return (micromamba_asset_suffix, exe_extension)."""
    system = platform.system()
    machine = platform.machine().lower()
    key = (system, machine)
    asset = _PLATFORM_MAP.get(key)
    if asset is None:
        sys.exit(
            f"Unsupported platform: {system} ({machine}). "
            "Please install tesseract manually."
        )
    exe = ".exe" if system == "Windows" else ""
    return asset, exe


_PLATFORM_SUFFIX, _EXE_SUFFIX = _detect_platform()

# ---------------------------------------------------------------------------
# configuration
# ---------------------------------------------------------------------------

# where we cache micromamba + tesseract
OCR_HOME = Path.home() / ".cache" / "hindi-ocr"
MICROMAMBA_URL = (
    "https://github.com/mamba-org/micromamba-releases/releases/"
    f"latest/download/micromamba-{_PLATFORM_SUFFIX}"
)
MICROMAMBA_BIN = OCR_HOME / "bin" / f"micromamba{_EXE_SUFFIX}"
TESSERACT_ENV = "ocr"

# supported image extensions
SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".gif"}


# ---------------------------------------------------------------------------
# tesseract bootstrapping
# ---------------------------------------------------------------------------

def _find_tesseract() -> Path | None:
    """Look for tesseract on PATH or in our cached micromamba environment."""
    exe = f"tesseract{_EXE_SUFFIX}"

    # 1. standard PATH
    path = shutil.which(exe)
    if path:
        return Path(path)

    # 2. our cached micromamba env (check known locations)
    env = OCR_HOME / "envs" / TESSERACT_ENV
    candidates = [
        env / "bin" / exe,           # Linux, macOS
        env / "Library" / "bin" / exe,  # Windows
    ]
    for p in candidates:
        if p.is_file():
            return p

    return None


def _download(url: str, dest: Path, desc: str) -> None:
    """Download a file with a progress message."""
    print(f"  downloading {desc} ...")
    urllib.request.urlretrieve(url, dest)


def _bootstrap_tesseract() -> Path:
    """Download micromamba + install tesseract-hin. Returns path to tesseract."""
    print("Tesseract not found. Bootstrapping (one-time ~50 MB)...")
    OCR_HOME.mkdir(parents=True, exist_ok=True)

    # download micromamba if not already cached
    if not MICROMAMBA_BIN.is_file():
        MICROMAMBA_BIN.parent.mkdir(parents=True, exist_ok=True)
        _download(MICROMAMBA_URL, MICROMAMBA_BIN, "micromamba")
        if not _IS_WINDOWS:
            MICROMAMBA_BIN.chmod(0o755)

    # install tesseract into a named environment
    print("  installing tesseract + Hindi language data ...")
    subprocess.run(
        [str(MICROMAMBA_BIN), "create", "-n", TESSERACT_ENV, "-c", "conda-forge",
         "tesseract", "-y"],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={**os.environ, "MAMBA_ROOT_PREFIX": str(OCR_HOME)},
    )

    # verify installation
    tesseract = _find_tesseract()
    if not tesseract:
        sys.exit("Failed to install tesseract. Please install it manually.")

    print("  done.\n")
    return tesseract


# ---------------------------------------------------------------------------
# OCR engine
# ---------------------------------------------------------------------------

def _run_tesseract(image: Path, output_base: str, lang: str) -> str:
    """Call tesseract, return stdout text. Also creates output_base.txt."""
    tesseract = _find_tesseract() or _bootstrap_tesseract()

    result = subprocess.run(
        [str(tesseract), str(image), output_base, "-l", lang],
        capture_output=True,
        text=True,
        env={**os.environ, "MAMBA_ROOT_PREFIX": str(OCR_HOME)},
    )

    # tesseract writes to output_base.txt; any console output goes to stderr
    if result.returncode != 0:
        raise RuntimeError(f"tesseract failed: {result.stderr.strip()}")

    txt_path = Path(output_base + ".txt")
    return txt_path.read_text(encoding="utf-8") if txt_path.is_file() else ""


def process_directory(
    directory: Path,
    lang: str,
    output_dir: Path | None = None,
) -> None:
    """Run Hindi OCR on every supported image in *directory*."""
    images = sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    )

    if not images:
        print(f"No supported images found in {directory}")
        return

    out = output_dir or directory
    out.mkdir(parents=True, exist_ok=True)

    total = len(images)
    print(f"Found {total} images. Processing ...\n")

    for i, img_path in enumerate(images, 1):
        status = f"[{i}/{total}] {img_path.name}"
        print(f"{status} ... ", end="", flush=True)
        try:
            txt_path = out / img_path.stem
            text = _run_tesseract(img_path, str(txt_path), lang)
            print("OK")
        except Exception as exc:
            print(f"ERROR: {exc}")

    print(f"\nDone. Output → {out}/")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Zero-setup batch Hindi OCR on images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ocr.py ~/photos
  python3 ocr.py ~/photos -o ~/output
  python3 ocr.py ~/photos -l hin+eng
""",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="directory containing images (default: current)",
    )
    parser.add_argument(
        "-l", "--lang",
        default="hin",
        help="tesseract language code (default: hin)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="output directory for .txt files (default: same as input)",
    )

    args = parser.parse_args()

    directory = Path(args.directory).resolve()
    if not directory.is_dir():
        sys.exit(f"Error: '{directory}' is not a valid directory")

    output_dir = Path(args.output).resolve() if args.output else None
    process_directory(directory, args.lang, output_dir)


if __name__ == "__main__":
    main()
