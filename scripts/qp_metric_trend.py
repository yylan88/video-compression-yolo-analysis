# -*- coding: utf-8 -*-
"""
計算 detect_results 各 QP 與 baseline (QP15) 的辨識表現變化
輸出:
  - mAP@0.5
  - mAP@0.5:0.95
  - mean IoU
  - 結果圖與 CSV
"""

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import csv

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

# ============================================================
# 主函式：計算 mAP 與 mean IoU
# ============================================================
# ============================================================
# 主函式：計算 mAP 與 mean IoU
# ============================================================
def calc_metrics(gt_dir, pred_dir):
    """
    計算 mAP@0.5、mAP@0.5:0.95、mean IoU
    加入：
      - Recall 排序 (確保遞增)
      - Precision 累積最大化 (確保單調遞減)
      - 避免 np.trapz 積分負值
    """
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

                # 根據 conf threshold 過濾預測
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

                # 收集 TP IoU 值
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

        # === ������ 修正部分 ===
        if len(precisions) > 1:
            precisions = np.array(precisions)
            recalls = np.array(recalls)
            order = np.argsort(recalls)
            recalls = recalls[order]
            precisions = precisions[order]
            # 確保 precision 單調遞減（COCO 作法）
            precisions = np.maximum.accumulate(precisions[::-1])[::-1]
            ap = np.trapz(precisions, recalls)
        else:
            ap = 0.0

        ap_list.append(ap)

    mean_iou = np.mean(all_ious) if all_ious else 0
    map50 = ap_list[0]             # IoU=0.5
    map5095 = np.mean(ap_list)     # IoU=0.5~0.95 平均
    return map50, map5095, mean_iou


# ============================================================
# 主程式
# ============================================================
ROOT = Path("/home/bobo/yyl/proj/detect_results_curriculum_0.25/")
BASE_GT = ROOT / "frames_qp15" / "labels"  # baseline
if not BASE_GT.exists():
    raise FileNotFoundError(f"❌ Baseline labels not found: {BASE_GT}")

metrics = {'QP': [], 'mAP@0.5': [], 'mAP@0.5:0.95': [], 'meanIoU': []}

# 自動偵測 frames_qpXX 資料夾
for subdir in sorted(ROOT.glob("frames_qp*/")):
    pred_dir = subdir / "labels"
    if not pred_dir.exists():
        continue
    qp = int(subdir.name.replace("frames_qp", ""))
    print(f"=== QP={qp} ===")
    map50, map5095, miou = calc_metrics(BASE_GT, pred_dir)
    metrics['QP'].append(qp)
    metrics['mAP@0.5'].append(map50)
    metrics['mAP@0.5:0.95'].append(map5095)
    metrics['meanIoU'].append(miou)
    print(f"→ mAP@0.5={map50:.4f}, mAP@0.5:0.95={map5095:.4f}, meanIoU={miou:.4f}")

# ============================================================
# 畫圖
# ============================================================
plt.figure(figsize=(8,6))
plt.plot(metrics['QP'], metrics['mAP@0.5'], 'o-', label='mAP@0.5')
plt.plot(metrics['QP'], metrics['mAP@0.5:0.95'], 's-', label='mAP@0.5:0.95')
plt.plot(metrics['QP'], metrics['meanIoU'], '^-', label='mean IoU')
plt.xlabel("QP (Compression Level)")
plt.ylabel("Metric Value")
plt.title("YOLO Detection Performance vs QP (baseline=QP15) curriculum")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("detect_qp_vs_metrics_qpcurriculum.png", dpi=200)
print("✅ Saved plot: detect_qp_vs_metricscurriculum.png")

# ============================================================
# 輸出 CSV
# ============================================================
with open("detect_qpcurriculum_metrics.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["QP", "mAP@0.5", "mAP@0.5:0.95", "meanIoU"])
    for i in range(len(metrics['QP'])):
        writer.writerow([
            metrics['QP'][i],
            metrics['mAP@0.5'][i],
            metrics['mAP@0.5:0.95'][i],
            metrics['meanIoU'][i],
        ])
print("✅ Saved CSV: detect_qp_metricscurriculum.csv")
