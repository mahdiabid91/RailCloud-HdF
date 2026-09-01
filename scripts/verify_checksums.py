#!/usr/bin/env python3
"""Verify local Zenodo ZIP archives against checksums_sha256.txt."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

from release_utils import project_root


CHUNK_SIZE = 8 * 1024 * 1024
CHECKSUM_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+[ *]?(.+?)\s*$")


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-dir", type=Path, default=root)
    parser.add_argument("--checksums", type=Path, default=root / "checksums_sha256.txt")
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    try:
        lines = args.checksums.read_text(encoding="utf-8-sig").splitlines()
    except OSError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    entries: list[tuple[str, str]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = CHECKSUM_LINE.match(line)
        if not match:
            print(f"ERROR: malformed checksum line {line_number}: {line!r}", file=sys.stderr)
            return 1
        entries.append((match.group(1).lower(), match.group(2)))
    if not entries:
        print("ERROR: checksum file contains no entries", file=sys.stderr)
        return 1

    archive_root = args.archive_dir.resolve()
    failures = 0
    for expected, filename in entries:
        path = (archive_root / filename).resolve()
        try:
            path.relative_to(archive_root)
        except ValueError:
            print(f"FAIL  {filename}: path escapes archive directory", file=sys.stderr)
            failures += 1
            continue
        if not path.is_file():
            print(f"FAIL  {filename}: file not found", file=sys.stderr)
            failures += 1
            continue
        print(f"Checking {filename}...", flush=True)
        actual = sha256(path)
        if actual == expected:
            print(f"OK    {filename}")
        else:
            print(f"FAIL  {filename}: expected {expected}, got {actual}", file=sys.stderr)
            failures += 1
    if failures:
        print(f"Checksum verification failed for {failures} file(s).", file=sys.stderr)
        return 1
    print(f"All {len(entries)} checksum(s) verified successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
