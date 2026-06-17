#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil

# ===== 可調 =====
TXT_DIR = "/home/bobo/yyl/proj/yolo_raw_dataset/qp_curriculum/qp43"   
IMG_BASE_ROOT = "/home/bobo/yyl/proj/original_video"
IMAGE_EXT = ".png"
TARGET_QP = "qp43"    # ← 只選這個 QP，ex: qp15 / qp27 / qp35 / qp43 ...

def build_frame_index(img_root, target_qp):
    """
    走訪 IMG_BASE_ROOT 下所有 .png
    但只收集檔案路徑中包含指定 QP 的圖片
    建立： frame_name.png -> [完整路徑1, ...]
    """
    index = {}
    for root, dirs, files in os.walk(img_root):
        if target_qp not in root:
            continue  # 不含指定 QP，就跳過

        for f in files:
            if not f.lower().endswith(IMAGE_EXT):
                continue

            img_path = os.path.join(root, f)
            index.setdefault(f, []).append(img_path)

    return index


def main():
    print(f"[INFO] 正在掃描 {IMG_BASE_ROOT} (只取包含 {TARGET_QP} 的圖片)")

    frame_index = build_frame_index(IMG_BASE_ROOT, TARGET_QP)
    print(f"[INFO] 建立索引：共有 {len(frame_index)} 種不同圖片 (QP={TARGET_QP})")

    txt_files = [f for f in os.listdir(TXT_DIR) if f.endswith(".txt")]
    print(f"[INFO] 發現 {len(txt_files)} 個 txt 準備處理")

    for txt_name in txt_files:
        frame_name = txt_name.replace(".txt", "")
        png_name = frame_name + IMAGE_EXT

        if png_name not in frame_index:
            print(f"[WARN] 沒找到 {png_name} (QP={TARGET_QP}) ─ 跳過")
            continue

        # 此時候選應該只有一個或少數
        src = frame_index[png_name][0]   # 直接拿第一個，不 random
        dst = os.path.join(TXT_DIR, png_name)

        shutil.copy2(src, dst)
        print(f"[OK] {txt_name} -> 複製 {src} → {dst}")

    print("[DONE] 全部處理完畢！")


if __name__ == "__main__":
    main()
