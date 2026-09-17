#!/usr/bin/env python3
"""Auto-segmentation tool for CVAT Day 5 lab tasks.

Runs AI model inference (SegFormer for semantic, YOLOv8-seg for instance/panoptic)
and generates ready-to-import CVAT ZIP packages in submissions/<task_name>.zip.

Usage:
  python scripts/auto_segment.py <task_name>   # e.g. easy_semantic, medium_instance, hard_panoptic
  python scripts/auto_segment.py --all          # generate submissions for all tasks in manifest.json
"""
import argparse
import io
import json
import os
import sys
import zipfile
import numpy as np
import torch
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Cityscapes ID mapping to standard semantic labels
CITYSCAPES_MAP = {
    0:  "road",
    1:  "sidewalk",
    2:  "building",
    3:  "building",     # wall -> building
    4:  "building",     # fence -> building
    8:  "vegetation",
    9:  "vegetation",   # terrain -> vegetation
    10: "sky",
}

def load_manifest():
    manifest_path = ROOT / "data" / "manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)["tasks"]

def get_task_info(task_name, manifest):
    if task_name not in manifest:
        raise ValueError(f"Task '{task_name}' not found in manifest.json. Known tasks: {list(manifest.keys())}")
    info = manifest[task_name]
    task_dir = ROOT / "data" / info["path"]
    classes_path = task_dir / "classes.json"
    images_dir = task_dir / "images"
    
    with open(classes_path, "r", encoding="utf-8") as f:
        classes_data = json.load(f)
        
    return info, task_dir, images_dir, classes_data

def run_semantic_auto_segment(task_name, images_dir, classes_data, zip_path):
    """Run SegFormer for semantic segmentation and save CVAT 'Segmentation mask 1.1' ZIP."""
    from transformers import AutoImageProcessor, AutoModelForSemanticSegmentation
    
    MODEL_ID = "nvidia/segformer-b0-finetuned-cityscapes-1024-1024"
    print(f"[{task_name}] Loading SegFormer model ({MODEL_ID})...", flush=True)
    processor = AutoImageProcessor.from_pretrained(MODEL_ID)
    model = AutoModelForSemanticSegmentation.from_pretrained(MODEL_ID)
    model.eval()

    target_classes = classes_data.get("classes", [])
    colors = classes_data.get("colors", {})
    
    # Generate labelmap.txt content
    labelmap_lines = ["# CVAT palette"]
    for cname in target_classes:
        rgb = colors.get(cname, [128, 128, 128])
        labelmap_lines.append(f"{cname}:{rgb[0]},{rgb[1]},{rgb[2]}::")
    labelmap_content = "\n".join(labelmap_lines) + "\n"

    image_paths = sorted(list(images_dir.glob("*.jpg")))
    print(f"[{task_name}] Found {len(image_paths)} images.", flush=True)

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("labelmap.txt", labelmap_content.encode("utf-8"))
        
        for img_path in image_paths:
            img = Image.open(img_path).convert("RGB")
            w, h = img.size
            
            inputs = processor(images=img, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                upsampled_logits = torch.nn.functional.interpolate(
                    logits, size=(h, w), mode="bilinear", align_corners=False
                )
                pred_labels = upsampled_logits.argmax(dim=1)[0].cpu().numpy()
            
            rgb_mask = np.zeros((h, w, 3), dtype=np.uint8)
            
            for city_id, mapped_name in CITYSCAPES_MAP.items():
                if mapped_name in target_classes:
                    target_rgb = colors[mapped_name]
                    mask = (pred_labels == city_id)
                    rgb_mask[mask] = target_rgb

            mask_img = Image.fromarray(rgb_mask)
            img_byte_arr = io.BytesIO()
            mask_img.save(img_byte_arr, format='PNG')
            
            arc_name = f"SegmentationClass/{img_path.stem}.png"
            zf.writestr(arc_name, img_byte_arr.getvalue())
            print(f"  + Generated {arc_name}", flush=True)

    print(f"[{task_name}] Saved 'Segmentation mask 1.1' submission to {zip_path}", flush=True)

def run_instance_auto_segment(task_name, images_dir, classes_data, zip_path):
    """Run YOLOv8-seg for instance/panoptic segmentation and save CVAT 'COCO 1.0' ZIP."""
    import cv2
    from ultralytics import YOLO
    
    print(f"[{task_name}] Loading YOLOv8-seg model...", flush=True)
    model = YOLO("yolov8n-seg.pt")
    
    target_classes = classes_data.get("classes", [])
    image_paths = sorted(list(images_dir.glob("*.jpg")))
    
    coco_images = []
    coco_categories = []
    coco_annotations = []
    
    cat_name_to_id = {}
    for i, cname in enumerate(target_classes, 1):
        cat_name_to_id[cname] = i
        coco_categories.append({"id": i, "name": cname, "supercategory": ""})
        
    ann_id = 1
    
    for img_idx, img_path in enumerate(image_paths, 1):
        img_pil = Image.open(img_path)
        w, h = img_pil.size
        
        coco_images.append({
            "id": img_idx,
            "file_name": img_path.name,
            "height": h,
            "width": w
        })
        
        results = model.predict(source=str(img_path), conf=0.25, verbose=False)[0]
        
        if results.masks is not None:
            boxes = results.boxes
            masks = results.masks.xy  # list of polygon coordinates
            
            for box, poly in zip(boxes, masks):
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = model.names[cls_id]
                
                # Check if class matches target classes or alias
                matched_target = None
                if cls_name in cat_name_to_id:
                    matched_target = cls_name
                elif cls_name in ["car", "bus", "truck", "motorcycle", "bicycle"] and "vehicle" in cat_name_to_id:
                    matched_target = "vehicle"
                
                if not matched_target or len(poly) < 3:
                    continue
                
                flattened_poly = poly.flatten().tolist()
                
                x_coords = poly[:, 0]
                y_coords = poly[:, 1]
                x_min, y_min = float(np.min(x_coords)), float(np.min(y_coords))
                bbox_w, bbox_h = float(np.max(x_coords) - x_min), float(np.max(y_coords) - y_min)
                
                # Calculate polygon area via Shoelace formula
                x = poly[:, 0]
                y = poly[:, 1]
                area = float(0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))))
                
                coco_annotations.append({
                    "id": ann_id,
                    "image_id": img_idx,
                    "category_id": cat_name_to_id[matched_target],
                    "segmentation": [flattened_poly],
                    "area": area,
                    "bbox": [x_min, y_min, bbox_w, bbox_h],
                    "iscrowd": 0
                })
                ann_id += 1
                
        print(f"  + Processed {img_path.name}: generated annotations", flush=True)
        
    coco_json = {
        "images": coco_images,
        "categories": coco_categories,
        "annotations": coco_annotations
    }
    
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("annotations/instances.json", json.dumps(coco_json, indent=2).encode("utf-8"))
        
    print(f"[{task_name}] Saved 'COCO 1.0' submission to {zip_path}", flush=True)

