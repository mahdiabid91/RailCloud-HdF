#!/usr/bin/env python3
"""Package the public split files and release scripts in one supporting ZIP."""

from __future__ import annotations

import argparse
import os
import sys
import zipfile
from pathlib import Path

from release_utils import SUPPORTING_ARCHIVE_NAME, project_root


REQUIRED_SPLIT_FILES = ("laz_files.csv", "train_ds.csv", "valid_ds.csv", "test_ds.csv")


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=root)
    parser.add_argument("--output-dir", type=Path, default=root)
    parser.add_argument(
        "--overwrite", action="store_true", help="replace an existing archive after a new ZIP is complete"
    )
    return parser.parse_args()


def source_files(root: Path) -> list[Path]:
    splits_dir = root / "splits"
    scripts_dir = root / "scripts"
    missing = [splits_dir / name for name in REQUIRED_SPLIT_FILES if not (splits_dir / name).is_file()]
    if missing:
        raise ValueError(f"required split files are missing: {missing}")
    if not scripts_dir.is_dir():
        raise ValueError(f"scripts directory not found: {scripts_dir}")

    split_files = [path for path in splits_dir.rglob("*") if path.is_file()]
    script_files = [
        path
        for path in scripts_dir.rglob("*.py")
        if path.is_file() and "__pycache__" not in path.parts
    ]
    if not script_files:
        raise ValueError(f"no Python source files found below {scripts_dir}")
    return sorted(split_files + script_files, key=lambda path: path.relative_to(root).as_posix())


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / SUPPORTING_ARCHIVE_NAME
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")

    try:
        files = source_files(root)
        if output_path.exists() and not args.overwrite:
            raise FileExistsError(
                f"archive already exists (use --overwrite to replace it): {output_path}"
            )
        if temporary.exists():
            temporary.unlink()
        with zipfile.ZipFile(
            temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True
        ) as archive:
            for source in files:
                archive.write(source, arcname=source.relative_to(root).as_posix())
        os.replace(temporary, output_path)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    finally:
        if temporary.exists():
            temporary.unlink()

    print(f"Wrote {output_path} ({output_path.stat().st_size:,} bytes; {len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
