import os
import argparse
from typing import Dict, List, Tuple


IMAGE_EXTS = [
    ".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG",
]


def scan_webp_structure(optimized_root: str) -> Dict[str, str]:
    """
    Return a mapping of base_name -> relative subfolder in optimized_root.
    Example: {"engine_hood": "landing", "accessory": "gallery"}
    Items found directly under optimized_root are mapped to "" (root).
    """
    mapping: Dict[str, str] = {}
    for root, _, files in os.walk(optimized_root):
        rel_dir = os.path.relpath(root, optimized_root)
        if rel_dir == ".":
            rel_dir = ""
        for file in files:
            name, ext = os.path.splitext(file)
            if ext.lower() == ".webp":
                mapping[name] = rel_dir
    return mapping


def find_originals_by_base(assets_root: str, base: str) -> List[str]:
    matches: List[str] = []
    for root, _, files in os.walk(assets_root):
        for file in files:
            name, ext = os.path.splitext(file)
            if name == base and ext in IMAGE_EXTS:
                matches.append(os.path.join(root, file))
    return matches


def plan_moves(assets_root: str, structure: Dict[str, str]) -> List[Tuple[str, str]]:
    ops: List[Tuple[str, str]] = []
    for base, rel_dir in structure.items():
        originals = find_originals_by_base(assets_root, base)
        for src in originals:
            dst_dir = os.path.join(assets_root, rel_dir) if rel_dir else assets_root
            dst = os.path.join(dst_dir, os.path.basename(src))
            if os.path.abspath(src) != os.path.abspath(dst):
                ops.append((src, dst))
    return ops


def apply_moves(ops: List[Tuple[str, str]], dry_run: bool) -> None:
    if not ops:
        print("No matching originals to move.")
        return
    for src, dst in ops:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if dry_run:
            print(f"DRY-RUN: {src} -> {dst}")
        else:
            try:
                os.replace(src, dst)
                print(f"✅ {src} → {dst}")
            except Exception as e:
                print(f"⚠️  Failed to move {src} → {dst}: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Mirror assets folder structure to match assets_optimized (by base filename)")
    parser.add_argument("--assets", default="assets", help="Path to original assets folder")
    parser.add_argument("--optimized", default="assets_optimized", help="Path to optimized assets folder")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")
    args = parser.parse_args()

    structure = scan_webp_structure(args.optimized)
    ops = plan_moves(args.assets, structure)

    print(f"Planned moves: {len(ops)}")
    for src, dst in ops:
        print(f" - {src} → {dst}")

    apply_moves(ops, dry_run=args.dry_run)


if __name__ == "__main__":
    main()


