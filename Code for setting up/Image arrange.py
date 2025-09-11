# import shutil
# from pathlib import Path

# # Paths
# images_dir = Path(r"E:\JEC Internship\Dataset\Img")
# out_dir = Path(r"E:\JEC Internship\Dataset\Small chars")

# # Build mapping only for lowercase a–z
# mapping = {37+i: chr(97+i) for i in range(26)}  # 37 -> a, 62 -> z

# # Process all images
# for file in images_dir.glob("*.png"):
#     try:
#         # Extract prefix number: e.g. "img037-001.png" -> 37
#         prefix = int(file.stem.split("-")[0].replace("img", ""))
        
#         # Check if it's in lowercase range
#         if prefix in mapping:
#             label = mapping[prefix]   # e.g. 37 -> 'a'
#             target_dir = out_dir / label
#             target_dir.mkdir(parents=True, exist_ok=True)
            
#             # Copy file into corresponding folder
#             shutil.copy(file, target_dir / file.name)
#             print(f"Copied {file.name} → {label}/")
#     except Exception as e:
#         print(f"Skipping {file.name}: {e}")


import os
import shutil
from pathlib import Path

# Paths
images_dir = Path(r"E:\JEC Internship\Dataset\Img")
out_dir = Path(r"E:\JEC Internship\Dataset\Capital chars and no.")

# Create output folder if not exists
out_dir.mkdir(parents=True, exist_ok=True)

# Mapping: imgXXX -> character
mapping = {}

# Digits 0–9 (img001–img010)
for i in range(1, 11):
    prefix = f"img{i:03d}"
    mapping[prefix] = str(i - 1)  # 1→0, 2→1, ...

# Capital A–Z (img011–img036)
for i, ch in enumerate(range(ord('A'), ord('Z') + 1), start=11):
    prefix = f"img{i:03d}"
    mapping[prefix] = chr(ch)

# Small a–z (img037–img062)
for i, ch in enumerate(range(ord('a'), ord('z') + 1), start=37):
    prefix = f"img{i:03d}"
    mapping[prefix] = chr(ch)

print("Mapping loaded for", len(mapping), "classes")

# Process images
for img_file in images_dir.glob("*.png"):
    prefix = img_file.stem.split("-")[0]  # e.g. img001
    if prefix not in mapping:
        print(f"Skipping {img_file.name} (no mapping)")
        continue

    label = mapping[prefix]  # e.g. "A" or "b"
    label_dir = out_dir / label
    label_dir.mkdir(parents=True, exist_ok=True)

    # Move/copy image
    shutil.copy(img_file, label_dir / img_file.name)

print("✅ Images have been arranged successfully!")
