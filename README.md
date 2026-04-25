# Hindi OCR

Zero-setup batch OCR for Hindi text in images. Single file, no dependencies, no sudo.

## Quick Start (No Git)

**Option 1 — One-liner (terminal):**
```bash
curl -O https://raw.githubusercontent.com/nd28/image-ocr/main/ocr.py && python3 ocr.py /path/to/photos
```

**Option 2 — Download ZIP:**
Click **Code → Download ZIP** (green button above), extract, then:
```bash
python3 ocr.py /path/to/photos
```

## How it works

1. Runs Tesseract OCR on every image in a directory
2. Auto-bootstraps Tesseract + Hindi language data on first run (~50 MB one-time download)
3. Writes one `.txt` file per image

**No pip install. No apt-get. No sudo.** Just Python 3.8+.

## Usage

```bash
# OCR all images in a directory (Hindi by default)
python3 ocr.py ~/photos

# Save results to a separate directory
python3 ocr.py ~/photos -o ~/output

# Use mixed language (Hindi + English)
python3 ocr.py ~/photos -l hin+eng

# Process current directory
python3 ocr.py .
```

## Supported formats

`.jpg` `.jpeg` `.png` `.bmp` `.tiff` `.tif` `.webp` `.gif`

## Supported languages

The auto-bootstrap installs **125 languages**. Pass any Tesseract language code:

```bash
python3 ocr.py ~/photos -l ben      # Bengali
python3 ocr.py ~/photos -l guj      # Gujarati
python3 ocr.py ~/photos -l mar      # Marathi
python3 ocr.py ~/photos -l hin+eng  # Hindi + English
```

## Requirements

- Python 3.8+
- Internet (first run only, downloads tesseract)

## License

MIT
