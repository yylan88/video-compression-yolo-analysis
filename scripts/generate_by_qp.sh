#!/bin/bash

REF_DATASET="/home/bobo/yyl/proj/yolo_dataset"
OUT_ROOT="/home/bobo/yyl/proj/yolo_dataset_qp"
TMPDIR="./tmp_qp_encode"
QP_LIST=(20 25 30 33 35 37 39 41 43 45)

# 建立暫存資料夾
mkdir -p "$TMPDIR"

for QP in "${QP_LIST[@]}"; do
  echo "產生 QP=$QP 資料集..."

  # 建立輸出資料夾
  for SPLIT in train val; do
    mkdir -p "$OUT_ROOT$QP/images/$SPLIT"
    mkdir -p "$OUT_ROOT$QP/labels/$SPLIT"

    # 複製標註檔（不需要壓縮）
    cp "$REF_DATASET/labels/$SPLIT/"*.txt "$OUT_ROOT$QP/labels/$SPLIT/"

    # 針對每張圖片壓縮
    for IMG in "$REF_DATASET/images/$SPLIT/"*; do
      IMG_NAME=$(basename "$IMG")
      TMP_MP4="$TMPDIR/tmp.mp4"
      TMP_OUT="$TMPDIR/frame.png"

      # 把單張圖片轉成壓縮影片（1 frame）
      ffmpeg -y -loglevel error -loop 1 -i "$IMG" -c:v libx264 -t 0.04 -qp $QP -preset slow -pix_fmt yuv420p "$TMP_MP4"

      # 從壓縮影片中擷取出圖片
      ffmpeg -y -loglevel error -i "$TMP_MP4" -frames:v 1 "$TMP_OUT"

      # 儲存成輸出目錄中的圖片
      cp "$TMP_OUT" "$OUT_ROOT$QP/images/$SPLIT/$IMG_NAME"
    done
  done

  echo "✅ 完成 QP=$QP 的壓縮版本"
done

# 清除暫存
rm -rf "$TMPDIR"

