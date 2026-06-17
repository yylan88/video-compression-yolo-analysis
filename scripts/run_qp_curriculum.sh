#!/bin/bash
set -e

IMG_SIZE=640
BATCH=16
DEVICE=0
PROJECT=runs/train
EXP=shrimp_qp_gradual

# Phase 1: QP15
python train.py \
  --data "/home/bobo/yolov7/data/data_qp15.yaml" \
  --weights yolov7.pt \
  --epochs 100 \
  --name ${EXP}_phase1 \
  

P1=${PROJECT}/${EXP}_phase1/weights/last.pt

# Phase 2: QP35
python train.py \
  --data "/home/bobo/yolov7/data/data_qp30.yaml" \
  --weights $P1 \
  --epochs 100 \
  --name ${EXP}_phase2 \


P2=${PROJECT}/${EXP}_phase2/weights/last.pt

# Phase 3: QP mix
python train.py \
  --data "/home/bobo/yolov7/data/data_qp43.yaml" \
  --weights $P2 \
  --epochs 100 \
  --name ${EXP}_phase3 \
 

echo "Done. Final model: ${PROJECT}/${EXP}_phase3/weights/best.pt"
