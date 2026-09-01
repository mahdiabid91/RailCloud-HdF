"""Shared helpers for the RailCloud-HdF v1.0 release scripts."""

from __future__ import annotations

import csv
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Iterable, Mapping, Sequence


DATASET_NAME = "RailCloud-HdF"
VERSION = "v1.0"
EXPECTED_SCAN_COUNT = 5_353
EXPECTED_SPLIT_COUNTS = {"train": 4_068, "valid": 1_017, "test": 268}
ACQUISITIONS = (
    "ACQ_242_Aulnoye_Busigny",
    "ACQ_272_Lille_Douai",
    "ACQ_284_Lens_Ostricourt",
    "ACQ_286_Don_Lens",
    "ACQ_289_Don_Bethune",
    "ACQ_289_Lille_Don",
    "ACQ_295_Hazebrouck_Calais",
    "ACQ_301_Hazebrouck_Dunkerque",
)
DATA_ARCHIVE_NAMES = tuple(f"{DATASET_NAME}_{VERSION}_{name}.zip" for name in ACQUISITIONS)
SUPPORTING_ARCHIVE_NAME = f"{DATASET_NAME}_{VERSION}_supporting_files.zip"
ARCHIVE_NAMES = DATA_ARCHIVE_NAMES + (SUPPORTING_ARCHIVE_NAME,)

FLOAT = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
HEADER_PATTERNS = {
    "point_count": re.compile(r"^\s*number of point records:\s*(\d+)\s*$", re.MULTILINE),
    "las_version": re.compile(r"^\s*version major\.minor:\s*([^\s]+)\s*$", re.MULTILINE),
    "point_data_format": re.compile(r"^\s*point data format:\s*(\d+)\s*$", re.MULTILINE),
    "xyz_min": re.compile(
        rf"^\s*min x y z:\s*({FLOAT})\s+({FLOAT})\s+({FLOAT})\s*$", re.MULTILINE
    ),
    "xyz_max": re.compile(
        rf"^\s*max x y z:\s*({FLOAT})\s+({FLOAT})\s+({FLOAT})\s*$", re.MULTILINE
    ),
    "gps_time": re.compile(rf"^\s*gps_time\s+({FLOAT})\s+({FLOAT})\s*$", re.MULTILINE),
}
HISTOGRAM_ENTRY = re.compile(r"^\s*(\d+)\s+(.+?)\s+\((\d+)\)\s*$")


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def relative_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def normalize_laz_path(value: str) -> str:
    """Convert a split-list path to a relative POSIX-style path."""
    normalized = value.strip().replace("\\", "/")
    normalized = re.sub(r"/+", "/", normalized).lstrip("/")
    parts = [part for part in normalized.split("/") if part not in ("", ".")]
    if any(part == ".." for part in parts):
        raise ValueError(f"parent traversal is not allowed in a LAZ path: {value!r}")
    return "/".join(parts)


def acquisition_from_path(path_value: str) -> str:
    for part in normalize_laz_path(path_value).split("/"):
        if part.startswith("ACQ_"):
            return part
    raise ValueError(f"could not infer acquisition folder from path: {path_value!r}")


def read_single_column_csv(path: Path) -> list[str]:
    values: list[str] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for line_number, row in enumerate(csv.reader(handle), start=1):
            if len(row) != 1 or not row[0].strip():
                raise ValueError(
                    f"{path}: row {line_number} must contain exactly one non-empty field"
                )
            values.append(row[0].strip())
    return values


def write_csv_atomic(path: Path, fieldnames: Sequence[str], rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
        ) as handle:
            temp_name = handle.name
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise")
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temp_name, path)
    finally:
        if temp_name and Path(temp_name).exists():
            Path(temp_name).unlink()


def parse_info_file(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    result: dict[str, object] = {
        "point_count": "",
        "las_version": "",
        "point_data_format": "",
        "x_min": "",
        "y_min": "",
        "z_min": "",
        "x_max": "",
        "y_max": "",
        "z_max": "",
        "gps_time_min": "",
        "gps_time_max": "",
        "classification_histogram": "",
    }

    for key in ("point_count", "las_version", "point_data_format"):
        match = HEADER_PATTERNS[key].search(text)
        if match:
            result[key] = int(match.group(1)) if key != "las_version" else match.group(1)

    for key, names in (
        ("xyz_min", ("x_min", "y_min", "z_min")),
        ("xyz_max", ("x_max", "y_max", "z_max")),
        ("gps_time", ("gps_time_min", "gps_time_max")),
    ):
        match = HEADER_PATTERNS[key].search(text)
        if match:
            for name, value in zip(names, match.groups()):
                result[name] = value

    histogram: dict[str, dict[str, object]] = {}
    in_histogram = False
    for line in text.splitlines():
        if line.strip().lower() == "histogram of classification of points:":
            in_histogram = True
            continue
        if not in_histogram:
            continue
        match = HISTOGRAM_ENTRY.match(line)
        if match:
            count, label, class_id = match.groups()
            histogram[class_id] = {"label": label.strip(), "count": int(count)}
        elif line.strip() and histogram:
            break
    if histogram:
        result["classification_histogram"] = json.dumps(
            histogram, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        )
    return result


def info_match_key(stem: str) -> str:
    stem = re.sub(r"_info$", "", stem, flags=re.IGNORECASE)
    return re.sub(r"[^a-z0-9]+", "", stem.lower())


def archive_name(acquisition: str) -> str:
    return f"{DATASET_NAME}_{VERSION}_{acquisition}.zip"
