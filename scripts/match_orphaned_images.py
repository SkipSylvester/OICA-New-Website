#!/usr/bin/env python3
"""
Orphaned Image Matcher for OICA Cemetery
Finds orphaned images, suggests which plot they belong to, detects naming errors,
and can optionally fix filenames and update plots.csv
"""

import csv
import os
import re
import shutil
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

def extract_plot_from_filename(filename):
    """
    Extract plot ID from filename
    Examples:
      UTC4-1.JPG -> UTC4
      NYC4-1M.JPG -> NYC4
      NYG2-VP.JPG -> NYG2
    """
    # Remove extension
    name = filename.rsplit('.', 1)[0]

    # Pattern: 2-letter section + letter + number(s)
    match = re.match(r'^([A-Z]{2}[A-Z]\d+)', name.upper())
    if match:
        return match.group(1)

    return None

def detect_naming_errors(filename):
    """
    Detect common naming errors in filenames
    Returns (has_error, suggested_fix, error_description)
    """
    errors = []
    suggested = filename

    # Error 1: Extra dot before extension (UTC4.-1.JPG)
    if '.-' in filename:
        suggested = suggested.replace('.-', '-')
        errors.append("Extra dot before dash")

    # Error 2: Inconsistent extension case (.jpg vs .JPG)
    name, ext = filename.rsplit('.', 1)
    if ext.lower() == 'jpg' and ext != 'JPG' and ext != 'jpg':
        # If it's mixed case, standardize to JPG
        if any(c.isupper() for c in ext) and any(c.islower() for c in ext):
            suggested = name + '.JPG'
            errors.append("Mixed case extension")

    # Error 3: Missing dash after plot ID (NYC41M.JPG should be NYC4-1M.JPG)
    match = re.match(r'^([A-Z]{2}[A-Z]\d+)(\d)', name)
    if match and '-' not in name:
        suggested = f"{match.group(1)}-{match.group(2)}{name[len(match.group(1))+1:]}.{ext}"
        errors.append("Missing dash after plot ID")

    has_error = len(errors) > 0
    error_desc = "; ".join(errors) if errors else None

    return (has_error, suggested if has_error else None, error_desc)

