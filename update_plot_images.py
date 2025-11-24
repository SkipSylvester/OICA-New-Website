#!/usr/bin/env python3
"""
Cemetery Plot Image Updater
Scans image folders for new format images and updates plots.csv automatically.

New image format: ITC12-3F.jpg
- IT = Intervale Terrace (yard code)
- C12 = Plot C12 (plot identifier)
- 3 = Lot 3 (lot number)
- F = Front (image type: F=front, B=back, P=plaque, V=veteran)

Usage: python update_plot_images.py [--dry-run]
"""

import csv
import os
import re
from pathlib import Path
from collections import defaultdict

# Mapping of folder names to yard codes
YARD_MAPPINGS = {
    'OICA Church Yard': 'CY',
    'OICA Intervale': 'IT',
    'OICA New Yard': 'NY',
    'OICA Old Yard': 'OY',
    'OICA Upper Terrace': 'UT'
}

# Image type priority for sorting (F should appear before B)
IMAGE_TYPE_PRIORITY = {'F': 1, 'B': 2, 'P': 3, 'V': 4, '': 5}

def parse_new_format_filename(filename):
    """
    Parse new format filename and extract components.

    Format: ITC12-3F.jpg or ITC12-3.jpg
    Returns: (yard_code, plot_id, lot_number, image_type, full_filename)
    Returns None if filename doesn't match new format.
    """
    # Pattern: YardCode (2 chars) + PlotId + '-' + LotNumber + optional letters + optional ImageType + extension
    # Example: ITC12-3F.jpg, ITC12-3aF.jpg, ITC12-3.jpg
    # Yard codes are: IT, CY, NY, OY, UT (always 2 characters)
    pattern = r'^([A-Z]{2})([A-Z]?\d+)-(\d+)[a-z]*([FBPV])?\.jpe?g$'

    match = re.match(pattern, filename, re.IGNORECASE)
    if not match:
        return None

    yard_code = match.group(1).upper()
    plot_suffix = match.group(2).upper()
    lot_number = int(match.group(3))
    image_type = match.group(4).upper() if match.group(4) else ''

    # Construct plot_id (e.g., "ITC12")
    plot_id = f"{yard_code}{plot_suffix}"

    return (yard_code, plot_id, lot_number, image_type, filename)

def sort_images(image_list):
    """
    Sort images by lot number (descending) and image type priority.
    Lot 5 appears first (leftmost), Lot 1 appears last (rightmost).
    Within same lot: F before B before P before V.
    """
    def get_sort_key(img):
        parsed = parse_new_format_filename(img)
        if parsed:
            _, _, lot_num, img_type, _ = parsed
            # Negative lot number for descending sort (higher lots first)
            # Image type priority for secondary sort
            return (-lot_num, IMAGE_TYPE_PRIORITY.get(img_type, 99))
        else:
            # Old format images go to the end
            return (0, 99)

    return sorted(image_list, key=get_sort_key)

def scan_images(base_path='Monument Images'):
    """
    Scan all image folders and find new format images.
    Returns dict: {plot_id: [list of new image filenames]}
    """
    new_images = defaultdict(list)

    if not os.path.exists(base_path):
        print(f"Warning: '{base_path}' directory not found!")
        return new_images

    for folder_name, yard_code in YARD_MAPPINGS.items():
        folder_path = os.path.join(base_path, folder_name)

        if not os.path.exists(folder_path):
            print(f"Warning: Folder '{folder_path}' not found, skipping...")
            continue

        print(f"Scanning {folder_name}...")

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg')):
                parsed = parse_new_format_filename(filename)

                if parsed:
                    yard, plot_id, lot_num, img_type, full_name = parsed

                    # Verify yard code matches folder
                    if yard == yard_code:
                        new_images[plot_id].append(full_name)
                        print(f"  Found: {full_name} -> Plot {plot_id}, Lot {lot_num}")
                    else:
                        print(f"  Warning: {full_name} has yard code {yard} but is in {yard_code} folder")

    return new_images

def update_plots_csv(csv_path='data/plots.csv', new_images_dict=None, dry_run=False):
    """
    Update plots.csv with new images.
    Preserves existing images and adds new ones.
    """
    if new_images_dict is None:
        new_images_dict = {}

    if not os.path.exists(csv_path):
        print(f"Error: CSV file '{csv_path}' not found!")
        return

    # Read existing CSV
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    # Track updates
    updates_made = 0

    # Update rows with new images
    for row in rows:
        plot_id = row['plot_id']

        if plot_id in new_images_dict:
            # Get existing images
            existing = row['monument_images'].strip() if row['monument_images'] else ''
            existing_list = [img.strip() for img in existing.split(';') if img.strip()]

            # Get new images for this plot
            new_imgs = new_images_dict[plot_id]

            # Combine and deduplicate (case-insensitive)
            existing_lower = {img.lower() for img in existing_list}
            combined = existing_list.copy()

            for new_img in new_imgs:
                if new_img.lower() not in existing_lower:
                    combined.append(new_img)
                    existing_lower.add(new_img.lower())

            # Sort combined list
            sorted_images = sort_images(combined)

            # Update row
            new_value = '; '.join(sorted_images)

            if new_value != existing:
                print(f"\nPlot {plot_id}:")
                print(f"  Before: {existing if existing else '(empty)'}")
                print(f"  After:  {new_value}")
                row['monument_images'] = new_value
                updates_made += 1

    # Write back to CSV
    if not dry_run:
        # Create backup
        backup_path = csv_path + '.backup'
        if os.path.exists(csv_path):
            import shutil
            shutil.copy2(csv_path, backup_path)
            print(f"\nBackup created: {backup_path}")

        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(rows)

        print(f"\nCSV updated successfully! {updates_made} plots modified.")
    else:
        print(f"\n[DRY RUN] Would update {updates_made} plots (no changes made)")

    return updates_made

def main():
    import sys

    dry_run = '--dry-run' in sys.argv

    print("=" * 60)
    print("Cemetery Plot Image Updater")
    print("=" * 60)

    if dry_run:
        print("\n*** DRY RUN MODE - No changes will be made ***\n")

    # Scan for new images
    print("\n1. Scanning image folders for new format images...")
    new_images = scan_images()

    if not new_images:
        print("\nNo new format images found.")
        return

    print(f"\nFound new images for {len(new_images)} plots")

    # Update CSV
    print("\n2. Updating plots.csv...")
    updates_made = update_plots_csv(new_images_dict=new_images, dry_run=dry_run)

    if updates_made == 0:
        print("\nNo updates needed - all images already in CSV.")

    print("\nDone!")

if __name__ == '__main__':
    main()
