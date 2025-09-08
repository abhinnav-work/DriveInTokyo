import os
import json
import argparse
from typing import Dict, List, Tuple


SUPPORTED_INPUT_EXTS = [
    ".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG",
]
WEBP_EXTS = [".webp", ".WEBP"]


def load_mapping(mapping_path: str) -> Dict[str, str]:
    if not os.path.isfile(mapping_path):
        raise FileNotFoundError(f"Mapping file not found: {mapping_path}")
    with open(mapping_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("mapping.json must contain a JSON object of { old_base: new_base }")
    return data


def find_matching_files(base_dir: str, base_name: str, exts: List[str]) -> List[str]:
    matches: List[str] = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            name, ext = os.path.splitext(file)
            if name == base_name and ext in exts:
                matches.append(os.path.join(root, file))
    return matches


def plan_renames(
    mapping: Dict[str, str],
    assets_dir: str,
    optimized_dir: str,
) -> List[Tuple[str, str]]:
    """
    Build a list of (src, dst) rename operations across assets (JPG/PNG) and
    assets_optimized (WEBP). Keeps original extension/case when renaming.
    """
    ops: List[Tuple[str, str]] = []

    for old_base, new_base in mapping.items():
        # Original assets: preserve extension
        orig_matches = find_matching_files(assets_dir, old_base, SUPPORTED_INPUT_EXTS)
        for src in orig_matches:
            _, ext = os.path.splitext(src)
            dst = os.path.join(os.path.dirname(src), f"{new_base}{ext}")
            if src != dst:
                ops.append((src, dst))

        # Optimized assets: webp only
        opt_matches = find_matching_files(optimized_dir, old_base, WEBP_EXTS)
        for src in opt_matches:
            _, ext = os.path.splitext(src)
            dst = os.path.join(os.path.dirname(src), f"{new_base}{ext}")
            if src != dst:
                ops.append((src, dst))

    return ops


def apply_renames(ops: List[Tuple[str, str]], dry_run: bool, force: bool) -> None:
    if not ops:
        print("No files matched the mapping. Nothing to rename.")
        return

    # Detect collisions: destination file already exists and not forcing
    for src, dst in ops:
        if os.path.exists(dst) and not force:
            print(f"⏭️  Skipping (exists): {dst} — use --force to overwrite")
            continue
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if dry_run:
            print(f"DRY-RUN: {src} -> {dst}")
        else:
            try:
                os.replace(src, dst)
                print(f"✅ {src} → {dst}")
            except Exception as e:
                print(f"⚠️  Failed to rename {src} → {dst}: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rename images in assets and assets_optimized based on mapping.json",
    )
    parser.add_argument(
        "--mapping",
        default=os.path.join("scripts", "mapping.json"),
        help="Path to mapping.json (default: scripts/mapping.json)",
    )
    parser.add_argument(
        "--assets",
        default="assets",
        help="Path to assets directory containing JPG/PNG (default: assets)",
    )
    parser.add_argument(
        "--optimized",
        default="assets_optimized",
        help="Path to optimized assets directory containing WEBP (default: assets_optimized)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned renames without changing files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite destination files if they already exist",
    )

    args = parser.parse_args()

    mapping = load_mapping(args.mapping)
    ops = plan_renames(mapping, args.assets, args.optimized)

    if not ops:
        print("No rename operations found. Check your mapping and directories.")
        return

    print(f"Planned operations: {len(ops)}")
    for src, dst in ops:
        print(f" - {src} → {dst}")

    apply_renames(ops, dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    main()


