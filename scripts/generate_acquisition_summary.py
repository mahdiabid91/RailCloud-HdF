#!/usr/bin/env python3
"""Aggregate the scan manifest into one row per acquisition."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from release_utils import ACQUISITIONS, project_root, write_csv_atomic


FIELDS = (
    "acquisition_folder",
    "number_of_laz_files",
    "number_of_info_files",
    "total_size_bytes",
    "total_size_gb",
    "total_point_count",
    "train_count",
    "valid_count",
    "test_count",
    "x_min",
    "y_min",
    "z_min",
    "x_max",
    "y_max",
    "z_max",
    "classification_histogram_total",
)

PAPER_STATS = {
    "ACQ_242_Aulnoye_Busigny": (693, 1_051_200_000),
    "ACQ_272_Lille_Douai": (861, 1_496_000_000),
    "ACQ_284_Lens_Ostricourt": (296, 424_700_000),
    "ACQ_286_Don_Lens": (323, 435_400_000),
    "ACQ_289_Don_Bethune": (463, 686_800_000),
    "ACQ_289_Lille_Don": (553, 873_000_000),
    "ACQ_295_Hazebrouck_Calais": (1_215, 1_689_100_000),
    "ACQ_301_Hazebrouck_Dunkerque": (949, 1_404_200_000),
}


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan-manifest", type=Path, default=root / "scan_manifest.csv")
    parser.add_argument("--output", type=Path, default=root / "acquisition_summary.csv")
    return parser.parse_args()


def numeric_values(rows: list[dict[str, str]], key: str) -> list[float]:
    return [float(row[key]) for row in rows if row.get(key, "").strip()]


def compact_number(value: float) -> str:
    return format(value, ".15g")


def aggregate_histograms(rows: list[dict[str, str]]) -> str:
    totals: dict[str, dict[str, object]] = {}
    for row in rows:
        value = row.get("classification_histogram", "").strip()
        if not value:
            continue
        histogram = json.loads(value)
        for class_id, item in histogram.items():
            label = str(item["label"])
            count = int(item["count"])
            existing = totals.setdefault(class_id, {"label": label, "count": 0})
            if existing["label"] != label:
                raise ValueError(
                    f"classification {class_id} has inconsistent labels: "
                    f"{existing['label']!r} and {label!r}"
                )
            existing["count"] = int(existing["count"]) + count
    return json.dumps(totals, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def main() -> int:
    args = parse_args()
    try:
        with args.scan_manifest.open("r", encoding="utf-8-sig", newline="") as handle:
            source_rows = list(csv.DictReader(handle))
        grouped: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
        for row in source_rows:
            grouped[row["acquisition_folder"]].append(row)
        unexpected = sorted(set(grouped) - set(ACQUISITIONS))
        missing = sorted(set(ACQUISITIONS) - set(grouped))
        if unexpected or missing:
            raise ValueError(f"unexpected acquisitions={unexpected}; missing acquisitions={missing}")

        output_rows: list[dict[str, object]] = []
        warnings: list[str] = []
        for acquisition in ACQUISITIONS:
            rows = grouped[acquisition]
            size_bytes = sum(int(row["size_bytes"]) for row in rows)
            point_counts = [int(row["point_count"]) for row in rows if row["point_count"].strip()]
            point_total = sum(point_counts)
            bounds: dict[str, str] = {}
            for axis in "xyz":
                minimum = numeric_values(rows, f"{axis}_min")
                maximum = numeric_values(rows, f"{axis}_max")
                bounds[f"{axis}_min"] = compact_number(min(minimum)) if minimum else ""
                bounds[f"{axis}_max"] = compact_number(max(maximum)) if maximum else ""
            output_rows.append(
                {
                    "acquisition_folder": acquisition,
                    "number_of_laz_files": len(rows),
                    "number_of_info_files": sum(bool(row["info_relative_path"].strip()) for row in rows),
                    "total_size_bytes": size_bytes,
                    "total_size_gb": f"{size_bytes / 1_000_000_000:.3f}",
                    "total_point_count": point_total if len(point_counts) == len(rows) else "",
                    "train_count": sum(row["split"] == "train" for row in rows),
                    "valid_count": sum(row["split"] == "valid" for row in rows),
                    "test_count": sum(row["split"] == "test" for row in rows),
                    **bounds,
                    "classification_histogram_total": aggregate_histograms(rows),
                }
            )

            paper_tiles, paper_points = PAPER_STATS[acquisition]
            if len(rows) != paper_tiles:
                warnings.append(
                    f"{acquisition}: computed {len(rows)} tiles; paper reports {paper_tiles}"
                )
            if len(point_counts) != len(rows):
                warnings.append(
                    f"{acquisition}: point counts parsed for {len(point_counts)}/{len(rows)} scans"
                )
            elif abs(point_total - paper_points) > 100_000:
                warnings.append(
                    f"{acquisition}: computed {point_total:,} points; paper reports "
                    f"approximately {paper_points:,}"
                )

        write_csv_atomic(args.output, FIELDS, output_rows)
        print(f"Wrote {len(output_rows)} acquisition rows to {args.output}")
        if warnings:
            print("Paper cross-check warnings (computed values were retained):", file=sys.stderr)
            for warning in warnings:
                print(f"  {warning}", file=sys.stderr)
        else:
            print("Computed tile and rounded point totals agree with the paper statistics.")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
