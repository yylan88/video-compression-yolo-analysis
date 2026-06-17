#!/bin/bash
# ============================================
# 單支或多支影片皆可處理的版本
# ============================================

# 輸入影片路徑（可以是單一影片或資料夾）
VIDDIR="/home/bobo/yyl/proj/dgristd4_qp15_rec2.mp4"
# 輸出根資料夾
OUTDIR="/home/bobo/yyl/proj/extract_video/"

# 建立輸出根資料夾
mkdir -p "$OUTDIR"

# 自動產生 QP 值列表（17～51，每次加 2）
QP_LIST=()
for ((qp=15; qp<=51; qp+=2)); do
  QP_LIST+=($qp)
done

# ============================================
# 決定影片清單
# ============================================
if [ -d "$VIDDIR" ]; then
  # 如果是資料夾，就取裡面的所有 mp4
  VIDEO_LIST=("$VIDDIR"/*.mp4)
elif [ -f "$VIDDIR" ]; then
  # 如果是單一影片，就只處理這支
  VIDEO_LIST=("$VIDDIR")
else
  echo "❌ 找不到影片或資料夾: $VIDDIR"
  exit 1
fi

# ============================================
# 逐支影片處理
# ============================================
for VID in "${VIDEO_LIST[@]}"; do
  [ -e "$VID" ] || continue
  BASENAME=$(basename "$VID" .mp4)
  echo "=== 處理影片: $BASENAME ==="

  # 每個 QP 版本
  for QP in "${QP_LIST[@]}"; do
    echo " -> QP=$QP"
    TMP_FILE="$OUTDIR/$BASENAME/tmp_qp${QP}.mp4"
    OUT_PATH="$OUTDIR/$BASENAME/frames_qp${QP}"
    mkdir -p "$OUT_PATH"

    # 重新編碼影片（壓縮）
    ffmpeg -y -i "$VID" -c:v libx264 -qp $QP -preset medium -pix_fmt yuv420p "$TMP_FILE"

    # 抽幀
    ffmpeg -y -i "$TMP_FILE" -vf "fps=1" "$OUT_PATH/%06d.png"

    # 刪除暫存影片
    rm -f "$TMP_FILE"
  done

  echo "完成 $BASENAME → 存到 $OUTDIR/$BASENAME"
done

echo "✅ 所有影片處理完成，結果在 $OUTDIR/"
