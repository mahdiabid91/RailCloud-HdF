# RailCloud-HdF v1.0

RailCloud-HdF is a large-scale, densely annotated LiDAR point-cloud dataset for semantic segmentation of railway scenes. It was acquired along eight railway lines in the Hauts-de-France region of northern France and is distributed as compressed LAS (`.laz`) tiles.

This repository is the documentation and metadata companion for dataset version **v1.0**. The archival dataset record is hosted on Zenodo: **<https://doi.org/10.5281/zenodo.22115147>**.

## Dataset at a glance

| Property | Value |
|---|---|
| Version | v1.0 (metadata version `1.0.0`) |
| Task | Point-wise semantic segmentation of railway scenes |
| Coverage | 267.52 km across 8 railway lines |
| Scans / tiles | 5,353 |
| Points | Approximately 8.06 billion (8,060,277,695 from the supplied scan headers) |
| Source data size | Approximately 48 GB (50.08 GB decimal / 46.64 GiB for the local `.laz` files) |
| Point-cloud format | LAZ; LAS version 1.2, point data format 3 |
| Original benchmark splits | 4,068 train / 1,017 validation / 268 test |
| Dataset license | Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) |

The point records contain 3D coordinates, intensity, classification, RGB color channels, and GPS time. The scan headers consistently report LAS 1.2 and point data format 3.

## Associated paper

The dataset was introduced in:

> Mahdi Abid, Mathis Teixeira, Ankur Mahtani, and Thomas Laurent. “RailCloud-HdF: A Large-Scale Point Cloud Dataset for Railway Scene Semantic Segmentation.” In *Proceedings of the 19th International Joint Conference on Computer Vision, Imaging and Computer Graphics Theory and Applications, Volume 2: VISAPP*, pages 159–170, SciTePress, 2024. <https://doi.org/10.5220/0012394800003660>

If you use RailCloud-HdF in your research, please cite the associated VISAPP 2024 paper. The Zenodo DOI identifies this archived dataset release and can be used to reference the exact dataset version.

```bibtex
@conference{visapp24,
  author    = {Mahdi Abid and Mathis Teixeira and Ankur Mahtani and Thomas Laurent},
  title     = {RailCloud-HdF: A Large-Scale Point Cloud Dataset for Railway Scene Semantic Segmentation},
  booktitle = {Proceedings of the 19th International Joint Conference on Computer Vision, Imaging and Computer Graphics Theory and Applications - Volume 2: VISAPP},
  year      = {2024},
  pages     = {159--170},
  publisher = {SciTePress},
  doi       = {10.5220/0012394800003660}
}
```

Machine-readable citation metadata are also provided in `CITATION.cff`.

## Download and archive layout

The Zenodo release is intended to contain one ZIP archive per acquisition:

```text
RailCloud-HdF_v1.0_ACQ_242_Aulnoye_Busigny.zip
RailCloud-HdF_v1.0_ACQ_272_Lille_Douai.zip
RailCloud-HdF_v1.0_ACQ_284_Lens_Ostricourt.zip
RailCloud-HdF_v1.0_ACQ_286_Don_Lens.zip
RailCloud-HdF_v1.0_ACQ_289_Don_Bethune.zip
RailCloud-HdF_v1.0_ACQ_289_Lille_Don.zip
RailCloud-HdF_v1.0_ACQ_295_Hazebrouck_Calais.zip
RailCloud-HdF_v1.0_ACQ_301_Hazebrouck_Dunkerque.zip
```

The release also includes:

```text
RailCloud-HdF_v1.0_supporting_files.zip
```

