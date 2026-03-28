#!/usr/bin/env python3
"""
Add mobile navigation script to all HTML files.
"""

import os
import re
from pathlib import Path

def add_mobile_nav_script(file_path):
    """Add mobile navigation script tag to an HTML file if it doesn't have it."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if mobile-navigation.js is already included
    if 'mobile-navigation.js' in content:
        return False, "Already has mobile navigation script"

    # Find the load-navigation.js script tag and add mobile-navigation.js after it
    pattern = r'(<script src="js/load-navigation\.js"></script>)'

    if re.search(pattern, content):
        replacement = r'\1\n\t\t<script src="js/mobile-navigation.js"></script>'
        new_content = re.sub(pattern, replacement, content, count=1)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, "Added mobile navigation script"
    else:
        return False, "Could not find load-navigation.js"

def main():
    """Process all HTML files in the parent directory."""
    script_dir = Path(__file__).parent
    parent_dir = script_dir.parent

    # Find all HTML files
    html_files = list(parent_dir.glob('*.html'))

    print(f"Found {len(html_files)} HTML files\n")

    added = 0
    skipped = 0
    errors = 0

    for html_file in sorted(html_files):
        success, message = add_mobile_nav_script(html_file)
        if success:
            print(f"✓ {html_file.name}: {message}")
            added += 1
        elif "Already has" in message:
            print(f"  {html_file.name}: {message}")
            skipped += 1
        else:
            print(f"  {html_file.name}: {message}")
            errors += 1

    print(f"\nSummary:")
    print(f"  Added: {added}")
    print(f"  Skipped (already had script): {skipped}")
    print(f"  Not applicable (no navigation): {errors}")

if __name__ == '__main__':
    main()
