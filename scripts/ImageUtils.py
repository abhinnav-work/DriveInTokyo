import os
import argparse
from PIL import Image

SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg")


def _has_alpha(image: Image.Image) -> bool:
    mode = image.mode
    return mode in ("LA", "RGBA", "PA") or (mode == "P" and "transparency" in image.info)


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _convert_one_image(input_path: str, output_path: str, quality: int = 80) -> None:
    try:
        with Image.open(input_path) as img:
            img.load()  # ensure image is loaded before mode checks
            if _has_alpha(img):
                converted = img.convert("RGBA")
                converted.save(output_path, "webp", quality=quality)
            else:
                converted = img.convert("RGB")
                converted.save(output_path, "webp", quality=quality)
        print(f"✅ {input_path} → {output_path}")
    except Exception as e:
        print(f"⚠️ Error converting {input_path}: {e}")


def convert_images_to_webp(input_path: str, output_folder: str, quality: int = 80) -> None:
    """
    Convert images to WebP.

    - If input_path is a directory, recursively convert all supported images, preserving subfolders into output_folder.
    - If input_path is a file, convert only that file into output_folder.
    """

    # Ensure output folder exists
    _ensure_dir(output_folder)

    if os.path.isfile(input_path):
        # Single file conversion
        file = os.path.basename(input_path)
        if not file.lower().endswith(SUPPORTED_EXTENSIONS):
            print(f"⏭️ Skipping unsupported file: {input_path}")
            return
        output_path = os.path.join(output_folder, os.path.splitext(file)[0] + ".webp")
        _convert_one_image(input_path, output_path, quality)
        return

    # Directory conversion
    for root, _, files in os.walk(input_path):
        for file in files:
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                src = os.path.join(root, file)
                # Preserve subfolder structure
                relative_path = os.path.relpath(root, input_path)
                out_dir = os.path.join(output_folder, relative_path)
                _ensure_dir(out_dir)
                out_path = os.path.join(out_dir, os.path.splitext(file)[0] + ".webp")
                _convert_one_image(src, out_path, quality)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert images (file or directory) to WebP.")
    parser.add_argument("input", nargs="?", default="assets", help="Input file or directory")
    parser.add_argument("output", nargs="?", default="assets_optimized", help="Output directory for WebP files")
    parser.add_argument("--quality", type=int, default=80, help="WebP quality (0-100)")
    args = parser.parse_args()

    convert_images_to_webp(args.input, args.output, quality=args.quality)
