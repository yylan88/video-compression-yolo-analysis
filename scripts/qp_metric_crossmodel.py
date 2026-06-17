# -*- coding: utf-8 -*-
"""
QP-based compression vs YOLO detection performance
Includes:
  - mAP@0.5
  - mAP@0.5:0.95
  - mean IoU
  - weighted average bitrate
"""

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import csv

# ============================================================
# ������ 實驗名稱（只要改這一行）
# ============================================================

EXP_TAG = "qpmix"

# ============================================================
# QP → weighted average bitrate (bit/s)
# ============================================================

QP_BITRATE = {
    15: 30453064.91,
    17: 24336628.03,
    19: 19383027.47,
    21: 15618308.96,
    23: 12318620.49,
    25: 9706831.96,
    27: 7174100.86,
    29: 5138437.14,
    31: 3800010.92,
    33: 2597034.94,
    35: 1733314.18,
    37: 1188326.10,
    39: 756054.46,
    41: 481320.00,
    43: 334641.16,
    45: 219813.71,
    47: 146765.74,
    49: 107448.32,
    51: 76451.48,
}

# ============================================================
# 共用函式
# ============================================================

def compute_iou_matrix(boxes1, boxes2):
    if len(boxes1) == 0 or len(boxes2) == 0:
        return np.zeros((len(boxes1), len(boxes2)))
    inter_x1 = np.maximum(boxes1[:, None, 0], boxes2[:, 0])
    inter_y1 = np.maximum(boxes1[:, None, 1], boxes2[:, 1])
    inter_x2 = np.minimum(boxes1[:, None, 2], boxes2[:, 2])
    inter_y2 = np.minimum(boxes1[:, None, 3], boxes2[:, 3])
    inter_w = np.clip(inter_x2 - inter_x1, 0, None)
    inter_h = np.clip(inter_y2 - inter_y1, 0, None)
    inter_area = inter_w * inter_h
    area1 = (boxes1[:, 2] - boxes1[:, 0]) * (boxes1[:, 3] - boxes1[:, 1])
    area2 = (boxes2[:, 2] - boxes2[:, 0]) * (boxes2[:, 3] - boxes2[:, 1])
    union = area1[:, None] + area2 - inter_area
    return inter_area / (union + 1e-6)

def xywh_to_xyxy(boxes):
    out = boxes.copy()
    out[:, 0] = boxes[:, 0] - boxes[:, 2] / 2
    out[:, 1] = boxes[:, 1] - boxes[:, 3] / 2
    out[:, 2] = boxes[:, 0] + boxes[:, 2] / 2
    out[:, 3] = boxes[:, 1] + boxes[:, 3] / 2
    return out

