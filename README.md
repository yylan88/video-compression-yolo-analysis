# Compression-Robust YOLOv7 for Smart Aquaculture Monitoring

## Overview

This research investigates how video compression affects YOLOv7 object detection performance in smart aquaculture monitoring systems.

The project focuses on identifying the maximum acceptable compression level that minimizes bandwidth and storage requirements while maintaining reliable shrimp detection accuracy.

Unlike conventional studies that only evaluate compression effects, this work further explores training strategies designed to improve robustness against compression artifacts.

---

## Research Motivation

Large-scale shrimp farms continuously generate video streams for:

- Shrimp counting
- Behavior monitoring
- Feeding analysis
- Long-term video recording

However, real-world deployment faces several challenges:

- Limited internet bandwidth
- Large storage requirements
- High transmission costs

Video compression provides an effective solution, but excessive compression may remove important visual features required by object detection models.

This project aims to find the optimal balance between:

- Detection Accuracy
- Bandwidth Consumption
- Storage Efficiency

---

## System Architecture

```text
Shrimp Farm Cameras
        │
        ▼
 Video Compression
        │
        ▼
 Video Streaming
        │
        ▼
 Laboratory Server
        │
        ▼
 YOLOv7 Detection
        │
        ▼
 Data Analysis & Storage
```

---

## Experimental Pipeline

```text
Original Video
        │
        ▼
Frame Extraction
        │
        ▼
QP Compression
(QP15 ~ QP51)
        │
        ▼
YOLOv7 Inference
        │
        ▼
Performance Evaluation
(mAP / IoU)
        │
        ▼
Compression Analysis
```

---

## Dataset

| Dataset | Images |
|----------|---------|
| Training | 509 |
| Validation | 219 |
| Testing | 116 |

---

## Compression Settings

Compression is controlled using the H.264 Quantization Parameter (QP).

| QP | Quality |
|-----|---------|
| 15 | Very High |
| 25 | High |
| 35 | Medium |
| 43 | Heavy Compression |
| 51 | Maximum Compression |

A total of 22 compression levels were evaluated.

```text
QP15 → QP51
```

---

# Baseline 1: Fixed-QP Training

Three independent YOLOv7 models were trained.

| Model | Training Data |
|---------|---------|
| QP15 Model | High-quality images |
| QP35 Model | Medium-compressed images |
| QP43 Model | Heavily-compressed images |

### Observations

#### QP15 Model

Advantages:

- Highest overall accuracy
- Best performance on clear images

Limitations:

- Performance drops rapidly under heavy compression

---

#### QP35 Model

Advantages:

- More robust against compression artifacts

Limitations:

- Slightly worse on clear images

---

#### QP43 Model

Advantages:

- Stable under severe compression

Limitations:

- Lower performance on high-quality images

---

## Key Observation

Although the QP15 model achieves the highest overall mAP, the QP35 and QP43 models show greater robustness under severe compression.

This raises an important research question:

> Can a model learn both clear-image features and compressed-image features simultaneously?

---

# Baseline 2: Mixed-QP Training

To improve robustness, multiple compression levels are combined during training.

### Strategy

Training samples are randomly drawn from:

```text
QP15 ~ QP51
```

during training.

### Advantages

- Exposure to multiple compression artifacts
- Better generalization across compression levels

### Limitation

High-QP images are introduced too early.

This may:

- Increase optimization difficulty
- Produce unstable gradients
- Slow feature learning

---

# Proposed Method: Curriculum Learning over QP

Instead of mixing all QP levels from the beginning, training difficulty is gradually increased.

The model first learns clear visual features and then progressively adapts to more challenging compressed images.

---

## Motivation

### Optimization Stability

High-QP images contain:

- Blur
- Blocking artifacts
- Loss of texture information

Introducing them too early may lead to poor convergence.

---

### Feature Learning Order

Low-QP images preserve:

- Edges
- Texture
- Shape information

These features should be learned first.

Compressed samples are introduced later to improve robustness.

---

## Curriculum Schedule

### Stage 1 (Epoch 1–99)

```text
90% QP15–20
10% QP21–25
```

### Stage 2 (Epoch 100–199)

```text
60% QP26–35
30% QP15–25
10% QP36–40
```

### Stage 3 (Epoch 200–300)

```text
60% QP41–45
30% QP15–40
10% QP46–51
```

---

## Evaluation Metrics

### IoU

Intersection over Union

Measures overlap between:

- Ground Truth Bounding Box
- Predicted Bounding Box

---

### AP

Average Precision

Area under the Precision-Recall Curve.

---

### mAP@0.5

Average AP using:

```text
IoU = 0.5
```

---

### mAP@0.5:0.95

Average AP over multiple IoU thresholds.

Provides a more comprehensive evaluation of detection quality.

---

# Results

## Compression Effect

Detection performance remains relatively stable under moderate compression.

A noticeable performance drop appears beyond:

```text
QP43
```

---

## Bandwidth Reduction

The proposed framework achieves:

```text
~4× bandwidth reduction
```

while maintaining acceptable detection performance.

---

## Mixed-QP vs Curriculum Learning

Curriculum Learning consistently outperforms Mixed-QP Training.

Benefits include:

- Higher mAP
- Higher IoU
- Better robustness at high QP levels

---

# Technologies

- Python
- PyTorch
- YOLOv7
- OpenCV
- FFmpeg
- Linux

---

# Future Work

- Reverse Curriculum Learning (Hard → Easy)
- Larger training datasets
- CRF-based compression analysis
- Real-world deployment in shrimp farms

---

# Author

Yu Ying Lan

Department of Computer Science and Engineering

National Sun Yat-Sen University

Embedded Systems Laboratory
