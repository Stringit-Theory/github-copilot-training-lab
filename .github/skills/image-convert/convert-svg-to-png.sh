#!/usr/bin/env bash

if [[ -z "${1:-}" ]]; then
	echo "Usage: $0 INPUT_SVG_FILE" >&2
	exit 1
fi

input_svg="$1"
output_png="${input_svg%.*}.png"

if [[ ! -f "$input_svg" ]]; then
	echo "Error: input SVG file not found: $input_svg" >&2
	exit 1
fi

convert "$input_svg" "$output_png"
