import os
from PIL import Image

def convert_images_to_webp(input_folder, output_folder, quality=80):
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                input_path = os.path.join(root, file)

                # Preserve subfolder structure
                relative_path = os.path.relpath(root, input_folder)
                output_dir = os.path.join(output_folder, relative_path)
                os.makedirs(output_dir, exist_ok=True)

                # Save as .webp in optimized folder
                output_path = os.path.join(output_dir, os.path.splitext(file)[0] + ".webp")

                try:
                    img = Image.open(input_path).convert("RGB")  # RGBA → RGB
                    img.save(output_path, "webp", quality=quality)
                    print(f"✅ {input_path} → {output_path}")
                except Exception as e:
                    print(f"⚠️ Error converting {input_path}: {e}")

if __name__ == "__main__":
    convert_images_to_webp("assets", "assets_optimized", quality=80)
