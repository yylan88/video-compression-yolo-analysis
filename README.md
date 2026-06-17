# Video Compression Impact on YOLOv7 Detection

## Overview

This project investigates how video compression affects YOLOv7 object detection performance in smart aquaculture monitoring systems.

The goal is to identify the maximum acceptable compression level that significantly reduces bandwidth and storage requirements while maintaining reliable detection accuracy.

---

## Research Motivation

Large-scale shrimp farm monitoring systems continuously generate video streams.

Challenges:

- Limited network bandwidth
- Large storage requirements
- Long-term video archival costs

Video compression can greatly reduce resource consumption, but excessive compression may degrade object detection performance.

This project evaluates the trade-off between compression efficiency and detection accuracy.

---

## Experimental Setup

### Detection Model

- YOLOv7
- Input Size: 640 × 640
- Epochs: 300
- Batch Size: 16

### Dataset

| Split | Images |
|---------|---------|
| Training | 509 |
| Validation | 219 |
| Testing | 116 |

### Compression Levels

QP values:

```
15 ~ 51
```

22 compression levels were evaluated.

---

## Models

Three YOLOv7 models were trained:

| Model | Training Data |
|---------|---------|
| QP15 Model | High-quality images |
| QP35 Model | Medium compression |
| QP43 Model | Heavy compression |

Additionally:

- Mixed-QP Training
- Multi-QP Random Sampling

were evaluated to improve robustness.

---

## Evaluation Metrics

- IoU
- AP
- mAP@0.5
- mAP@0.5:0.95

---

## Key Findings

### Compression vs Detection

- Detection accuracy remains relatively stable under moderate compression.
- Significant degradation appears beyond QP43.
- QP43 is a critical operating point.

### Bandwidth Savings

- Nearly 4× bandwidth reduction
- Maintain acceptable detection performance

### Mixed-QP Training

- Better robustness under high compression
- No noticeable accuracy loss under low compression

---

## Technologies

- Python
- YOLOv7
- PyTorch
- OpenCV
- FFmpeg
- Linux

---

## Future Work

- Curriculum Learning over QP
- CRF-based evaluation
- Larger datasets
- Real-world deployment validation

---

## Author

Yu Ying Lan

National Sun Yat-Sen University

Embedded Systems Laboratory
