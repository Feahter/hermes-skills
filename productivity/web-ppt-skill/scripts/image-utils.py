#!/usr/bin/env python3
"""Image utilities for web-ppt-skill.
Resize, crop, and optimize images for presentations.
Usage: python image-utils.py <command> <input> <output> [options]
Commands: resize, crop-circle, optimize
"""
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow required. Run: pip install Pillow")
    sys.exit(1)

def resize(input_path, output_path, max_width=1920, max_height=1080):
    """Resize image maintaining aspect ratio."""
    img = Image.open(input_path)
    img.thumbnail((max_width, max_height), Image.LANCZOS)
    img.save(output_path, optimize=True)
    print(f"Resized to {img.size}: {output_path}")

def crop_circle(input_path, output_path):
    """Crop image to circle (for avatars/profile images)."""
    img = Image.open(input_path).convert("RGBA")
    size = min(img.size)
    mask = Image.new("L", (size, size), 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0), mask)
    output.save(output_path)
    print(f"Cropped circle: {output_path}")

def optimize(input_path, output_path, quality=85):
    """Compress and optimize image."""
    img = Image.open(input_path)
    if img.mode == "RGBA":
        img = img.convert("RGB")
    img.save(output_path, "JPEG", quality=quality, optimize=True)
    print(f"Optimized ({quality}%): {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    cmd, inp, out = sys.argv[1:4]
    if cmd == "resize":
        resize(inp, out)
    elif cmd == "crop-circle":
        crop_circle(inp, out)
    elif cmd == "optimize":
        q = int(sys.argv[4]) if len(sys.argv) > 4 else 85
        optimize(inp, out, q)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
