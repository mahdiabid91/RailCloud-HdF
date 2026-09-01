# notes_for_release.md

# RailCloud-HdF v1.0 — release notes for Zenodo preparation

## Dataset identity

Dataset name: RailCloud-HdF  
Version: v1.0  
Release date: 2024-02-27
Dataset type: LiDAR point-cloud dataset for railway scene semantic segmentation  
Primary file format: compressed LAS files, `.laz`  
Approximate release size: approximately 48 GB  
Intended archive: Zenodo  
Zenodo DOI: 10.5281/zenodo.22115147

## Associated paper

Users should cite the associated paper when using this dataset:

Mahdi Abid, Mathis Teixeira, Ankur Mahtani, Thomas Laurent.  
RailCloud-HdF: A Large-Scale Point Cloud Dataset for Railway Scene Semantic Segmentation.  
VISAPP 2024 — 19th International Conference on Computer Vision Theory and Applications.  
In Proceedings of VISIGRAPP 2024, Volume 2: VISAPP, pages 159–170.  
DOI: 10.5220/0012394800003660

Suggested citation message:

If you use RailCloud-HdF in your research, please cite the associated VISAPP 2024 paper. The Zenodo DOI identifies this archived dataset release and may be used to refer to this exact dataset version.

## Authors / creators

- Mahdi Abid
- Mathis Teixeira
- Ankur Mahtani
- Thomas Laurent

Affiliation in the associated paper: FCS Railenium, F-59300 Famars, France.

## Contact

Contact: mahdiabid91@gmail.com  
Alternative / institutional contact: mahdi.abid@railenium.eu

## License

Dataset license: CC BY-NC 4.0

Important: do not assume that the dataset license is identical to the paper license. The paper is published under CC BY-NC-ND 4.0.

## Permission

Permission to publish the dataset has been obtained.

Details of the permission / approving entity: Railenium authorized sharing the dataset publicly. People can modify, clean, extend, annotate, or improve the dataset and redistribute their version, provided the use is non-commercial and they give proper attribution.

## Intended research uses

The dataset is intended for academic and research use, including:

- benchmarking point-cloud methods;
- evaluating new methods for semantic segmentation, classification, or object detection;
- segmenting additional objects to annotate new classes;
- cleaning, extending, improving, or otherwise completing the dataset.

All use and redistribution must comply with CC BY-NC 4.0. These examples describe the intended research scope; the license terms govern the permissions and restrictions.

## Dataset description

RailCloud-HdF is a large-scale LiDAR point-cloud dataset designed for semantic segmentation of railway scenes. The dataset contains dense point-wise annotations and was collected in the Hauts-de-France region in northern France.

The dataset covers 8 railway lanes connecting 11 cities:

- Aulnoye
- Busigny
- Lille
- Douai
- Lens
- Ostricourt
- Don
- Béthune
- Hazebrouck
- Calais
- Dunkerque

The suffix `HdF` refers to Hauts-de-France.

## Acquisition context

The data were acquired using two identical railborne LiDAR acquisition systems mounted on a flat wagon.

Paper details to mention in the README if relevant:

- Laser scanner: RIEGL VUX-1HA
- INS system: IGI Compact MEMS (ROBIN)
- GNSS receiver: Septentrio Dual GNSS
- Camera: FLIR Grasshopper 3, 12MP
- LiDAR field of view: 360°
- Acquisition rate: 200 Hz
- Precision: 1 mm within a range of 119 m
- Systems mounted horizontally on top of a railborne flat wagon
- Acquisition height: 3.61 m
- Round trips were used to densify the point clouds
- Acquisition conditions: no rain/fog and sufficient daylight
- Minimum density target: one point every 5 cm per scan on a 20 m corridor centered on the acquisition system
- Acquisition over four days

## Dataset format

The point-cloud files are stored as `.laz` files.

Format details from the paper:

- LAS version: 1.2
- Point data format: type 3
- Stored attributes:
  - 3D coordinates
  - intensity
  - classification
  - color channels
  - GPS time

Each point cloud is saved in one `.laz` file.

Coordinate reference systems:

- planimetry (`X`, `Y`): EPSG:3950, ETRS89-FRA [RGF93 v1] / CC50 (formerly named RGF93 v1 / CC50);
- altimetry (`Z`): EPSG:5720, NGF-IGN69 height;
- CRS coordinate unit: metre;
- LAS XYZ scale factor: `0.001 0.001 0.001`, corresponding to 1 mm coordinate quantization.

