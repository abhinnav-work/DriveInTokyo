import os
import json
import argparse
from typing import Dict, Any, Optional, Tuple

from PIL import Image


ASSETS_DIR_DEFAULT = "assets"
OPTIMIZED_DIR_DEFAULT = "assets_optimized"
MAPPING_PATH_DEFAULT = os.path.join("scripts", "mapping.json")
OUTPUT_METADATA_PATH_DEFAULT = os.path.join("scripts", "image_metadata.json")

SUPPORTED_ORIGINAL_EXTS = (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG")
SUPPORTED_OPTIMIZED_EXTS = (".webp", ".WEBP")


def load_mapping(mapping_path: str) -> Dict[str, Any]:
    with open(mapping_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def find_first_existing(base_dir: str, base_name: str, exts: Tuple[str, ...]) -> Optional[str]:
    """Find first existing file under base_dir recursively matching base_name with any of exts."""
    for root, _, files in os.walk(base_dir):
        for file in files:
            name, ext = os.path.splitext(file)
            if name == base_name and ext in exts:
                return os.path.join(root, file)
    return None


def get_image_size_bytes(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def get_image_dimensions(path: str) -> Optional[Tuple[int, int]]:
    try:
        with Image.open(path) as img:
            img.load()
            return img.width, img.height
    except Exception:
        return None


def suggest_layout(width: int, height: int) -> Dict[str, Any]:
    if width <= 0 or height <= 0:
        return {"rowSpan": 1, "colSpan": 1, "priority": "normal"}
    aspect = width / height
    orientation = "square"
    if aspect > 1.1:
        orientation = "landscape"
    elif aspect < 0.9:
        orientation = "portrait"

    # Simple heuristic for grid spans
    if orientation == "landscape":
        col_span = 2 if aspect >= 1.7 else 1
        row_span = 1
    elif orientation == "portrait":
        col_span = 1
        row_span = 2 if (1 / aspect) >= 1.6 else 1
    else:  # square-ish
        col_span = 1
        row_span = 1

    # Priority helps you feature some images in larger slots
    priority = "feature" if (orientation == "landscape" and aspect >= 2.0) else "normal"

    return {
        "rowSpan": row_span,
        "colSpan": col_span,
        "priority": priority,
    }


def build_metadata(
    mapping_path: str,
    assets_dir: str,
    optimized_dir: str,
) -> Dict[str, Any]:
    raw_mapping = load_mapping(mapping_path)
    # Extract rename map (str->str) only, ignore non-string values (like metadata blocks)
    mapping: Dict[str, str] = {k: v for k, v in raw_mapping.items() if isinstance(k, str) and isinstance(v, str)}

    # Build a set of candidate base names from both mapping values (preferred slugs)
    # and any webp filenames present in optimized dir.
    candidate_names = set(mapping.values())

    for root, _, files in os.walk(optimized_dir):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext in SUPPORTED_OPTIMIZED_EXTS:
                candidate_names.add(name)

    metadata: Dict[str, Any] = {}

    for base in sorted(candidate_names):
        opt_path = find_first_existing(optimized_dir, base, SUPPORTED_OPTIMIZED_EXTS)
        orig_path = find_first_existing(assets_dir, base, SUPPORTED_ORIGINAL_EXTS)

        # Prefer optimized image for dimensions; fallback to original
        dims = None
        src_used = None
        if opt_path:
            dims = get_image_dimensions(opt_path)
            src_used = "optimized"
        if (dims is None) and orig_path:
            dims = get_image_dimensions(orig_path)
            src_used = "original"

        width, height = (0, 0)
        aspect_ratio = None
        orientation = "unknown"

        if dims is not None:
            width, height = dims
            aspect_ratio = round(width / height, 4) if height > 0 else None
            if width == height:
                orientation = "square"
            elif width > height:
                orientation = "landscape"
            else:
                orientation = "portrait"

        layout = suggest_layout(width, height)

        entry = {
            "paths": {
                "optimized": opt_path,
                "original": orig_path,
                "sourceUsedForDimensions": src_used,
            },
            "width": width,
            "height": height,
            "bytes": get_image_size_bytes(opt_path) if opt_path else (get_image_size_bytes(orig_path) if orig_path else 0),
            "aspectRatio": aspect_ratio,
            "orientation": orientation,
            "layout": layout,
        }

        metadata[base] = entry

    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate image metadata and layout suggestions.")
    parser.add_argument("--mapping", default=MAPPING_PATH_DEFAULT, help="Path to mapping.json")
    parser.add_argument("--assets", default=ASSETS_DIR_DEFAULT, help="Path to assets directory")
    parser.add_argument("--optimized", default=OPTIMIZED_DIR_DEFAULT, help="Path to assets_optimized directory")
    parser.add_argument("--out", default=OUTPUT_METADATA_PATH_DEFAULT, help="Path to write image metadata JSON")
    parser.add_argument(
        "--merge-into-mapping",
        action="store_true",
        help="Also merge metadata into mapping.json under top-level 'metadata' keyed by slug",
    )
    args = parser.parse_args()

    meta = build_metadata(args.mapping, args.assets, args.optimized)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"✅ Wrote metadata for {len(meta)} images to {args.out}")

    if args.merge_into_mapping:
        mapping_doc = load_mapping(args.mapping)
        # Merge under top-level 'metadata'
        if not isinstance(mapping_doc, dict):
            mapping_doc = {}
        mapping_doc["metadata"] = meta
        with open(args.mapping, "w", encoding="utf-8") as f:
            json.dump(mapping_doc, f, indent=2, ensure_ascii=False)
        print(f"✅ Merged metadata into {args.mapping} under key 'metadata'")


if __name__ == "__main__":
    main()