def find_orphaned_images():
    """Find all orphaned images and suggest matches"""

    print("=" * 100)
    print("OICA Cemetery - Orphaned Image Matcher")
    print("=" * 100)
    print()

    # Read plots.csv
    plots_dict = {}
    referenced_images = set()

    with open(PLOTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for plot in reader:
            plot_id = plot['plot_id']
            plots_dict[plot_id] = plot

            images_str = plot.get('monument_images', '')
            image_list = parse_images(images_str)

            for img in image_list:
                referenced_images.add((get_section_prefix(plot_id), img))

    # Scan all image folders for orphaned images
    orphaned_matches = []

    for section, folder_name in FOLDER_MAP.items():
        folder_path = IMAGES_DIR / folder_name

        if not folder_path.exists():
            continue

        for img_path in folder_path.iterdir():
            if img_path.is_file() and img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                filename = img_path.name

                # Check if orphaned
                if (section, filename) not in referenced_images:
                    # Extract plot ID from filename
                    suggested_plot = extract_plot_from_filename(filename)

                    # Detect naming errors
                    has_error, fixed_name, error_desc = detect_naming_errors(filename)

                    # Check if plot exists
                    plot_exists = suggested_plot in plots_dict if suggested_plot else False

                    # Check if fixed name would match
                    fixed_plot = None
                    if has_error and fixed_name:
                        fixed_plot = extract_plot_from_filename(fixed_name)
                        fixed_plot_exists = fixed_plot in plots_dict if fixed_plot else False
                    else:
                        fixed_plot_exists = False

                    orphaned_matches.append({
                        'section': section,
                        'folder': folder_name,
                        'current_filename': filename,
                        'path': img_path,
                        'suggested_plot': suggested_plot,
                        'plot_exists': plot_exists,
                        'has_naming_error': has_error,
                        'fixed_filename': fixed_name,
                        'fixed_plot': fixed_plot if has_error else None,
                        'fixed_plot_exists': fixed_plot_exists if has_error else False,
                        'error_description': error_desc
                    })

    # Display results
    print(f"Found {len(orphaned_matches)} orphaned images")
    print()

    if not orphaned_matches:
        print("✓ No orphaned images found!")
        return []

    # Group by section
    by_section = {}
    for match in orphaned_matches:
        section = match['section']
        if section not in by_section:
            by_section[section] = []
        by_section[section].append(match)

    # Display by section
    for section in sorted(by_section.keys()):
        matches = by_section[section]
        folder_name = FOLDER_MAP[section]

        print("=" * 100)
        print(f"SECTION: {section} ({folder_name}) - {len(matches)} orphaned images")
        print("=" * 100)
        print()

        for i, match in enumerate(matches, 1):
            print(f"{i}. {match['current_filename']}")

            if match['has_naming_error']:
                print(f"   ⚠ NAMING ERROR: {match['error_description']}")
                print(f"   → Suggested fix: {match['fixed_filename']}")

                if match['fixed_plot']:
                    if match['fixed_plot_exists']:
                        print(f"   ✓ Fixed name matches plot: {match['fixed_plot']} (EXISTS in plots.csv)")
                    else:
                        print(f"   ✗ Fixed name suggests plot: {match['fixed_plot']} (NOT FOUND in plots.csv)")

            if match['suggested_plot']:
                if match['plot_exists']:
                    print(f"   ✓ Suggests plot: {match['suggested_plot']} (EXISTS in plots.csv)")

                    # Show current images for this plot
                    current_plot = plots_dict[match['suggested_plot']]
                    current_images = parse_images(current_plot.get('monument_images', ''))

                    if current_images:
                        print(f"   Current images for {match['suggested_plot']}: {'; '.join(current_images)}")
                    else:
                        print(f"   Plot {match['suggested_plot']} currently has NO images")
                else:
                    print(f"   ✗ Suggests plot: {match['suggested_plot']} (NOT FOUND in plots.csv)")
            else:
                print(f"   ? Cannot determine plot ID from filename")

            print()

    return orphaned_matches

def apply_fixes(orphaned_matches, dry_run=True):
    """
    Apply fixes to orphaned images:
    1. Rename files with naming errors
    2. Add images to plots.csv
    """

    if dry_run:
        print("=" * 100)
        print("DRY RUN - No changes will be made")
        print("=" * 100)
        print()
    else:
        print("=" * 100)
        print("APPLYING FIXES")
        print("=" * 100)
        print()

    # Prepare changes
    files_to_rename = []
    plots_to_update = {}

    for match in orphaned_matches:
        target_plot = None
        final_filename = match['current_filename']

        # Determine target plot and filename
        if match['has_naming_error'] and match['fixed_plot_exists']:
            # Fix naming error and use the corrected plot
            target_plot = match['fixed_plot']
            final_filename = match['fixed_filename']

            files_to_rename.append({
                'old_path': match['path'],
                'new_name': final_filename,
                'reason': f"Fix naming error: {match['error_description']}"
            })

        elif match['plot_exists']:
            # No naming error, but plot exists
            target_plot = match['suggested_plot']
            final_filename = match['current_filename']

        # Add to plot updates
        if target_plot:
            if target_plot not in plots_to_update:
                plots_to_update[target_plot] = []
            plots_to_update[target_plot].append(final_filename)

    # Display planned changes
    print(f"Files to rename: {len(files_to_rename)}")
    print(f"Plots to update: {len(plots_to_update)}")
    print()

    if files_to_rename:
        print("FILE RENAMES:")
        print("-" * 100)
        for rename in files_to_rename:
            old_name = rename['old_path'].name
            new_name = rename['new_name']
            print(f"  {old_name} → {new_name}")
            print(f"    Reason: {rename['reason']}")
        print()

    if plots_to_update:
        print("PLOT UPDATES:")
        print("-" * 100)
        for plot_id, images in plots_to_update.items():
            print(f"  {plot_id}:")
            for img in images:
                print(f"    + {img}")
        print()

    if dry_run:
        print("This was a DRY RUN. No changes were made.")
        print("Run with --apply to actually make these changes.")
        return False

    # Apply changes
    print("Applying changes...")
    print()

    # Step 1: Rename files
    if files_to_rename:
        print("Renaming files...")
        for rename in files_to_rename:
            old_path = rename['old_path']
            new_path = old_path.parent / rename['new_name']

            print(f"  Renaming: {old_path.name} → {new_path.name}")
            shutil.move(str(old_path), str(new_path))
        print()

    # Step 2: Update plots.csv
    if plots_to_update:
        print("Updating plots.csv...")

        # Read all plots
        with open(PLOTS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            plots = list(reader)

        # Update plots
        for plot in plots:
            plot_id = plot['plot_id']
            if plot_id in plots_to_update:
                current_images = parse_images(plot.get('monument_images', ''))
                new_images = plots_to_update[plot_id]

                # Combine and deduplicate
                all_images = current_images + new_images
                all_images = list(dict.fromkeys(all_images))  # Remove duplicates, preserve order

                plot['monument_images'] = '; '.join(all_images)
                print(f"  Updated {plot_id}: added {len(new_images)} images (total: {len(all_images)})")

        # Write back
        with open(PLOTS_CSV, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(plots)

        print()

    print("✓ All changes applied successfully!")
    return True

if __name__ == '__main__':
    import sys

    # Find orphaned images
    orphaned_matches = find_orphaned_images()

    if not orphaned_matches:
        sys.exit(0)

    # Check for --apply flag
    apply_changes = '--apply' in sys.argv

    print()
    print("=" * 100)

    # Apply fixes (dry run by default)
    success = apply_fixes(orphaned_matches, dry_run=not apply_changes)

    if not apply_changes and orphaned_matches:
        print()
        print("To apply these changes, run:")
        print("  python3 match_orphaned_images.py --apply")