For quick browser visualization, a `.laz` file can be loaded in [Plas.io](https://plas.io/). Point attributes such as scaled 3D coordinates, intensity, classification, color, and GPS time can be extracted with the Python `laspy` library (or `pylas` in existing workflows).

## Dataset organization

The dataset has 8 acquisition folders:

```text
ACQ_242_Aulnoye_Busigny/
ACQ_272_Lille_Douai/
ACQ_284_Lens_Ostricourt/
ACQ_286_Don_Lens/
ACQ_289_Don_Bethune/
ACQ_289_Lille_Don/
ACQ_295_Hazebrouck_Calais/
ACQ_301_Hazebrouck_Dunkerque/
```

Each acquisition folder contains:

```text
ACQ_xxx_Name/
  info/
    *.txt
  cloud/
    *.laz
```

`cloud/` contains the LiDAR point-cloud files.

`info/` contains text files with scan-level LAS/LAZ header information. These metadata files may include:

- LAS signature;
- LAS version;
- generating software;
- point data format;
- number of point records;
- scale factor;
- offset;
- min/max XYZ coordinates;
- GPS time range;
- RGB ranges;
- classification histogram.

## Dataset scale

Statistics from the associated paper:

| Acquisition / railway lane | Points, millions | Length, km | Number of tiles |
|---|---:|---:|---:|
| Aulnoye-Busigny | 1051.2 | 34.62 | 693 |
| Lille-Douai | 1496.0 | 43.01 | 861 |
| Lens-Ostricourt | 424.7 | 14.78 | 296 |
| Don-Lens | 435.4 | 16.13 | 323 |
| Don-Béthune | 686.8 | 23.09 | 463 |
| Lille-Don | 873.0 | 27.63 | 553 |
| Hazebrouck-Calais | 1689.1 | 60.73 | 1215 |
| Hazebrouck-Dunkerque | 1404.2 | 47.53 | 949 |
| Total | 8060.3 | 267.52 | 5353 |

The resulting point clouds have an average of approximately 1.5 million points per `.laz` file.

## Annotation

Manual point-wise annotation was performed tile by tile in 3D using CloudCompare.

The paper states that colorized point clouds were used to help annotators obtain consistent and geometrically reliable labels.

Each tile was verified by a different annotator.

## Classes

The dataset contains point-wise semantic labels.

Classes mentioned in the paper:

- Unclassified
- Ground
- Vegetation
- Building
- Catenary pole
- Rail
- Structure
- Catenary wire
- Level crossing gate, abbreviated as LCG

Important benchmark note:

The paper states that the `Unclassified` class was not included in the performance evaluation because it includes outliers, other structures and objects, and has high intra-class variation. Therefore, 8 classes instead of 9 were used during training and testing in the baseline experiments.

Numeric class IDs, verified from the classification histograms in all 5,353 `info/*.txt` files:

| ID | Class |
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

## Benchmark task

The associated paper proposes semantic segmentation of point clouds from a single LiDAR scan as the benchmark task.

Input features used in the paper:

- coordinates: x, y, z
- intensity: I

The methods estimate the semantic class of each input point.

## Preprocessing used in the paper

The following preprocessing steps were used in the paper baseline experiments:

- grid sampling with grid size 15 cm;
- cube crop with cubes of 10 m per side;
- intensity normalization to [0, 1] using 65535 as scale factor;
- coordinate scaling to [0, 1] within each 10 m cube;
- data augmentation for cubes containing rare classes such as LCG, catenary pole, or structure;
- fixed number of points per cube: N = 8192.

These details describe the paper benchmark protocol, not necessarily mandatory usage of the dataset.

## Data splits

The release includes original split files:

```text
splits/laz_files.csv
splits/train_ds.csv
splits/valid_ds.csv
splits/test_ds.csv
```

Interpretation:

- `laz_files.csv` contains the ordered list of all `.laz` files.
- `train_ds.csv`, `valid_ds.csv`, and `test_ds.csv` contain 0-based indices into `laz_files.csv`.
- The paths in `laz_files.csv` use Windows-style backslashes.

Observed split counts:

| Split | Count |
|---|---:|
| Train | 4068 |
| Validation | 1017 |
| Test | 268 |
| Total | 5353 |

The split files are disjoint and cover all 5353 scans.

This matches the protocol described in the paper:

- 95% of scans used for the training process;
- 5% reserved for testing;
- the 95% training-process subset is split into 80% model training and 20% validation.

Equivalent global proportions:

- train: approximately 76%
- validation: approximately 19%
- test: approximately 5%

## Intended Zenodo packaging

The intended Zenodo upload should use one ZIP archive per acquisition folder:

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

Each ZIP archive should preserve the internal folder structure:

```text
ACQ_xxx_Name/
  info/
  cloud/
```

The upload should also contain the supporting archive:

```text
RailCloud-HdF_v1.0_supporting_files.zip
```

This archive preserves the public release utilities and original split layout:

```text
splits/
  laz_files.csv
  train_ds.csv
  valid_ds.csv
  test_ds.csv
scripts/
  *.py
```

The release should also include:

```text
README.md
LICENSE.txt
CITATION.cff
metadata.json
file_manifest.csv
scan_manifest.csv
split_manifest.csv
split_summary.csv
acquisition_summary.csv
checksums_sha256.txt
```

## Git policy

Do not commit raw `.laz` files or generated ZIP archives.

The `data/` folder should be ignored by Git.

The `splits/`, `scripts/`, README, metadata, citation, license, and manifest files should be tracked.

## README wording constraints

Do not claim that the Zenodo DOI replaces the paper DOI.

Use this wording:

If you use RailCloud-HdF in your research, please cite the associated VISAPP 2024 paper. The Zenodo DOI identifies this archived dataset release and can be used to reference the exact dataset version.

Do not invent missing information; explicitly document any fields that still require completion.
