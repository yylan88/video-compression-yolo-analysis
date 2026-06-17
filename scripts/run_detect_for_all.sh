#!/bin/bash
# ============================================
# 自動對每個資料夾執行 YOLO detect
# ============================================

# ?? 根資料夾（要偵測的資料）
ROOT_DIR="/home/bobo/yyl/proj/original_video/drristd4/trim1/"

# ?? YOLO detect 腳本位置
YOLO_SCRIPT="/home/bobo/yolov7/detect.py"

# ?? 權重與輸出設定
WEIGHTS="/home/bobo/yolov7/runs/train/qp_gradual_final/weights/best.pt"
OUTPUT_BASE="/home/bobo/yyl/proj/detect_results_qpcurriculum_0.25_newlabel"

# ?? 其他偵測參數
CONF_THRES=0.25
EXTRA_ARGS="--save-txt --save-conf"

mkdir -p "$OUTPUT_BASE"

# ============================================
# 逐一處理子資料夾
# ============================================
for SUBDIR in "$ROOT_DIR"/*/; do
  [ -d "$SUBDIR" ] || continue
  BASENAME=$(basename "$SUBDIR")
  echo "=== ?? 處理資料夾: $BASENAME ==="

  # 檢查是否有圖片
  IMAGE_PATHS=($(find "$SUBDIR" -type f -name "*.png" | head -n 1))
  if [ -z "$IMAGE_PATHS" ]; then
    echo "?? 沒有找到圖片，跳過 $BASENAME"
    continue
  fi

  # 執行 YOLO detect
  python "$YOLO_SCRIPT" \
    --source "$SUBDIR" \
    --weights "$WEIGHTS" \
    --conf-thres "$CONF_THRES" \
    $EXTRA_ARGS \
    --project "$OUTPUT_BASE" \
    --name "$BASENAME" \
    --exist-ok

  echo "? 完成偵測：$BASENAME → 存到 $OUTPUT_BASE/$BASENAME"
done

echo "?? 全部資料夾偵測完成！"
