#!/bin/bash
# PDF export for web-ppt-skill using Playwright
# Usage: bash export-pdf.sh <path-to-html> [output.pdf]

set -e

HTML_PATH="$1"
OUTPUT_PDF="${2:-output.pdf}"

if [ -z "$HTML_PATH" ]; then
  echo "Usage: bash export-pdf.sh <path-to-html> [output.pdf]"
  exit 1
fi

HTML_PATH=$(realpath "$HTML_PATH")
OUTPUT_PDF=$(realpath "$OUTPUT_PDF")
TMP_DIR=$(mktemp -d)

echo "Exporting $HTML_PATH to $OUTPUT_PDF..."

# Use Playwright if available
if command -v playwright &> /dev/null; then
  playwright screenshot --browser=chromium --full-page "$HTML_PATH" "$OUTPUT_PDF" 2>/dev/null || true
fi

# Fallback: use puppeteer or chromium directly
if [ ! -f "$OUTPUT_PDF" ]; then
  node -e "
    const puppeteer = require('puppeteer');
    (async () => {
      const browser = await puppeteer.launch();
      const page = await browser.newPage();
      await page.goto('file://${HTML_PATH}', { waitUntil: 'networkidle0' });
      await page.pdf({ path: '${OUTPUT_PDF}', format: 'A4', landscape: true });
      await browser.close();
    })();
  " 2>/dev/null || echo "PDF export failed. Please install puppeteer: npm i -g puppeteer"
fi

if [ -f "$OUTPUT_PDF" ]; then
  echo "PDF saved to $OUTPUT_PDF"
else
  echo "PDF export not available. Please install puppeteer: npm i -g puppeteer"
fi
