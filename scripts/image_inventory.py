#!/usr/bin/env python3
"""
Image Inventory Report for OICA Cemetery
Creates a comprehensive inventory of all monument images
Shows which images are referenced in plots.csv and which are orphaned (not referenced)
"""

import csv
import os
from pathlib import Path
from datetime import datetime

# Configuration
BASE_DIR = Path(__file__).parent
PLOTS_CSV = BASE_DIR / 'data' / 'plots.csv'
IMAGES_DIR = BASE_DIR / 'Monument Images'
OUTPUT_FILE = BASE_DIR / 'image_inventory_report.txt'

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

def get_file_size(file_path):
    """Get human-readable file size"""
    size = file_path.stat().st_size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def create_inventory():
    """Create comprehensive image inventory"""

    print("Creating image inventory report...")

    # Read plots.csv to get referenced images
    referenced_images = {}  # {section: {filename: [plot_ids]}}

    with open(PLOTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for plot in reader:
            plot_id = plot['plot_id']
            images_str = plot.get('monument_images', '')
            image_list = parse_images(images_str)

            section = get_section_prefix(plot_id)
            if section not in referenced_images:
                referenced_images[section] = {}

            for img in image_list:
                if img not in referenced_images[section]:
                    referenced_images[section][img] = []
                referenced_images[section][img].append(plot_id)

    # Scan all image folders
    all_images = {}  # {section: {filename: file_info}}

    for section, folder_name in FOLDER_MAP.items():
        folder_path = IMAGES_DIR / folder_name

        if not folder_path.exists():
            print(f"Warning: Folder not found: {folder_name}")
            continue

        all_images[section] = {}

        # Get all image files
        for img_path in folder_path.iterdir():
            if img_path.is_file() and img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                all_images[section][img_path.name] = {
                    'path': img_path,
                    'size': get_file_size(img_path),
                    'modified': datetime.fromtimestamp(img_path.stat().st_mtime)
                }

    # Generate report
    report_lines = []

    report_lines.append("=" * 100)
    report_lines.append("OICA CEMETERY - IMAGE INVENTORY REPORT")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 100)
    report_lines.append("")

    # Summary statistics
    total_referenced = sum(len(imgs) for imgs in referenced_images.values())
    total_physical = sum(len(imgs) for imgs in all_images.values())
    total_orphaned = 0

    report_lines.append("SUMMARY STATISTICS")
    report_lines.append("-" * 100)
    report_lines.append(f"Total Image Files in Folders: {total_physical}")
    report_lines.append(f"Total Images Referenced in plots.csv: {total_referenced}")
    report_lines.append("")

    # Section-by-section inventory
    for section in sorted(FOLDER_MAP.keys()):
        folder_name = FOLDER_MAP[section]

        report_lines.append("=" * 100)
        report_lines.append(f"SECTION: {section} ({folder_name})")
        report_lines.append("=" * 100)
        report_lines.append("")

        if section not in all_images:
            report_lines.append(f"ERROR: Folder not found: {folder_name}")
            report_lines.append("")
            continue

        section_images = all_images[section]
        section_refs = referenced_images.get(section, {})

        report_lines.append(f"Physical Files: {len(section_images)}")
        report_lines.append(f"Referenced Files: {len(section_refs)}")
        report_lines.append("")

        # Referenced images
        if section_refs:
            report_lines.append("REFERENCED IMAGES (in plots.csv)")
            report_lines.append("-" * 100)

            for img_name in sorted(section_refs.keys()):
                plot_list = section_refs[img_name]
                exists = img_name in section_images

                status = "✓ EXISTS" if exists else "✗ MISSING"
                size = section_images[img_name]['size'] if exists else "N/A"

                report_lines.append(f"  {img_name:<40} {status:<12} {size:<10} Plots: {', '.join(plot_list)}")

            report_lines.append("")

        # Orphaned images (not referenced in plots.csv)
        orphaned = set(section_images.keys()) - set(section_refs.keys())

        if orphaned:
            total_orphaned += len(orphaned)
            report_lines.append("ORPHANED IMAGES (not referenced in plots.csv)")
            report_lines.append("-" * 100)
            report_lines.append(f"Total: {len(orphaned)} files")
            report_lines.append("")

            for img_name in sorted(orphaned):
                img_info = section_images[img_name]
                report_lines.append(f"  {img_name:<40} {img_info['size']:<10} Modified: {img_info['modified'].strftime('%Y-%m-%d')}")

            report_lines.append("")

        # Images with multiple plot references
        multi_refs = {img: plots for img, plots in section_refs.items() if len(plots) > 1}

        if multi_refs:
            report_lines.append("IMAGES USED BY MULTIPLE PLOTS")
            report_lines.append("-" * 100)

            for img_name in sorted(multi_refs.keys()):
                plot_list = multi_refs[img_name]
                report_lines.append(f"  {img_name:<40} Used by {len(plot_list)} plots: {', '.join(plot_list)}")

            report_lines.append("")

    # Final summary
    report_lines.append("=" * 100)
    report_lines.append("INVENTORY SUMMARY")
    report_lines.append("=" * 100)
    report_lines.append(f"Total Physical Image Files: {total_physical}")
    report_lines.append(f"Total Referenced Images: {total_referenced}")
    report_lines.append(f"Total Orphaned Images (not referenced): {total_orphaned}")
    report_lines.append("")

    if total_orphaned > 0:
        report_lines.append("NOTE: Orphaned images may be:")
        report_lines.append("  - Old versions that should be deleted")
        report_lines.append("  - Images for plots not yet entered in database")
        report_lines.append("  - Images with naming errors")
        report_lines.append("  - Backup copies")
        report_lines.append("")

    # Write to file
    report_text = '\n'.join(report_lines)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report_text)

    # Also print to console
    print(report_text)

    print(f"\nReport saved to: {OUTPUT_FILE}")

    return {
        'total_physical': total_physical,
        'total_referenced': total_referenced,
        'total_orphaned': total_orphaned
    }

if __name__ == '__main__':
    results = create_inventory()