This small archive preserves the original `splits/` directory and the release-preparation `scripts/` directory. Download all nine archives and the individually listed documentation and manifest files from the [Zenodo record](https://zenodo.org/records/22115147). Extract the supporting archive into the release root. Then create a `data/` directory and extract all eight acquisition archives into it. Each acquisition archive retains its acquisition folder, so the resulting layout is:

```text
RailCloud-HdF_v1.0/
├── data/
│   ├── ACQ_242_Aulnoye_Busigny/
│   │   ├── cloud/*.laz
│   │   └── info/*.txt
│   ├── ACQ_272_Lille_Douai/{cloud,info}/
│   ├── ACQ_284_Lens_Ostricourt/{cloud,info}/
│   ├── ACQ_286_Don_Lens/{cloud,info}/
│   ├── ACQ_289_Don_Bethune/{cloud,info}/
│   ├── ACQ_289_Lille_Don/{cloud,info}/
│   ├── ACQ_295_Hazebrouck_Calais/{cloud,info}/
│   └── ACQ_301_Hazebrouck_Dunkerque/{cloud,info}/
├── splits/
├── scripts/
├── README.md
├── LICENSE.txt
├── CITATION.cff
├── metadata.json
├── split_manifest.csv
├── split_summary.csv
├── scan_manifest.csv
├── acquisition_summary.csv
├── file_manifest.csv
└── checksums_sha256.txt
```

Within every acquisition, `cloud/` contains the point-cloud tiles and `info/` contains the corresponding text-form LAS/LAZ header report. The metadata report includes point count, spatial bounds, GPS-time range, and a classification histogram without requiring the full LAZ file to be read.

## Integrity verification

After all nine ZIP archives have been created, `scripts/generate_checksums.py` writes their SHA-256 values to `checksums_sha256.txt`. To verify downloaded archives, put the checksum file beside the ZIP files and run:

```console
python scripts/verify_checksums.py --archive-dir . --checksums checksums_sha256.txt
```

Every archive must report `OK`. A missing file or hash mismatch returns a nonzero exit status.

## Original benchmark splits

The headerless CSV files in `splits/` preserve the original benchmark partition:

| File | Meaning | Rows |
|---|---|---:|
| `laz_files.csv` | Ordered list of all LAZ paths | 5,353 |
| `train_ds.csv` | 0-based row indices into `laz_files.csv` | 4,068 |
| `valid_ds.csv` | 0-based row indices into `laz_files.csv` | 1,017 |
| `test_ds.csv` | 0-based row indices into `laz_files.csv` | 268 |

The three index sets are disjoint and cover all 5,353 scans. The original paths in `laz_files.csv` use Windows backslashes and the historical directory name `Nuage`; the release data directory is named `cloud`. `split_manifest.csv` preserves the original strings, adds POSIX-normalized paths, and links each row to an acquisition and filename. `scan_manifest.csv` provides the paths that exist in this release.

Regenerate and validate the derived split files with:

```console
python scripts/prepare_splits.py
```

The split protocol corresponds to approximately 76% train, 19% validation, and 5% test globally. See the associated paper for the benchmark preprocessing and evaluation protocol.

## Semantic classes

The classification histograms in all 5,353 supplied header reports verify the following LAS classification values:

| ID | Label |
|---:|---|
| 0 | Unclassified |
| 1 | Ground |
| 2 | Vegetation |
| 3 | Building |
| 4 | Catenary pole |
| 5 | Rail |
| 6 | Structure |
| 7 | Catenary wire |
| 8 | Level crossing gate (`LCG`) |

The paper excludes `Unclassified` from its baseline performance evaluation because that category includes outliers and heterogeneous objects. This leaves eight evaluated classes in the reported experiments.

## Coordinate reference systems

The point coordinates use separate horizontal and vertical reference systems:

| Coordinates | Reference system | EPSG code | Unit |
|---|---|---:|---|
| Planimetry (`X`, `Y`) | ETRS89-FRA [RGF93 v1] / CC50 (formerly named RGF93 v1 / CC50) | [EPSG:3950](https://epsg.org/crs_3950/RGF93-v1-CC50.html) | metre |
| Altimetry (`Z`) | NGF-IGN69 height | [EPSG:5720](https://epsg.io/5720) | metre |

All supplied LAS headers use scale factors of `0.001 0.001 0.001`, corresponding to 1 mm coordinate quantization. In `laspy`, lowercase `x`, `y`, and `z` expose scaled coordinates in the CRS units (metres), while uppercase `X`, `Y`, and `Z` expose the stored integer values. Account for the header scale and offset when using raw integer coordinates.

## Using the LAZ files

For a quick visualization without installing desktop software, open [Plas.io](https://plas.io/) and load a LAZ file in the browser. LAZ files can also be opened directly in tools such as CloudCompare or processed with PDAL. For example:

```console
pdal info data/ACQ_242_Aulnoye_Busigny/cloud/ACQ_242_Aulnoye_Busigny_F_0+000_0+050.laz
```

Python users can use `laspy` with the `lazrs` decompression backend to extract coordinates, intensity, classifications, color, GPS time, and other stored point dimensions:

```python
import laspy
import numpy as np

cloud = laspy.read("data/ACQ_242_Aulnoye_Busigny/cloud/ACQ_242_Aulnoye_Busigny_F_0+000_0+050.laz")
xyz_m = np.column_stack((cloud.x, cloud.y, cloud.z))
intensity = np.asarray(cloud.intensity)
classification = np.asarray(cloud.classification)

print(xyz_m.shape, intensity.shape, classification.shape)
```

Install the required packages with `pip install "laspy[lazrs]" numpy`. The `pylas` library can also read these fields in existing Python workflows; the example above uses the current `laspy` API.

Individual tiles can contain millions of points. Plan memory use accordingly; the supplied `info/*.txt` and `scan_manifest.csv` files are preferable for lightweight inspection. `laspy.open()` also supports chunked reading when loading a complete tile at once would use too much memory.

## Intended research uses

RailCloud-HdF is intended for academic and research use. Examples include:

- benchmarking point-cloud methods;
- evaluating new semantic segmentation, classification, or object-detection methods;
- segmenting additional objects to annotate new classes;
- cleaning, extending, or otherwise improving and completing the dataset.

All use and redistribution must comply with CC BY-NC 4.0, including attribution and the prohibition on commercial use. These examples describe the intended research scope; the license terms govern the permissions and restrictions.

## Rebuilding release metadata

The scripts use only the Python standard library:

```console
python scripts/prepare_splits.py
python scripts/generate_scan_manifest.py
python scripts/generate_acquisition_summary.py
```

For release packaging, run `python scripts/package_for_zenodo.py`, followed by `python scripts/package_supporting_files.py`, `python scripts/generate_checksums.py`, and finally `python scripts/generate_file_manifest.py`. LAZ files are stored without an additional ZIP compression pass; ZIP is used primarily to retain structure and reduce the number of uploaded files. Existing archives are not overwritten unless `--overwrite` is explicitly supplied.

Generated metadata files have the following roles:

- `split_manifest.csv`: one row per original split-list entry;
- `split_summary.csv`: split counts by acquisition;
- `scan_manifest.csv`: scan-level file, header, bounds, class, and split metadata;
- `acquisition_summary.csv`: aggregate file, point, extent, class, and split statistics;
- `file_manifest.csv`: all nine final archive names, types, sizes, SHA-256 values, and member counts.

## Acquisition context

The data were collected over four days with two identical railborne acquisition systems mounted horizontally on a flat wagon. Each system combined a RIEGL VUX-1HA laser scanner, IGI Compact MEMS (ROBIN) inertial navigation system, Septentrio dual-GNSS receiver, and FLIR Grasshopper 3 12 MP camera. The paper reports a 360° LiDAR field of view, a 200 Hz acquisition rate, an acquisition height of 3.61 m, and round trips used to densify the point clouds. Consult the paper for full acquisition and annotation methodology.

## License

RailCloud-HdF v1.0 is made available under the [Creative Commons Attribution-NonCommercial 4.0 International license](https://creativecommons.org/licenses/by-nc/4.0/) (CC BY-NC 4.0). See `LICENSE.txt`.

The associated paper has its own CC BY-NC-ND 4.0 publication license. The dataset license and paper license are distinct.

## Contact

- Mahdi Abid: <mahdiabid91@gmail.com>
- Institutional contact: <mahdi.abid@railenium.eu>

## Changelog

- **v1.0 — 2024-02-27:** Initial archival Zenodo release. Preserves the original LAZ tiles and benchmark splits, with release manifests, validation scripts, documentation, and checksums.
