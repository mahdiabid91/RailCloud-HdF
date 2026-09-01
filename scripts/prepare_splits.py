#!/usr/bin/env python3
"""Validate the original split indices and generate split release manifests."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from release_utils import (
    ACQUISITIONS,
    EXPECTED_SCAN_COUNT,
    EXPECTED_SPLIT_COUNTS,
    acquisition_from_path,
    normalize_laz_path,
    project_root,
    read_single_column_csv,
    write_csv_atomic,
)


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits-dir", type=Path, default=root / "splits")
    parser.add_argument("--manifest", type=Path, default=root / "split_manifest.csv")
    parser.add_argument("--summary", type=Path, default=root / "split_summary.csv")
    return parser.parse_args()


def fail(message: str) -> None:
    raise ValueError(f"split validation failed: {message}")


def main() -> int:
    args = parse_args()
    try:
        paths = read_single_column_csv(args.splits_dir / "laz_files.csv")
        if len(paths) != EXPECTED_SCAN_COUNT:
            fail(f"laz_files.csv has {len(paths)} rows; expected {EXPECTED_SCAN_COUNT}")

        split_indices: dict[str, list[int]] = {}
        for split, expected_count in EXPECTED_SPLIT_COUNTS.items():
            raw_values = read_single_column_csv(args.splits_dir / f"{split}_ds.csv")
            try:
                indices = [int(value, 10) for value in raw_values]
            except ValueError as error:
                fail(f"{split}_ds.csv contains a non-integer value ({error})")
            if len(indices) != expected_count:
                fail(f"{split}_ds.csv has {len(indices)} rows; expected {expected_count}")
            if len(indices) != len(set(indices)):
                fail(f"{split}_ds.csv contains duplicate indices")
            invalid = [index for index in indices if not 0 <= index < EXPECTED_SCAN_COUNT]
            if invalid:
                fail(
                    f"{split}_ds.csv contains indices outside [0, {EXPECTED_SCAN_COUNT - 1}]: "
                    f"{invalid[:10]}"
                )
            split_indices[split] = indices

        owners: dict[int, str] = {}
        for split, indices in split_indices.items():
            for index in indices:
                if index in owners:
                    fail(f"index {index} occurs in both {owners[index]} and {split}")
                owners[index] = split
        expected_indices = set(range(EXPECTED_SCAN_COUNT))
        actual_indices = set(owners)
        if actual_indices != expected_indices:
            missing = sorted(expected_indices - actual_indices)
            extra = sorted(actual_indices - expected_indices)
            fail(f"splits do not cover 0..5352 exactly; missing={missing[:10]}, extra={extra[:10]}")
        if min(actual_indices) != 0 or max(actual_indices) != EXPECTED_SCAN_COUNT - 1:
            fail("indices are not a complete 0-based range")

        manifest_rows: list[dict[str, object]] = []
        summary_counts: Counter[tuple[str, str]] = Counter()
        for scan_index, original in enumerate(paths):
            normalized = normalize_laz_path(original)
            acquisition = acquisition_from_path(normalized)
            if acquisition not in ACQUISITIONS:
                fail(f"row {scan_index} contains unexpected acquisition {acquisition!r}")
            split = owners[scan_index]
            filename = normalized.rsplit("/", 1)[-1]
            if not filename.lower().endswith(".laz"):
                fail(f"row {scan_index} is not a .laz path: {original!r}")
            manifest_rows.append(
                {
                    "scan_index": scan_index,
                    "split": split,
                    "laz_relative_path_original": original,
                    "laz_relative_path_normalized": normalized,
                    "acquisition_folder": acquisition,
                    "laz_filename": filename,
                }
            )
            summary_counts[(split, acquisition)] += 1

        manifest_fields = (
            "scan_index",
            "split",
            "laz_relative_path_original",
            "laz_relative_path_normalized",
            "acquisition_folder",
            "laz_filename",
        )
        summary_rows = [
            {"split": split, "acquisition_folder": acquisition, "count": summary_counts[split, acquisition]}
            for split in EXPECTED_SPLIT_COUNTS
            for acquisition in ACQUISITIONS
        ]
        write_csv_atomic(args.manifest, manifest_fields, manifest_rows)
        write_csv_atomic(args.summary, ("split", "acquisition_folder", "count"), summary_rows)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    counts = ", ".join(f"{name}={len(values)}" for name, values in split_indices.items())
    print(f"Validated {len(paths)} scans ({counts}); indices are disjoint and cover 0..5352.")
    print(f"Wrote {args.manifest}")
    print(f"Wrote {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
