#!/usr/bin/env python3

import os
import sys


def main() -> int:
    if len(sys.argv) < 2 or not sys.argv[1]:
        print("Usage: python find_and_print_files.py FILE_NAME", file=sys.stderr)
        return 1

    file_name = sys.argv[1]
    script_directory = os.path.dirname(os.path.abspath(__file__))
    matches = []

    for directory_path, _, file_names in os.walk(script_directory):
        for name in file_names:
            path = os.path.join(directory_path, name)
            if name == file_name and os.path.isfile(path):
                matches.append(path)

    if not matches:
        print(f"No files named {file_name!r} found in {script_directory}.")
        return 0

    for path in sorted(matches):
        print(f"\n--- {path} ---")
        with open(path, encoding="utf-8") as file:
            contents = file.read()
        print(contents, end="" if contents.endswith("\n") else "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
