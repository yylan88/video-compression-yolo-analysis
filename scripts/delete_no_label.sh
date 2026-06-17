#!/bin/bash
IMG_DIR="/home/bobo/yyl/proj/yolo_raw_dataset/qp43/"
LBL_DIR="/home/bobo/yyl/proj/yolo_raw_dataset/qp43/"

for img in "$IMG_DIR"/*.png; do
    base=$(basename "$img" .png)
    if [ ! -f "$LBL_DIR/$base.txt" ]; then
        echo "❌ 沒有標記檔，刪除：$img"
        rm "$img"
    fi
done

