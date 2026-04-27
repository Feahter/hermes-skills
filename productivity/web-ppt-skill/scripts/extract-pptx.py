#!/usr/bin/env python3
"""Extract content from PPTX file for web-ppt-skill.
Usage: python extract-pptx.py <input.pptx> <output_dir>
"""
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

def extract_pptx(pptx_path, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(pptx_path, 'r') as z:
        # Read slide content
        slide_files = sorted([f for f in z.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')])
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)

        slides_content = []
        for i, slide_file in enumerate(slide_files, 1):
            with z.open(slide_file) as f:
                tree = ET.parse(f)
                root = tree.getroot()

                # Extract text
                texts = []
                for elem in root.iter():
                    if elem.text and elem.text.strip():
                        texts.append(elem.text.strip())

                slides_content.append({
                    'index': i,
                    'texts': texts,
                    'images': []
                })

        # Extract images
        media_files = [f for f in z.namelist() if f.startswith('ppt/media/')]
        for media_file in media_files:
            ext = Path(media_file).suffix
            img_name = f"image_{len(images_dir.glob('*')) + 1}{ext}"
            with z.open(media_file) as src, open(images_dir / img_name, 'wb') as dst:
                dst.write(src.read())

        # Write content summary
        with open(output_dir / "content_summary.md", "w") as f:
            f.write(f"# Extracted from {Path(pptx_path).name}\n\n")
            for slide in slides_content:
                f.write(f"\n## Slide {slide['index']}\n")
                for text in slide['texts']:
                    f.write(f"- {text}\n")

        print(f"Extracted {len(slides_content)} slides to {output_dir}")
        return slides_content

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract-pptx.py <input.pptx> <output_dir>")
        sys.exit(1)
    extract_pptx(sys.argv[1], sys.argv[2])