def load_yolo_txt(path):
    labels = []
    with open(path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            x, y, w, h = map(float, parts[1:5])
            conf = float(parts[5]) if len(parts) > 5 else 1.0
            labels.append([x, y, w, h, conf])
    return np.array(labels, dtype=np.float32)

def match_and_eval(gt_boxes, pred_boxes, iou_thr=0.5):
    if len(gt_boxes) == 0 and len(pred_boxes) == 0:
        return 0, 0, 0
    if len(pred_boxes) == 0:
        return 0, 0, len(gt_boxes)
    if len(gt_boxes) == 0:
        return 0, len(pred_boxes), 0

    ious = compute_iou_matrix(gt_boxes[:, :4], pred_boxes[:, :4])
    matched = set()
    tp = 0
    for j in range(pred_boxes.shape[0]):
        best_iou = 0
        best = -1
        for i in range(gt_boxes.shape[0]):
            if i in matched:
                continue
            if ious[i, j] > best_iou:
                best_iou = ious[i, j]
                best = i
        if best_iou >= iou_thr:
            tp += 1
            matched.add(best)

    fp = pred_boxes.shape[0] - tp
    fn = gt_boxes.shape[0] - tp
    return tp, fp, fn

def calc_metrics(gt_dir, pred_dir):
    iou_thresholds = np.arange(0.5, 1.0, 0.05)
    ap_list = []
    all_ious = []

    for iou_thr in iou_thresholds:
        thresholds = np.linspace(0, 1, 21)
        precisions, recalls = [], []

        for thr in thresholds:
            TP = FP = FN = 0
            iou_acc = []

            for gt_file in gt_dir.glob("*.txt"):
                pred_file = pred_dir / gt_file.name
                if not pred_file.exists():
                    continue

                gt = load_yolo_txt(gt_file)
                pred = load_yolo_txt(pred_file)

                if len(pred) > 0:
                    pred = pred[pred[:, 4] >= thr]

                if len(gt) == 0 and len(pred) == 0:
                    continue

                gt_xy = xywh_to_xyxy(gt[:, :4])
                pr_xy = xywh_to_xyxy(pred[:, :4])

                ious = compute_iou_matrix(gt_xy, pr_xy)
                tp, fp, fn = match_and_eval(gt_xy, pr_xy, iou_thr)
                TP += tp
                FP += fp
                FN += fn

                for gi in range(len(gt_xy)):
                    if len(pr_xy) == 0:
                        continue
                    best_iou = ious[gi].max()
                    if best_iou >= iou_thr:
                        iou_acc.append(best_iou)

            if TP + FP + FN == 0:
                continue

            P = TP / (TP + FP + 1e-6)
            R = TP / (TP + FN + 1e-6)

            precisions.append(P)
            recalls.append(R)

            if iou_acc:
                all_ious.extend(iou_acc)

        if len(precisions) > 1:
            precisions = np.array(precisions)
            recalls = np.array(recalls)
            order = np.argsort(recalls)
            recalls = recalls[order]
            precisions = precisions[order]
            precisions = np.maximum.accumulate(precisions[::-1])[::-1]
            ap = np.trapz(precisions, recalls)
        else:
            ap = 0.0

        ap_list.append(ap)

    return ap_list[0], np.mean(ap_list), np.mean(all_ious) if all_ious else 0

# ============================================================
# 主程式
# ============================================================

BASELINE_PATH = Path("/home/bobo/yyl/proj/from_dgristd_label/new_gt/")
TARGET_ROOT = Path("/home/bobo/yyl/proj/detect_results_qpmix_0.25_newlabel/")

metrics = {'QP': [], 'bitrate': [], 'mAP@0.5': [], 'mAP@0.5:0.95': [], 'meanIoU': []}

for subdir in sorted(TARGET_ROOT.glob("dgristd4_trim1_qp*/")):
    pred_dir = subdir / "labels"
    if not pred_dir.exists():
        continue

    qp = int(subdir.name.replace("dgristd4_trim1_qp", ""))
    map50, map5095, miou = calc_metrics(BASELINE_PATH, pred_dir)

    metrics['QP'].append(qp)
    metrics['bitrate'].append(QP_BITRATE.get(qp))
    metrics['mAP@0.5'].append(map50)
    metrics['mAP@0.5:0.95'].append(map5095)
    metrics['meanIoU'].append(miou)

# ============================================================
# 繪圖
# ============================================================

fig, ax1 = plt.subplots(figsize=(8,6))
ax1.plot(metrics['QP'], metrics['mAP@0.5'], 'o-', label='mAP@0.5')
ax1.plot(metrics['QP'], metrics['mAP@0.5:0.95'], 's-', label='mAP@0.5:0.95')
ax1.plot(metrics['QP'], metrics['meanIoU'], '^-', label='mean IoU')
ax1.set_xlabel("QP")
ax1.set_ylabel("Detection Performance")
ax1.grid(True)

ax2 = ax1.twinx()
ax2.plot(metrics['QP'], metrics['bitrate'], 'k--', label='Bitrate')
ax2.set_ylabel("Bitrate (bit/s)")
ax2.set_yscale("log")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2)

plt.title("Detection Performance vs QP with Bitrate")
plt.tight_layout()
plt.savefig(f"detect_qp_gtqp_metrics_{EXP_TAG}.png", dpi=200)

# ============================================================
# CSV
# ============================================================

with open(f"detect_qp_gt_metrics_{EXP_TAG}.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["QP", "bitrate", "mAP@0.5", "mAP@0.5:0.95", "meanIoU"])
    for i in range(len(metrics['QP'])):
        writer.writerow([
            metrics['QP'][i],
            metrics['bitrate'][i],
            metrics['mAP@0.5'][i],
            metrics['mAP@0.5:0.95'][i],
            metrics['meanIoU'][i],
        ])

print(f"✅ Done: detect_qp_gt_metrics_{EXP_TAG}.png & CSV generated")
