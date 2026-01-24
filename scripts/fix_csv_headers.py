#!/usr/bin/env python3
"""
Fix CSV headers that got moved during sorting.
Run this anytime after manually editing/sorting CSV files.
"""

import csv
import sys

def fix_csv_header(filepath):
    """Find and move header to line 1 if it's been displaced."""

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not lines:
        print(f'✗ {filepath} is empty')
        return False

    # Detect header line (contains field names, not data)
    header_keywords = ['lot_id', 'plot_id', 'name', 'status']
    header_line = None
    header_index = -1
    data_lines = []

    for i, line in enumerate(lines):
        # Check if this line looks like a header
        if any(keyword in line.lower() for keyword in header_keywords):
            # Make sure it's actually a header, not data that happens to contain these words
            if line.count(',') >= 4 and line.strip().startswith('"'):
                # Count how many header keywords it has
                keyword_count = sum(1 for kw in header_keywords if kw in line.lower())
                if keyword_count >= 2:  # At least 2 keywords = likely header
                    header_line = line
                    header_index = i
                    continue

        # Not a header line, add to data
        if line.strip():
            data_lines.append(line)

    if header_line is None:
        print(f'✗ {filepath}: No header found!')
        return False

    if header_index == 0:
        print(f'✓ {filepath}: Header already at line 1')
        return True

    # Header is not at line 1 - fix it
    print(f'⚠  {filepath}: Header found at line {header_index + 1}, moving to line 1')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(header_line)
        f.writelines(data_lines)

    print(f'✓ {filepath}: Fixed! Header at line 1, {len(data_lines)} data rows')
    return True

def main():
    files_to_check = [
        'data/occupants.csv',
        'data/lots.csv',
        'data/plots.csv'
    ]

    print('='*80)
    print('CSV HEADER POSITION CHECK')
    print('='*80)
    print()

    all_good = True
    for filepath in files_to_check:
        try:
            result = fix_csv_header(filepath)
            if not result:
                all_good = False
        except FileNotFoundError:
            print(f'✗ {filepath}: File not found')
            all_good = False
        except Exception as e:
            print(f'✗ {filepath}: Error - {e}')
            all_good = False
        print()

    print('='*80)
    if all_good:
        print('✓ All CSV files have headers at line 1')
    else:
        print('⚠  Some files had issues - check output above')
    print('='*80)

if __name__ == '__main__':
    main()
