#!/usr/bin/env python3
"""
Find Oldest Occupants at Death
Identifies the 10 occupants who lived the longest

Usage: python3 oldest_at_death.py
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

def calculate_age(birth_date, death_date):
    """
    Calculate age in years between two dates.
    """
    if not birth_date or not death_date:
        return None

    age_days = (death_date - birth_date).days
    age_years = age_days / 365.25  # Account for leap years

    return age_years

def find_oldest_at_death(csv_path='data/occupants.csv'):
    """
    Find the 10 occupants who were oldest at death.
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

    # Calculate ages
    ages_data = []

    for occ in occupants:
        lot_id = occ['lot_id']
        name = occ['name']
        birth_str = occ.get('birth_date', '').strip()
        death_str = occ.get('death_date', '').strip()

        if not birth_str or not death_str:
            continue

        birth_date = parse_date(birth_str)
        death_date = parse_date(death_str)

        if birth_date and death_date:
            age = calculate_age(birth_date, death_date)
            if age and age > 0 and age < 130:  # Sanity check
                ages_data.append({
                    'lot_id': lot_id,
                    'name': name,
                    'birth_date': birth_str,
                    'death_date': death_str,
                    'age': age
                })

    # Sort by age descending
    ages_data.sort(key=lambda x: x['age'], reverse=True)

    # Print report
    print("=" * 80)
    print("OLDEST OCCUPANTS AT DEATH - OICA Cemetery")
    print("=" * 80)
    print(f"\nTotal occupants with both dates: {len(ages_data)}")
    print(f"\nTop 10 Oldest at Death:\n")

    print(f"{'Rank':<6} {'Lot ID':<15} {'Name':<35} {'Age':<8} {'Birth - Death'}")
    print("-" * 80)

    for i, occ in enumerate(ages_data[:10], 1):
        age_str = f"{occ['age']:.1f}"
        dates_str = f"{occ['birth_date']} - {occ['death_date']}"
        print(f"{i:<6} {occ['lot_id']:<15} {occ['name']:<35} {age_str:<8} {dates_str}")

    print("\n" + "=" * 80)

    # Write to regular text file
    output_file = 'oldest_at_death_report.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("OLDEST OCCUPANTS AT DEATH - OICA Cemetery\n")
        f.write("=" * 80 + "\n")
        f.write(f"\nTotal occupants with both dates: {len(ages_data)}\n")
        f.write(f"\nTop 10 Oldest at Death:\n\n")

        f.write(f"{'Rank':<6} {'Lot ID':<15} {'Name':<35} {'Age':<8} {'Birth - Death'}\n")
        f.write("-" * 80 + "\n")

        for i, occ in enumerate(ages_data[:10], 1):
            age_str = f"{occ['age']:.1f}"
            dates_str = f"{occ['birth_date']} - {occ['death_date']}"
            f.write(f"{i:<6} {occ['lot_id']:<15} {occ['name']:<35} {age_str:<8} {dates_str}\n")

        f.write("\n" + "=" * 80 + "\n")

    print(f"\nReport saved to: {output_file}")

    # Write tab-separated version for Word
    tsv_file = 'oldest_at_death_report_for_word.txt'
    with open(tsv_file, 'w', encoding='utf-8') as f:
        f.write("OLDEST OCCUPANTS AT DEATH - OICA Cemetery\n\n")
        f.write(f"Total occupants with both dates: {len(ages_data)}\n\n")
        f.write("Top 10 Oldest at Death:\n\n")

        # Tab-separated header
        f.write("Rank\tLot ID\tName\tAge (years)\tBirth Date\tDeath Date\n")

        # Tab-separated data
        for i, occ in enumerate(ages_data[:10], 1):
            age_str = f"{occ['age']:.1f}"
            f.write(f"{i}\t{occ['lot_id']}\t{occ['name']}\t{age_str}\t{occ['birth_date']}\t{occ['death_date']}\n")

    print(f"Word-friendly version saved to: {tsv_file}")
    print("\nTo use in Word:")
    print("1. Open the *_for_word.txt file")
    print("2. Select and copy the table data (from 'Rank' onwards)")
    print("3. Paste into Word")
    print("4. Select the pasted text and go to: Insert > Table > Convert Text to Table")
    print("5. Choose 'Tabs' as separator and click OK")

if __name__ == '__main__':
    find_oldest_at_death()
