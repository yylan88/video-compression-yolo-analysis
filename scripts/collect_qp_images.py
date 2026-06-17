#!/usr/bin/env python3
# collect_qp_images_with_label_whitelist.py
import argparse
import os
import re
import shutil
from pathlib import Path

IMG_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}
QP_DIR_RE = re.compile(r"(?:^|_)qp(\d+)$", re.IGNORECASE)

def is_image(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in IMG_EXTS

def safe_mkdir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def copy_or_link(src: Path, dst: Path, mode: str):
    if dst.exists():
        return "exists"
    if mode == "copy":
        shutil.copy2(src, dst)
        return "copied"
    elif mode == "symlink":
        os.symlink(src, dst)
        return "linked"
    else:
        raise ValueError(f"Unknown mode: {mode}")

def build_label_stems(labels_root: Path, label_ext: str = ".txt"):
    """
    Build a set of allowed stems based on label files.
    Example: label file '000601_2_1.txt' -> stem '000601_2_1'
    """
    stems = set()
    for p in labels_root.rglob(f"*{label_ext}"):
        if not p.is_file():
            continue
        name = p.name
        if name.lower().startswith("classes"):  # skip classes.txt
            continue
        stems.add(p.stem)
    return stems

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src_root", type=str, default="/home/bobo/yyl/proj/original_video",
                    help="Root folder containing dgristd2/ dgristd4/ ...")
    ap.add_argument("--labels_root", type=str, required=True,
                    help="Folder containing label .txt files (can be nested); whitelist is built from these")
    ap.add_argument("--dst_root", type=str, required=True,
                    help="New root folder to write QPxx/ folders into")
    ap.add_argument("--mode", type=str, default="copy", choices=["copy", "symlink"])
    ap.add_argument("--dry_run", action="store_true")
    ap.add_argument("--qp_min", type=int, default=15)
    ap.add_argument("--qp_max", type=int, default=51)
    ap.add_argument("--qp_step", type=int, default=2)
    args = ap.parse_args()

    src_root = Path(args.src_root)
    labels_root = Path(args.labels_root)
    dst_root = Path(args.dst_root)

    exclude = (src_root / "dgristd4" / "trim7").resolve()

    if not src_root.exists():
        raise SystemExit(f"[ERR] src_root not found: {src_root}")
    if not labels_root.exists():
        raise SystemExit(f"[ERR] labels_root not found: {labels_root}")

    # 1) Build whitelist from labels
    allowed_stems = build_label_stems(labels_root)
    print(f"[INFO] label whitelist size: {len(allowed_stems)}")

    safe_mkdir(dst_root)

    total_found = 0
    total_allowed = 0
    total_done = 0
    total_skipped_no_label = 0
    total_skipped_exists = 0

    per_qp_found = {}
    per_qp_allowed = {}
    per_qp_done = {}

    valid_qps = set(range(args.qp_min, args.qp_max + 1, args.qp_step))

    # 2) Walk all qp folders and copy ONLY images whose stem is in allowed_stems
    for dirpath in src_root.rglob("*"):
        if not dirpath.is_dir():
            continue

        # exclude dgristd4/trim7 subtree
        try:
            if exclude in dirpath.resolve().parents or dirpath.resolve() == exclude:
                continue
        except Exception:
            pass

        m = QP_DIR_RE.search(dirpath.name)
        if not m:
            continue

        qp = int(m.group(1))
        if qp not in valid_qps:
            continue

        qp_name = f"QP{qp:02d}"
        per_qp_found.setdefault(qp_name, 0)
        per_qp_allowed.setdefault(qp_name, 0)
        per_qp_done.setdefault(qp_name, 0)

        # scan recursively under qp folder
        img_files = [p for p in dirpath.rglob("*") if is_image(p)]
        if not img_files:
            continue

        dst_qp_dir = dst_root / qp_name
        safe_mkdir(dst_qp_dir)

        for img in img_files:
            total_found += 1
            per_qp_found[qp_name] += 1

            if img.stem not in allowed_stems:
                total_skipped_no_label += 1
                continue

            total_allowed += 1
            per_qp_allowed[qp_name] += 1

            dst = dst_qp_dir / img.name
            if args.dry_run:
                continue

            status = copy_or_link(img, dst, args.mode)
            if status == "exists":
                total_skipped_exists += 1
            else:
                total_done += 1
                per_qp_done[qp_name] += 1

    # Summary
    print("\n==== Summary ====")
    print(f"src_root: {src_root}")
    print(f"labels_root: {labels_root}")
    print(f"dst_root: {dst_root}")
    print(f"excluded: {exclude}")
    print(f"mode: {args.mode}")
    print(f"qp range: {args.qp_min}-{args.qp_max} step {args.qp_step}")
    print(f"total images scanned: {total_found}")
    print(f"total images with label: {total_allowed}")
    print(f"skipped (no label): {total_skipped_no_label}")
    if args.dry_run:
        print("(dry-run, nothing copied)")
    else:
        print(f"total done: {total_done}")
        print(f"skipped (already exists): {total_skipped_exists}")

    print("\nPer-QP:")
    for qp_name in sorted(per_qp_found.keys(), key=lambda s: int(s[2:])):
        f = per_qp_found[qp_name]
        a = per_qp_allowed[qp_name]
        d = per_qp_done[qp_name]
        if args.dry_run:
            print(f"  {qp_name}: scanned {f}, with_label {a}")
        else:
            print(f"  {qp_name}: scanned {f}, with_label {a}, done {d}")

if __name__ == "__main__":
    main()