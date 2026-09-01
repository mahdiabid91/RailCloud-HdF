#!/usr/bin/env python3
"""Generate SHA-256 checksums for all final Zenodo ZIP archives."""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import tempfile
from pathlib import Path

from release_utils import ARCHIVE_NAMES, project_root


CHUNK_SIZE = 8 * 1024 * 1024


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-dir", type=Path, default=root)
    parser.add_argument("--output", type=Path, default=root / "checksums_sha256.txt")
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    archive_paths = [args.archive_dir / name for name in ARCHIVE_NAMES]
    missing = [path for path in archive_paths if not path.is_file()]
    if missing:
        print("ERROR: expected Zenodo archives are missing:", file=sys.stderr)
        for path in missing:
            print(f"  {path}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp_name: str | None = None
    try:
        lines: list[str] = []
        for path in archive_paths:
            print(f"Hashing {path.name}...", flush=True)
            lines.append(f"{sha256(path)}  {path.name}\n")
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="\n", dir=args.output.parent, delete=False, suffix=".tmp"
        ) as handle:
            temp_name = handle.name
            handle.writelines(lines)
        os.replace(temp_name, args.output)
    except OSError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    finally:
        if temp_name and Path(temp_name).exists():
            Path(temp_name).unlink()
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
