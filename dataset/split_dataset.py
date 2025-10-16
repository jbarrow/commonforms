import csv
import shutil
import sys
from pathlib import Path


def read_csv_ids(csv_path):
    ids = []
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                id_value = row[0].strip()
                ids.append(id_value)
    return ids


def read_all_filenames(coco_dir):
    """Read all filenames once into arrays"""
    images_dir = coco_dir / 'images'
    json_dir = coco_dir / 'json'

    # Get all filenames as lists
    image_files = [f for f in images_dir.iterdir() if f.is_file()]
    json_files = [f for f in json_dir.iterdir() if f.is_file()]

    return image_files, json_files


def build_file_lookup(image_files, json_files):
    from collections import defaultdict

    image_lookup = defaultdict(list)
    json_lookup = defaultdict(list)

    for img_file in image_files:
        # Extract ID from filename (ID-pagenumber.ext pattern)
        id_value = img_file.name.split('-')[0]
        image_lookup[id_value].append(img_file)

    for json_file in json_files:
        # Extract ID from filename (ID-pagenumber.ext pattern)
        id_value = json_file.name.split('-')[0]
        json_lookup[id_value].append(json_file)

    return image_lookup, json_lookup


def move_files(source_files, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    moved_count = 0

    for file_path in source_files:
        dest_path = dest_dir / file_path.name
        try:
            shutil.move(str(file_path), str(dest_path))
            moved_count += 1
            print(f"Moved: {file_path.name}")
        except Exception as e:
            print(f"Error moving {file_path}: {e}")

    return moved_count


def main():
    coco_dir = Path(sys.argv[1])

    # Validate inputs
    if not coco_dir.exists():
        print(f"Error: Directory '{coco_dir}' does not exist")
        return 1

    images_dir = coco_dir / 'images'
    json_dir = coco_dir / 'json'

    if not images_dir.exists() or not json_dir.exists():
        print(f"Error: Directory must contain 'images' and 'json' subdirectories")
        return 1

    # Read CSV files
    test_csv = Path('test.csv')
    val_csv = Path('val.csv')

    if not test_csv.exists() or not val_csv.exists():
        print("Error: test.csv and val.csv must exist in current directory")
        return 1

    print(f"Reading test IDs from {test_csv}...")
    test_ids = read_csv_ids(test_csv)
    print(f"Found {len(test_ids)} test IDs")

    print(f"\nReading validation IDs from {val_csv}...")
    val_ids = read_csv_ids(val_csv)
    print(f"Found {len(val_ids)} validation IDs")

    # Create test and val directories as siblings to coco_dir
    test_dir = coco_dir.parent / 'test'
    val_dir = coco_dir.parent / 'val'

    test_images_dir = test_dir / 'images'
    test_json_dir = test_dir / 'json'
    val_images_dir = val_dir / 'images'
    val_json_dir = val_dir / 'json'

    # Read all filenames once into memory and build lookup
    print("\nReading all filenames from coco directory...")
    image_files, json_files = read_all_filenames(coco_dir)
    print(f"Found {len(image_files)} images and {len(json_files)} JSON files")

    print("Building file lookup index...")
    image_lookup, json_lookup = build_file_lookup(image_files, json_files)
    print(f"Indexed {len(image_lookup)} unique image IDs and {len(json_lookup)} unique JSON IDs")

    # Process test files
    print("\n" + "="*60)
    print("Processing TEST files...")
    print("="*60)
    test_image_count = 0
    test_json_count = 0

    for id_value in test_ids:
        matching_images = image_lookup.get(id_value, [])
        matching_json = json_lookup.get(id_value, [])
        if matching_images or matching_json:
            test_image_count += move_files(matching_images, test_images_dir)
            test_json_count += move_files(matching_json, test_json_dir)

    # Process validation files
    print("\n" + "="*60)
    print("Processing VALIDATION files...")
    print("="*60)
    val_image_count = 0
    val_json_count = 0

    for id_value in val_ids:
        matching_images = image_lookup.get(id_value, [])
        matching_json = json_lookup.get(id_value, [])
        if matching_images or matching_json:
            val_image_count += move_files(matching_images, val_images_dir)
            val_json_count += move_files(matching_json, val_json_dir)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Test images moved: {test_image_count}")
    print(f"Test JSON files moved: {test_json_count}")
    print(f"Validation images moved: {val_image_count}")
    print(f"Validation JSON files moved: {val_json_count}")

    return 0


if __name__ == '__main__':
    main()
