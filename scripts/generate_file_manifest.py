#!/usr/bin/env python3
"""Create a manifest of all final Zenodo archives."""

from __future__ import annotations

import argparse
import csv
import re
import sys
import zipfile
from pathlib import Path

from release_utils import (
    ACQUISITIONS,
    ARCHIVE_NAMES,
    SUPPORTING_ARCHIVE_NAME,
    archive_name,
    project_root,
    write_csv_atomic,
)


CHECKSUM_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+[ *]?(.+?)\s*$")
FIELDS = (
    "archive_type",
    "acquisition_folder",
    "archive_filename",
    "size_bytes",
    "sha256",
    "number_of_archive_members",
    "number_of_laz_files",
    "number_of_info_files",
)


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-dir", type=Path, default=root)
    parser.add_argument("--checksums", type=Path, default=root / "checksums_sha256.txt")
    parser.add_argument("--acquisition-summary", type=Path, default=root / "acquisition_summary.csv")
    parser.add_argument("--output", type=Path, default=root / "file_manifest.csv")
    return parser.parse_args()


def read_checksums(path: Path) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = CHECKSUM_LINE.match(line)
        if not match:
            raise ValueError(f"malformed checksum line {line_number}: {line!r}")
        digest, filename = match.groups()
        if filename in checksums:
            raise ValueError(f"duplicate checksum entry for {filename}")
        checksums[filename] = digest.lower()
    return checksums


def main() -> int:
    args = parse_args()
    try:
        checksums = read_checksums(args.checksums)
        with args.acquisition_summary.open("r", encoding="utf-8-sig", newline="") as handle:
            summaries = {row["acquisition_folder"]: row for row in csv.DictReader(handle)}

        rows: list[dict[str, object]] = []
        for acquisition in ACQUISITIONS:
            filename = archive_name(acquisition)
            archive_path = args.archive_dir / filename
            if not archive_path.is_file():
                raise ValueError(f"archive not found: {archive_path}")
            if filename not in checksums:
                raise ValueError(f"checksum not found for {filename}")
            if acquisition not in summaries:
                raise ValueError(f"acquisition summary not found for {acquisition}")
            summary = summaries[acquisition]
            with zipfile.ZipFile(archive_path) as archive:
                member_count = len(archive.infolist())
            rows.append(
                {
                    "archive_type": "acquisition",
                    "acquisition_folder": acquisition,
                    "archive_filename": filename,
                    "size_bytes": archive_path.stat().st_size,
                    "sha256": checksums[filename],
                    "number_of_archive_members": member_count,
                    "number_of_laz_files": summary["number_of_laz_files"],
                    "number_of_info_files": summary["number_of_info_files"],
                }
            )

        supporting_path = args.archive_dir / SUPPORTING_ARCHIVE_NAME
        if not supporting_path.is_file():
            raise ValueError(f"archive not found: {supporting_path}")
        if SUPPORTING_ARCHIVE_NAME not in checksums:
            raise ValueError(f"checksum not found for {SUPPORTING_ARCHIVE_NAME}")
        with zipfile.ZipFile(supporting_path) as archive:
            supporting_member_count = len(archive.infolist())
        rows.append(
            {
                "archive_type": "supporting",
                "acquisition_folder": "",
                "archive_filename": SUPPORTING_ARCHIVE_NAME,
                "size_bytes": supporting_path.stat().st_size,
                "sha256": checksums[SUPPORTING_ARCHIVE_NAME],
                "number_of_archive_members": supporting_member_count,
                "number_of_laz_files": "",
                "number_of_info_files": "",
            }
        )

        expected_names = set(ARCHIVE_NAMES)
        unexpected_checksums = sorted(set(checksums) - expected_names)
        if unexpected_checksums:
            raise ValueError(f"unexpected entries in checksum file: {unexpected_checksums}")
        write_csv_atomic(args.output, FIELDS, rows)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Wrote {len(rows)} archive rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
