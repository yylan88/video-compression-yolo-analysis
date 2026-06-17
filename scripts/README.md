# Scripts

This folder contains the core scripts used in the video compression and YOLOv7 detection experiments.

The scripts cover four major stages:

1. Dataset preparation
2. Video compression
3. Object detection evaluation
4. Result analysis

---

# Workflow

```text
Original Video
      │
      ▼
Video Compression
(generate_by_qp.sh)
      │
      ▼
Frame Extraction
(generate_qp_frames_folder.sh)
      │
      ▼
Dataset Construction
(collect_qp_images.py)
      │
      ▼
YOLOv7 Detection
(run_detect_for_all.sh)
      │
      ▼
Metric Analysis
(qp_metric_trend.py)
(qp_metric_crossmodel.py)
      │
      ▼
Performance Comparison
```

---

# Dataset Preparation

## collect_qp_images.py

Collect images generated from different QP levels and organize them into YOLO datasets.

Purpose:

- Build fixed-QP datasets
- Build Mixed-QP datasets
- Build Curriculum datasets

---

## copy_qp_images.py

Copy images from selected QP folders into a new training dataset.

---

## split_dataset.sh

Split images into:

```text
train
validation
test
```

sets for YOLO training.

---

## delete_no_label.sh

Remove images without corresponding YOLO labels.

---

# Video Compression

## generate_by_qp.sh

Generate compressed videos using different H.264 QP values.

Compression range:

```text
QP15 ~ QP51
```

Purpose:

- Create datasets under different compression levels.
- Analyze the impact of compression on detection performance.

---

## generate_qp_frames_folder.sh

Extract frames from compressed videos.

Output:

```text
QP15 Frames
QP17 Frames
QP19 Frames
...
QP51 Frames
```

---

## get_video_bitrate.sh

Calculate bitrate information for compressed videos.

Used for:

- Bandwidth analysis
- Compression-performance tradeoff evaluation

---

# Detection Evaluation

## run_detect_for_all.sh

Run YOLOv7 detection on all QP datasets automatically.

Purpose:

- Batch evaluation
- Generate prediction results
- Collect performance metrics

---

## run_qp_curriculum.sh

Training script for Curriculum Learning experiments.

Curriculum stages:

### Stage 1

```text
QP15–20
```

### Stage 2

```text
QP26–40
```

### Stage 3

```text
QP41–51
```

The model gradually learns from easy samples to difficult samples.

---

# Performance Analysis

## qp_metric_trend.py

Analyze performance trends across different compression levels.

Metrics:

- mAP@0.5
- mAP@0.5:0.95
- Mean IoU

Outputs:

- Compression-performance curves
- Bandwidth-performance curves

---

## qp_metric_crossmodel.py

Compare multiple YOLOv7 models trained under different QP conditions.

Models:

- QP15 Model
- QP35 Model
- QP43 Model
- Mixed-QP Model
- Curriculum Learning Model

Purpose:

- Cross-model comparison
- Robustness evaluation

---

# Additional Utilities

## collect_png_paths.sh

Generate image path lists for dataset processing.

---

# Research Contributions

This project extends traditional compression-performance analysis by introducing:

- Fixed-QP Training
- Mixed-QP Training
- Curriculum Learning over Compression Levels

The proposed Curriculum Learning strategy demonstrates improved robustness under severe video compression conditions while maintaining high detection accuracy.
