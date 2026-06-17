#!/bin/bash

SRC_DIR="/home/bobo/yyl/proj/yolo_dataset/qpgradual/qp15/images/train/"
OUTFILE="/home/bobo/yyl/proj/epoch/stage1.txt"

mkdir -p "$(dirname "$OUTFILE")"
> "$OUTFILE"

find "$SRC_DIR" -type f -name "*.png" | sort >> "$OUTFILE"

echo "已完成：所有 PNG 路徑已輸出到 $OUTFILE"
