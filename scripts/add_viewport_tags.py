#!/usr/bin/env python3
"""
Add viewport meta tags to all HTML files that don't have them.
"""

import os
import re
from pathlib import Path

def add_viewport_tag(file_path):
    """Add viewport meta tag to an HTML file if it doesn't have one."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if viewport tag already exists
    if 'name="viewport"' in content or 'name=\'viewport\'' in content:
        return False, "Already has viewport tag"

    # Find the charset meta tag and add viewport after it
    pattern = r'(<meta\s+http-equiv="content-type"\s+content="text/html;\s*charset=utf-8"\s*/>)'

    if re.search(pattern, content, re.IGNORECASE):
        replacement = r'\1\n\t\t<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        new_content = re.sub(pattern, replacement, content, count=1, flags=re.IGNORECASE)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, "Added viewport tag"
    else:
        return False, "Could not find insertion point"

def main():
    """Process all HTML files in the parent directory."""
    script_dir = Path(__file__).parent
    parent_dir = script_dir.parent

    # Find all HTML files (excluding includes directory)
    html_files = []
    for file in parent_dir.glob('*.html'):
        html_files.append(file)

    print(f"Found {len(html_files)} HTML files\n")

    added = 0
    skipped = 0
    errors = 0

    for html_file in sorted(html_files):
        success, message = add_viewport_tag(html_file)
        if success:
            print(f"✓ {html_file.name}: {message}")
            added += 1
        elif "Already has" in message:
            print(f"  {html_file.name}: {message}")
            skipped += 1
        else:
            print(f"✗ {html_file.name}: {message}")
            errors += 1

    print(f"\nSummary:")
    print(f"  Added: {added}")
    print(f"  Skipped (already had tag): {skipped}")
    print(f"  Errors: {errors}")

if __name__ == '__main__':
    main()
