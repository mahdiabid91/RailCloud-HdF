#!/usr/bin/env python3
"""Generate a scan-level manifest from LAZ files, info headers, and split data."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

from release_utils import info_match_key, parse_info_file, project_root, relative_posix, write_csv_atomic


FIELDS = (
    "scan_index",
    "split",
    "acquisition_folder",
    "laz_relative_path",
    "info_relative_path",
    "laz_filename",
    "info_filename",
    "size_bytes",
    "point_count",
    "las_version",
    "point_data_format",
    "x_min",
    "y_min",
    "z_min",
    "x_max",
    "y_max",
    "z_max",
    "gps_time_min",
    "gps_time_max",
    "classification_histogram",
)
METADATA_FIELDS = FIELDS[8:]


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=root / "data")
    parser.add_argument("--split-manifest", type=Path, default=root / "split_manifest.csv")
    parser.add_argument("--output", type=Path, default=root / "scan_manifest.csv")
    return parser.parse_args()


def acquisition_for(path: Path, data_dir: Path) -> str:
    relative = path.resolve().relative_to(data_dir.resolve())
    if not relative.parts:
        raise ValueError(f"cannot determine acquisition for {path}")
    return relative.parts[0]


def main() -> int:
    args = parse_args()
    root = project_root()
    try:
        laz_files = sorted(
            path for path in args.data_dir.glob("*/cloud/**/*.laz") if path.is_file()
        )
        info_files = sorted(
            path for path in args.data_dir.glob("*/info/**/*.txt") if path.is_file()
        )
        if not laz_files:
            raise ValueError(f"no .laz files found below {args.data_dir}")
        if not args.split_manifest.is_file():
            raise ValueError(
                f"split manifest not found: {args.split_manifest}; run scripts/prepare_splits.py first"
            )

        split_by_key: dict[tuple[str, str], dict[str, str]] = {}
        with args.split_manifest.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                key = (row["acquisition_folder"].casefold(), row["laz_filename"].casefold())
                if key in split_by_key:
                    raise ValueError(f"duplicate split manifest key: {key}")
                split_by_key[key] = row

        info_by_key: defaultdict[tuple[str, str], list[Path]] = defaultdict(list)
        for info_path in info_files:
            key = (acquisition_for(info_path, args.data_dir).casefold(), info_match_key(info_path.stem))
            info_by_key[key].append(info_path)

        matched_info: set[Path] = set()
        matched_split_keys: set[tuple[str, str]] = set()
        unmatched_laz: list[Path] = []
        ambiguous_laz: list[tuple[Path, list[Path]]] = []
        rows: list[dict[str, object]] = []

        for laz_path in laz_files:
            acquisition = acquisition_for(laz_path, args.data_dir)
            match_key = (acquisition.casefold(), info_match_key(laz_path.stem))
            candidates = info_by_key.get(match_key, [])
            info_path: Path | None = candidates[0] if len(candidates) == 1 else None
            if not candidates:
                unmatched_laz.append(laz_path)
            elif len(candidates) > 1:
                ambiguous_laz.append((laz_path, candidates))
            if info_path:
                matched_info.add(info_path)
                metadata = parse_info_file(info_path)
            else:
                metadata = {name: "" for name in METADATA_FIELDS}

            split_key = (acquisition.casefold(), laz_path.name.casefold())
            split_row = split_by_key.get(split_key)
            if split_row:
                matched_split_keys.add(split_key)
            rows.append(
                {
                    "scan_index": split_row["scan_index"] if split_row else "",
                    "split": split_row["split"] if split_row else "",
                    "acquisition_folder": acquisition,
                    "laz_relative_path": relative_posix(laz_path, root),
                    "info_relative_path": relative_posix(info_path, root) if info_path else "",
                    "laz_filename": laz_path.name,
                    "info_filename": info_path.name if info_path else "",
                    "size_bytes": laz_path.stat().st_size,
                    **metadata,
                }
            )

        rows.sort(
            key=lambda row: (
                row["scan_index"] == "",
                int(row["scan_index"]) if row["scan_index"] != "" else 0,
                str(row["laz_relative_path"]),
            )
        )
        write_csv_atomic(args.output, FIELDS, rows)

        unmatched_info = sorted(set(info_files) - matched_info)
        unmatched_split = sorted(set(split_by_key) - matched_split_keys)
        print(f"Found {len(laz_files)} LAZ files and {len(info_files)} info files.")
        print(f"Wrote {len(rows)} rows to {args.output}")
        if unmatched_laz or ambiguous_laz or unmatched_info or unmatched_split:
            print("WARNING: manifest matching was not complete:", file=sys.stderr)
            print(f"  LAZ files without info match: {len(unmatched_laz)}", file=sys.stderr)
            for path in unmatched_laz[:20]:
                print(f"    {relative_posix(path, root)}", file=sys.stderr)
            print(f"  LAZ files with ambiguous info matches: {len(ambiguous_laz)}", file=sys.stderr)
            for path, candidates in ambiguous_laz[:20]:
                names = ", ".join(relative_posix(item, root) for item in candidates)
                print(f"    {relative_posix(path, root)} -> {names}", file=sys.stderr)
            print(f"  Unmatched info files: {len(unmatched_info)}", file=sys.stderr)
            for path in unmatched_info[:20]:
                print(f"    {relative_posix(path, root)}", file=sys.stderr)
            print(f"  Split rows without a local LAZ match: {len(unmatched_split)}", file=sys.stderr)
            for acquisition, filename in unmatched_split[:20]:
                print(f"    {acquisition}/{filename}", file=sys.stderr)
        else:
            print("All LAZ, info, and split records matched one-to-one.")
    except (OSError, ValueError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
