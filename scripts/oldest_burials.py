#!/usr/bin/env python3
"""
Find Oldest Burials
Identifies the 10 earliest burials (oldest death dates) in the cemetery

Usage: python3 oldest_burials.py
"""

import csv
import os
from datetime import datetime

def parse_date(date_str):
    """
    Parse various date formats from the CSV.
    Returns datetime object or None if unable to parse.
    """
    if not date_str or not date_str.strip():
        return None

    date_str = date_str.strip()

    # Common date formats to try
    formats = [
        '%m/%d/%Y',   # 01/15/1920
        '%m/%d/%y',   # 01/15/20
        '%Y',         # 1920
        '%m/%Y',      # 01/1920
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None

def find_oldest_burials(csv_path='data/occupants.csv'):
    """
    Find the 10 earliest burials (oldest death dates).
    """
    if not os.path.exists(csv_path):
        print(f"Error: CSV file '{csv_path}' not found!")
        return

    # Read occupants CSV
    occupants = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            occupants.append(row)

    # Parse death dates
    burial_data = []

    for occ in occupants:
        lot_id = occ['lot_id']
        name = occ['name']
        birth_str = occ.get('birth_date', '').strip()
        death_str = occ.get('death_date', '').strip()

        if not death_str:
            continue

        death_date = parse_date(death_str)

        if death_date:
            burial_data.append({
                'lot_id': lot_id,
                'name': name,
                'birth_date': birth_str if birth_str else 'Unknown',
                'death_date': death_str,
                'death_datetime': death_date
            })

    # Sort by death date ascending (oldest first)
    burial_data.sort(key=lambda x: x['death_datetime'])

    # Print report
    print("=" * 90)
    print("OLDEST BURIALS (EARLIEST DEATH DATES) - OICA Cemetery")
    print("=" * 90)
    print(f"\nTotal occupants with death dates: {len(burial_data)}")
    print(f"\nTop 10 Oldest Burials:\n")

    print(f"{'Rank':<6} {'Lot ID':<15} {'Name':<35} {'Birth':<12} {'Death'}")
    print("-" * 90)

    for i, occ in enumerate(burial_data[:10], 1):
        print(f"{i:<6} {occ['lot_id']:<15} {occ['name']:<35} {occ['birth_date']:<12} {occ['death_date']}")

    print("\n" + "=" * 90)

    # Write to regular text file
    output_file = 'oldest_burials_report.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 90 + "\n")
        f.write("OLDEST BURIALS (EARLIEST DEATH DATES) - OICA Cemetery\n")
        f.write("=" * 90 + "\n")
        f.write(f"\nTotal occupants with death dates: {len(burial_data)}\n")
        f.write(f"\nTop 10 Oldest Burials:\n\n")

        f.write(f"{'Rank':<6} {'Lot ID':<15} {'Name':<35} {'Birth':<12} {'Death'}\n")
        f.write("-" * 90 + "\n")

        for i, occ in enumerate(burial_data[:10], 1):
            f.write(f"{i:<6} {occ['lot_id']:<15} {occ['name']:<35} {occ['birth_date']:<12} {occ['death_date']}\n")

        f.write("\n" + "=" * 90 + "\n")

    print(f"\nReport saved to: {output_file}")

    # Write tab-separated version for Word
    tsv_file = 'oldest_burials_report_for_word.txt'
    with open(tsv_file, 'w', encoding='utf-8') as f:
        f.write("OLDEST BURIALS (EARLIEST DEATH DATES) - OICA Cemetery\n\n")
        f.write(f"Total occupants with death dates: {len(burial_data)}\n\n")
        f.write("Top 10 Oldest Burials:\n\n")

        # Tab-separated header
        f.write("Rank\tLot ID\tName\tBirth\tDeath\n")

        # Tab-separated data
        for i, occ in enumerate(burial_data[:10], 1):
            f.write(f"{i}\t{occ['lot_id']}\t{occ['name']}\t{occ['birth_date']}\t{occ['death_date']}\n")

    print(f"Word-friendly version saved to: {tsv_file}")
    print("\nTo use in Word:")
    print("1. Open the *_for_word.txt file")
    print("2. Select and copy the table data (from 'Rank' onwards)")
    print("3. Paste into Word")
    print("4. Select the pasted text and go to: Insert > Table > Convert Text to Table")
    print("5. Choose 'Tabs' as separator and click OK")

if __name__ == '__main__':
    find_oldest_burials()
