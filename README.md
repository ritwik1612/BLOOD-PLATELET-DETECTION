# BPD - current application source

This folder contains the BPD 2.3.0 application source, configuration, runtime model weights, and installer build scripts.

**Use the app:** double-click `RUN BPD.cmd`, or open `..\BPD App\BPD.exe`.
**Install it:** open `..\BPD App\Installer\BPD-Setup-2.3.0.exe`.

| Location | Contents |
| --- | --- |
| `desktop_launcher.py` | Native Windows application entry point |
| `web_app/` | Interface HTML, CSS, JavaScript and legacy local API |
| `inference/` | Existing detection and morphology pipeline |
| `models/` | YOLO loader and autoencoder architecture |
| `anomaly_detection/` | Runtime score calculation |
| `feature_extraction/`, `training/`, `utils/` | Required model-loading and utility modules |
| `configs/` | Active settings plus baseline training/data configuration |
| `outputs/weights/` | Four runtime artifacts; no image datasets |
| `installer/`, `BPD.spec` | Installer assets and build definitions |

The active inference settings are `configs/anomaly.yaml` and `configs/yolo.yaml`.
Older experiments and build caches are under `..\ALT`. Documentation audits are under `..\..\DOCS\WORKSPACE AUDITS\BPD`.
The full source/build guide is `..\..\DOCS\INFORMATIVE\BPD SOURCE GUIDE.md`.

## Run from source

Create a Python 3.10 environment, install `requirements.txt`, then run `python desktop_launcher.py`.
The packaged Windows app needs neither a Python installation nor the research datasets.

[Source repository](https://github.com/ritwik1612/BLOOD-PLATELET-DETECTION) · [Windows installer](https://github.com/ritwik1612/BLOOD-PLATELET-DETECTION/releases/tag/v2.3.0)
