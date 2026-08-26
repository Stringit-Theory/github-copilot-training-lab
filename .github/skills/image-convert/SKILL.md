---
name: image-convert
description: Converts SVG images to PNG format. Use when asked to convert SVG files.
allowed-tools: zsh
---

When asked to convert an SVG to PNG, run the `convert-svg-to-png.sh` script
from this skill's base directory, passing the input SVG file path as the
first argument. Take the input file path from the user prompt, and return the output PNG file path to the user.