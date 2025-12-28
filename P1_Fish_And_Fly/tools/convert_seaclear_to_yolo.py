import os
import json
import random
from tqdm import tqdm
from shutil import copyfile

# ========================================================
# CONFIGURE PATHS
# ========================================================
ROOT = "data/Seaclear Marine Debris Dataset"
JSON_PATH = os.path.join(ROOT, "dataset.json")

YOLO_DIR = "data/yolo"
TRAIN_IMG = f"{YOLO_DIR}/images/train"
VAL_IMG = f"{YOLO_DIR}/images/val"
TRAIN_LBL = f"{YOLO_DIR}/labels/train"
VAL_LBL = f"{YOLO_DIR}/labels/val"

for d in [TRAIN_IMG, VAL_IMG, TRAIN_LBL, VAL_LBL]:
    os.makedirs(d, exist_ok=True)

# ========================================================
# YOUR CLASSES (SeaClear categories)
# Edit if needed
# ========================================================
classes = [
    "plastic", 
    "metal", 
    "rubber", 
    "cloth", 
    "other"
]

class_to_id = {c: i for i, c in enumerate(classes)}

# ========================================================
# LOAD JSON
# ========================================================
print("Loading dataset.json ...")
with open(JSON_PATH, "r") as f:
    data = json.load(f)

images_info = {img["id"]: img for img in data["images"]}

# Build annotation list grouped by image_id
ann_by_image = {}
for ann in data["annotations"]:
    img_id = ann["image_id"]
    if img_id not in ann_by_image:
        ann_by_image[img_id] = []
    ann_by_image[img_id].append(ann)

# ========================================================
# RECURSIVELY SCAN ALL IMAGES
# ========================================================
print("\nScanning image folders ...")

image_paths = {}
for root, dirs, files in os.walk(ROOT):
    for f_name in files:
        if f_name.lower().endswith(".jpg"):
            image_paths[f_name] = os.path.join(root, f_name)

print("Found", len(image_paths), "images.")

# ========================================================
# SPLIT TRAIN/VAL (80/20)
# ========================================================
all_ids = list(images_info.keys())
random.shuffle(all_ids)

split_idx = int(len(all_ids) * 0.8)
train_ids = set(all_ids[:split_idx])
val_ids = set(all_ids[split_idx:])

print(f"Train images: {len(train_ids)}")
print(f"Val images:   {len(val_ids)}")

# ========================================================
# CONVERT FUNCTION
# ========================================================
def coco_bbox_to_yolo(bbox, img_w, img_h):
    x, y, w, h = bbox
    cx = (x + w / 2) / img_w
    cy = (y + h / 2) / img_h
    nw = w / img_w
    nh = h / img_h
    return cx, cy, nw, nh

# ========================================================
# PROCESS IMAGES
# ========================================================
print("\nConverting annotations to YOLO format...")

for img_id in tqdm(images_info):
    
    img_info = images_info[img_id]
    file_name = img_info["file_name"]
    img_w = img_info["width"]
    img_h = img_info["height"]

    if file_name not in image_paths:
        print("WARNING: image not found:", file_name)
        continue

    # Choose train or val
    if img_id in train_ids:
        img_out = TRAIN_IMG
        lbl_out = TRAIN_LBL
    else:
        img_out = VAL_IMG
        lbl_out = VAL_LBL

    # Copy image
    src_path = image_paths[file_name]
    dst_path = os.path.join(img_out, file_name)
    copyfile(src_path, dst_path)

    # Write label
    label_path = os.path.join(lbl_out, file_name.replace(".jpg", ".txt"))
    with open(label_path, "w") as f:

        if img_id in ann_by_image:
            for ann in ann_by_image[img_id]:
                cls_id = ann["category_id"]
                cls_id = min(cls_id, len(classes)-1)

                bbox = ann["bbox"]
                cx, cy, w, h = coco_bbox_to_yolo(bbox, img_w, img_h)

                f.write(f"{cls_id} {cx} {cy} {w} {h}\n")

print("\nDONE! SeaClear is now converted to YOLO format.")
