import json
import os
import sys
from pathlib import Path


def merge_coco_annotations():
    """Merge individual JSON files into a single COCO format annotations file"""
    coco_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("coco")
    json_dir = coco_dir / "json"
    output_file = coco_dir / "annotations.json"

    # COCO format structure
    coco_data = {
            "info": {
                "year": 2025,
                "version": "1.0",
                "description": "Form field detection dataset",
                "contributor": "",
                "url": "",
                "date_created": "2025-10-16"
            },
            "licenses": [
                {
                    "id": 1,
                    "name": "Unknown",
                    "url": ""
                }
            ],
            "images": [],
            "annotations": [],
            "categories": [
                {"id": 0, "name": "Text", "supercategory": "none"},
                {"id": 1, "name": "CheckBox", "supercategory": "none"}
                ]
            }

    # Get all JSON files sorted by name
    json_files = sorted(json_dir.glob("*.json"))

    image_id = 0
    annotation_id = 0

    for json_file in json_files:
        with json_file.open("r") as fp:
            page_data = json.load(fp)

        # Add image with sequential ID
        image_info = page_data["image"].copy()
        image_info["id"] = image_id
        coco_data["images"].append(image_info)

        # Track seen bounding boxes for this page to skip duplicates
        seen_bboxes = set()

        # Add annotations with sequential IDs and image_id reference
        for annotation in page_data["annotations"]:
            if json_file.name.startswith("2908641"):
                continue

            # Round bounding box to integers
            bbox = annotation["bbox"]
            bbox_int = [round(bbox[0]), round(bbox[1]), round(bbox[2]), round(bbox[3])]

            # Skip if any x or y coordinate is negative
            if bbox_int[0] < 0 or bbox_int[1] < 0:
                continue

            # Skip if bbox extends beyond image boundaries
            if (bbox_int[0] + bbox_int[2] > image_info["width"] or
                bbox_int[1] + bbox_int[3] > image_info["height"]):
                continue

            # Calculate area from rounded bounding box
            area_int = bbox_int[2] * bbox_int[3]

            bbox_tuple = tuple(bbox_int)

            # Skip if this bounding box was already added for this page
            if bbox_tuple in seen_bboxes:
                continue

            seen_bboxes.add(bbox_tuple)
            annotation_copy = annotation.copy()
            annotation_copy["id"] = annotation_id
            annotation_copy["image_id"] = image_id
            annotation_copy["bbox"] = bbox_int
            annotation_copy["area"] = area_int
            coco_data["annotations"].append(annotation_copy)
            annotation_id += 1

        image_id += 1

    # Save merged COCO format file
    with output_file.open("w") as fp:
        json.dump(coco_data, fp, indent=2)

    print(f"Merged {len(coco_data['images'])} images with {len(coco_data['annotations'])} annotations")
    print(f"Saved to {output_file}")

    # Create symlink in images folder
    images_dir = coco_dir / "images"
    symlink_path = images_dir / "_annotations.coco.json"

    # Remove existing symlink if it exists
    if symlink_path.exists() or symlink_path.is_symlink():
        symlink_path.unlink()

    # Create relative symlink
    os.symlink(os.path.relpath(output_file, images_dir), symlink_path)
    print(f"Created symlink at {symlink_path}")


if __name__ == "__main__":
    merge_coco_annotations()
