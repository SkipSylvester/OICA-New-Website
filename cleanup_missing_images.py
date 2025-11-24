#!/usr/bin/env python3
"""
Cemetery Plot Image Cleanup Script
Removes non-existent image filenames from plots.csv

This script:
1. Reads plots.csv
2. Checks if each image file actually exists
3. Removes filenames that don't exist
4. Updates the CSV with only valid image filenames

Usage: python3 cleanup_missing_images.py [--dry-run]
"""

import csv
import os
from pathlib import Path

# Mapping of file prefixes to folder names
YARD_MAPPINGS = {
    'CY': 'OICA Church Yard',
    'IT': 'OICA Intervale',
    'NY': 'OICA New Yard',
    'OY': 'OICA Old Yard',
    'UT': 'OICA Upper Terrace'
}

def get_image_folder(filename):
    """Get the folder path for an image based on its prefix."""
    prefix = filename[:2].upper()
    folder_name = YARD_MAPPINGS.get(prefix, 'OICA Church Yard')
    return f"Monument Images/{folder_name}"

def check_image_exists(filename, base_path='Monument Images'):
    """Check if an image file actually exists."""
    folder = get_image_folder(filename)
    full_path = os.path.join(folder, filename)
    return os.path.exists(full_path)

def cleanup_csv(csv_path='data/plots.csv', dry_run=False):
    """
    Clean up plots.csv by removing non-existent image filenames.
    """
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

    # Track statistics
    total_images_checked = 0
    total_images_removed = 0
    plots_modified = 0

    # Process each row
    for row in rows:
        plot_id = row['plot_id']
        monument_images = row['monument_images'].strip()

        if not monument_images:
            continue

        # Parse image list
        images = [img.strip() for img in monument_images.split(';') if img.strip()]
        original_count = len(images)
        total_images_checked += original_count

        # Filter out non-existent images
        valid_images = []
        removed_images = []

        for img in images:
            if check_image_exists(img):
                valid_images.append(img)
            else:
                removed_images.append(img)
                total_images_removed += 1

        # Update row if changes were made
        if removed_images:
            plots_modified += 1
            new_value = '; '.join(valid_images) if valid_images else ''

            print(f"\nPlot {plot_id}:")
            print(f"  Removed {len(removed_images)} missing image(s):")
            for img in removed_images:
                print(f"    - {img}")
            if valid_images:
                print(f"  Kept {len(valid_images)} valid image(s)")
            else:
                print(f"  No images remaining")

            row['monument_images'] = new_value

    # Write back to CSV
    if not dry_run:
        if plots_modified > 0:
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

            print(f"\n{'='*60}")
            print(f"CSV updated successfully!")
            print(f"  Total images checked: {total_images_checked}")
            print(f"  Images removed: {total_images_removed}")
            print(f"  Plots modified: {plots_modified}")
            print(f"{'='*60}")
        else:
            print(f"\n{'='*60}")
            print(f"No missing images found - CSV is clean!")
            print(f"  Total images checked: {total_images_checked}")
            print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print(f"[DRY RUN] Would remove {total_images_removed} missing images from {plots_modified} plots")
        print(f"  Total images checked: {total_images_checked}")
        print(f"{'='*60}")

    return plots_modified

def main():
    import sys

    dry_run = '--dry-run' in sys.argv

    print("=" * 60)
    print("Cemetery Plot Image Cleanup")
    print("=" * 60)

    if dry_run:
        print("\n*** DRY RUN MODE - No changes will be made ***\n")

    print("Checking for missing image files...\n")

    plots_modified = cleanup_csv(dry_run=dry_run)

    if plots_modified == 0 and not dry_run:
        print("\nAll image references are valid!")

    print("\nDone!")

if __name__ == '__main__':
    main()
