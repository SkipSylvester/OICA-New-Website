#!/usr/bin/env python3
"""
Image Verification Script for OICA Cemetery
Checks that all images referenced in plots.csv actually exist in the Monument Images folder
Reports missing images and broken references
"""

import csv
import os
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
PLOTS_CSV = BASE_DIR / 'data' / 'plots.csv'
IMAGES_DIR = BASE_DIR / 'Monument Images'

# Folder mapping from cemetery-viewer.html
FOLDER_MAP = {
    'CY': 'OICA Church Yard',
    'IT': 'OICA Intervale Terrace',
    'NY': 'OICA New Yard',
    'OY': 'OICA Old Yard',
    'UT': 'OICA Upper Terrace'
}

def get_section_prefix(plot_id):
    """Extract section prefix from plot_id (e.g., 'CYA1' -> 'CY')"""
    if len(plot_id) >= 2:
        return plot_id[:2].upper()
    return None

def parse_images(images_str):
    """Parse the monument_images field into individual filenames"""
    if not images_str or images_str.strip() == '':
        return []
    return [img.strip() for img in images_str.split(';') if img.strip()]

def verify_images():
    """Verify all images referenced in plots.csv exist"""

    print("=" * 80)
    print("OICA Cemetery - Image Verification Report")
    print("=" * 80)
    print()

    # Statistics
    total_plots = 0
    plots_with_images = 0
    plots_without_images = 0
    total_image_refs = 0
    missing_images = []
    valid_images = []
    unknown_sections = []

    # Read plots.csv
    with open(PLOTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        plots = list(reader)

    total_plots = len(plots)

    # Check each plot
    for plot in plots:
        plot_id = plot['plot_id']
        images_str = plot.get('monument_images', '')

        image_list = parse_images(images_str)

        if image_list:
            plots_with_images += 1
            total_image_refs += len(image_list)

            # Determine which folder to check
            section = get_section_prefix(plot_id)

            if section not in FOLDER_MAP:
                unknown_sections.append((plot_id, section))
                continue

            folder_name = FOLDER_MAP[section]
            folder_path = IMAGES_DIR / folder_name

            # Check if folder exists
            if not folder_path.exists():
                for img in image_list:
                    missing_images.append({
                        'plot_id': plot_id,
                        'image': img,
                        'reason': f'Folder not found: {folder_name}'
                    })
                continue

            # Check each image
            for img in image_list:
                image_path = folder_path / img

                if image_path.exists():
                    valid_images.append({
                        'plot_id': plot_id,
                        'image': img,
                        'path': str(image_path.relative_to(BASE_DIR))
                    })
                else:
                    missing_images.append({
                        'plot_id': plot_id,
                        'image': img,
                        'expected_path': str(image_path.relative_to(BASE_DIR))
                    })
        else:
            plots_without_images += 1

    # Print summary
    print(f"Total Plots: {total_plots}")
    print(f"Plots with Images: {plots_with_images}")
    print(f"Plots without Images: {plots_without_images}")
    print(f"Total Image References: {total_image_refs}")
    print(f"Valid Images Found: {len(valid_images)}")
    print(f"Missing Images: {len(missing_images)}")
    print()

    # Report missing images
    if missing_images:
        print("=" * 80)
        print("MISSING IMAGES")
        print("=" * 80)
        print()

        for item in missing_images:
            print(f"Plot: {item['plot_id']}")
            print(f"  Image: {item['image']}")
            if 'expected_path' in item:
                print(f"  Expected Path: {item['expected_path']}")
            if 'reason' in item:
                print(f"  Reason: {item['reason']}")
            print()
    else:
        print("✓ All referenced images exist!")
        print()

    # Report unknown sections
    if unknown_sections:
        print("=" * 80)
        print("UNKNOWN SECTION PREFIXES")
        print("=" * 80)
        print()

        for plot_id, section in unknown_sections:
            print(f"Plot: {plot_id}, Section: {section}")
        print()

    # Summary by section
    print("=" * 80)
    print("SUMMARY BY SECTION")
    print("=" * 80)
    print()

    section_stats = {}
    for plot in plots:
        plot_id = plot['plot_id']
        section = get_section_prefix(plot_id)

        if section not in section_stats:
            section_stats[section] = {
                'total': 0,
                'with_images': 0,
                'image_count': 0
            }

        section_stats[section]['total'] += 1

        images_str = plot.get('monument_images', '')
        image_list = parse_images(images_str)

        if image_list:
            section_stats[section]['with_images'] += 1
            section_stats[section]['image_count'] += len(image_list)

    for section in sorted(section_stats.keys()):
        stats = section_stats[section]
        folder = FOLDER_MAP.get(section, 'Unknown')

        print(f"{section} ({folder}):")
        print(f"  Total Plots: {stats['total']}")
        print(f"  Plots with Images: {stats['with_images']}")
        print(f"  Total Images: {stats['image_count']}")
        print()

    # Return statistics for potential scripting use
    return {
        'total_plots': total_plots,
        'plots_with_images': plots_with_images,
        'total_image_refs': total_image_refs,
        'valid_images': len(valid_images),
        'missing_images': len(missing_images),
        'success': len(missing_images) == 0
    }

if __name__ == '__main__':
    results = verify_images()

    # Exit with error code if there are missing images
    import sys
    sys.exit(0 if results['success'] else 1)
