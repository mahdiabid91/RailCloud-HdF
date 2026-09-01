#!/usr/bin/env python3
"""Package each acquisition as a separate ZIP archive for Zenodo upload."""

from __future__ import annotations

import argparse
import os
import sys
import zipfile
from pathlib import Path

from release_utils import ACQUISITIONS, archive_name, project_root


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=root / "data")
    parser.add_argument("--output-dir", type=Path, default=root)
    parser.add_argument(
        "--overwrite", action="store_true", help="replace an existing archive after a new ZIP is complete"
    )
    return parser.parse_args()


def package(acquisition_dir: Path, output_path: Path, data_dir: Path) -> None:
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    try:
        with zipfile.ZipFile(temporary, "w", allowZip64=True) as archive:
            for source in sorted(path for path in acquisition_dir.rglob("*") if path.is_file()):
                arcname = source.relative_to(data_dir).as_posix()
                compression = zipfile.ZIP_STORED if source.suffix.casefold() == ".laz" else zipfile.ZIP_DEFLATED
                archive.write(source, arcname=arcname, compress_type=compression, compresslevel=6)
        os.replace(temporary, output_path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    try:
        for acquisition in ACQUISITIONS:
            source = args.data_dir / acquisition
            if not (source / "cloud").is_dir() or not (source / "info").is_dir():
                raise ValueError(f"expected cloud/ and info/ below {source}")
            output = args.output_dir / archive_name(acquisition)
            if output.exists() and not args.overwrite:
                raise FileExistsError(f"archive already exists (use --overwrite to replace it): {output}")
        for acquisition in ACQUISITIONS:
            source = args.data_dir / acquisition
            output = args.output_dir / archive_name(acquisition)
            print(f"Creating {output.name}...", flush=True)
            package(source, output, args.data_dir)
            print(f"Wrote {output} ({output.stat().st_size:,} bytes)")
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
