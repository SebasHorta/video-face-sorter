# Face Sorter Pro

Automated desktop tool to detect, cluster, and sort faces from videos to speed up editorial workflows.

- **Cut manual review time by ~70%** for professional videographers  
- **Desktop UI** built with customtkinter  
- **Accurate embeddings** via face_recognition  
- **High-throughput video I/O** with OpenCV and performance optimizations

---

## 🔍 Features

- **Automated Face Detection** across video frames
- **Embedding Extraction** with face_recognition
- **Clustering & Grouping** to organize by unique identities
- **Batch Processing** with robust error handling
- **Frame Skipping** for long videos
- **Export** per-person folders and optional CSV/JSON metadata

---

## 🧠 How It Works

- **Frame Sampling:** Processes every Nth frame for speed.  
- **Detection & Embeddings:** Uses face_recognition to generate 128-d embeddings.  
- **Clustering:** Groups similar embeddings (e.g., DBSCAN/KMeans).  
- **Export:** Cropped faces, thumbnails, and cluster metadata.

---

## 🛠 Tech Stack

- UI: customtkinter (Python)
- Video: OpenCV
- Face Processing: face_recognition (dlib under the hood)
- Clustering: scikit-learn
- Language: Python 3.10+

---

## 📦 Setup

1. Clone repository
   ```bash
   git clone https://github.com/SebasHorta/video-face-sorter.git
   cd video-face-sorter
   ```

2. Create and activate virtual environment
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

   - macOS (Apple Silicon) may require `xcode-select --install` and `brew install cmake` for dlib/face_recognition.

---

## 🚀 Run

- Launch the desktop app (adjust the entry file if different):
  ```bash
  python face_sorter_backend.py
  ```
  If your entry point is named differently (e.g., `main.py`), run that file instead.

- Typical flow:
  - Select one or more videos
  - Choose output directory
  - Set frame skip (e.g., 5–10)
  - Start processing and review clusters
  - Export per-identity folders and/or metadata

---

## ⚙️ Configuration

- Frame skip (sampling interval)
- Batch size
- Minimum faces per cluster
- Output options: crops, thumbnails, CSV/JSON
- Clustering parameters (e.g., eps/min_samples for DBSCAN)

These may be toggled in the UI or via config/args if available.

---

## 📁 Output Structure (example)

```
output/
├── clusters/
│   ├── person_000/
│   ├── person_001/
│   └── ...
├── thumbnails/
│   ├── person_000.jpg
│   └── person_001.jpg
└── metadata/
    ├── clusters.json
    └── faces.csv
```

---

## 🧪 Example (CLI, if exposed)

```bash
python face_sorter_backend.py \
  --video /path/to/video.mp4 \
  --out ./output \
  --frame-skip 8 \
  --min-cluster-size 3 \
  --batch-size 64
```

If your script exposes different flags, update the example accordingly.

---

## ⚡ Performance Notes

- Frame skipping reduces compute on long clips
- Batching improves embedding throughput
- Graceful error handling for corrupt frames/streams
- Observed ~70% reduction in manual review time

---

## 🔧 Troubleshooting

- face_recognition/dlib build issues (macOS):
  - `xcode-select --install`
  - `brew install cmake` (and optionally `brew install boost`)
  - Refer to official dlib/face_recognition docs for platform notes

- No faces detected:
  - Lower frame skip
  - Ensure adequate lighting and resolution

- Over-fragmented clusters:
  - Tune clustering parameters (e.g., increase eps, reduce cluster count)
  - Increase minimum samples per cluster

---

## 📈 Roadmap

- Active learning with user labeling
- Identity persistence across projects
- GPU acceleration when available
- Timeline overlays for face presence
- Export EDL/XML for NLEs (Premiere/Resolve)
- Multi-process decoding for long-form media

---

## 📜 License

MIT License — see LICENSE for details.

---

## 🙌 Acknowledgments

Built with customtkinter, OpenCV, face_recognition, and scikit-learn.  
Designed and developed by @SebasHorta.