def process_task(task_name, manifest):
    info, task_dir, images_dir, classes_data = get_task_info(task_name, manifest)
    task_type = info["type"]
    zip_path = ROOT / "submissions" / f"{task_name}.zip"
    
    print(f"\n==========================================")
    print(f"  Processing Task: {task_name} (type: {task_type})")
    print(f"==========================================")
    
    if task_type == "semantic":
        run_semantic_auto_segment(task_name, images_dir, classes_data, zip_path)
    else:
        run_instance_auto_segment(task_name, images_dir, classes_data, zip_path)
        
    # Verify generated submission
    import subprocess
    inspect_script = ROOT / "scripts" / "inspect_submissions.py"
    subprocess.run([sys.executable, str(inspect_script), "--task", task_name])
    
    fmt = "Segmentation mask 1.1" if task_type == "semantic" else "COCO 1.0"
    rel_zip = zip_path.relative_to(ROOT)
    print(f"\n[INSTRUCTION] Steps to review & edit in CVAT:")
    print(f"  1. Open CVAT -> Task '{task_name}' -> Actions -> Upload annotations")
    print(f"  2. Select format '{fmt}'")
    print(f"  3. Upload file '{rel_zip}'")
    print(f"  4. Review, edit masks in CVAT UI, Save & Export!\n")

def main():
    parser = argparse.ArgumentParser(description="Auto-segment images for Day 5 lab tasks and generate CVAT ZIPs.")
    parser.add_argument("task", nargs="?", help="Task name (e.g. easy_semantic, medium_instance, hard_panoptic)")
    parser.add_argument("--all", action="store_true", help="Process all tasks in manifest.json")
    args = parser.parse_args()
    
    manifest = load_manifest()
    
    if args.all:
        for tname in manifest.keys():
            process_task(tname, manifest)
    elif args.task:
        process_task(args.task, manifest)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
