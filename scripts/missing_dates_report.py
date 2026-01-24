#!/usr/bin/env python3
"""
Missing Dates Report
Identifies occupants missing DOB, DOD, or both from occupants.csv

Usage: python3 missing_dates_report.py
"""

import csv
import os

def check_missing_dates(csv_path='data/occupants.csv'):
    """
    Check occupants.csv for missing birth_date and/or death_date.
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

    # Track different categories of missing data
    missing_both = []
    missing_dob = []
    missing_dod = []

    for occ in occupants:
        lot_id = occ['lot_id']
        name = occ['name']
        status = occ.get('status', '').strip()
        birth_date = occ.get('birth_date', '').strip()
        death_date = occ.get('death_date', '').strip()

        # Skip entries with status "Reserved"
        if status == 'Reserved':
            continue

        if not birth_date and not death_date:
            missing_both.append({'lot_id': lot_id, 'name': name})
        elif not birth_date:
            missing_dob.append({'lot_id': lot_id, 'name': name, 'death_date': death_date})
        elif not death_date:
            missing_dod.append({'lot_id': lot_id, 'name': name, 'birth_date': birth_date})

    # Print report
    print("=" * 80)
    print("MISSING DATES REPORT - OICA Cemetery Occupants")
    print("=" * 80)
    print(f"\nTotal occupants: {len(occupants)}")
    print(f"Missing both DOB and DOD: {len(missing_both)}")
    print(f"Missing DOB only: {len(missing_dob)}")
    print(f"Missing DOD only: {len(missing_dod)}")
    print(f"Total with missing date info: {len(missing_both) + len(missing_dob) + len(missing_dod)}")

    # Missing both dates
    if missing_both:
        print(f"\n{'=' * 80}")
        print(f"MISSING BOTH DOB AND DOD ({len(missing_both)} occupants)")
        print(f"{'=' * 80}")
        for occ in missing_both:
            print(f"  {occ['lot_id']:<15} {occ['name']}")

    # Missing DOB only
    if missing_dob:
        print(f"\n{'=' * 80}")
        print(f"MISSING DOB ONLY ({len(missing_dob)} occupants)")
        print(f"{'=' * 80}")
        for occ in missing_dob:
            print(f"  {occ['lot_id']:<15} {occ['name']:<40} DOD: {occ['death_date']}")

    # Missing DOD only
    if missing_dod:
        print(f"\n{'=' * 80}")
        print(f"MISSING DOD ONLY ({len(missing_dod)} occupants)")
        print(f"{'=' * 80}")
        for occ in missing_dod:
            print(f"  {occ['lot_id']:<15} {occ['name']:<40} DOB: {occ['birth_date']}")

    print(f"\n{'=' * 80}")

    # Write to file
    output_file = 'missing_dates_report.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("MISSING DATES REPORT - OICA Cemetery Occupants\n")
        f.write("=" * 80 + "\n")
        f.write(f"\nTotal occupants: {len(occupants)}\n")
        f.write(f"Missing both DOB and DOD: {len(missing_both)}\n")
        f.write(f"Missing DOB only: {len(missing_dob)}\n")
        f.write(f"Missing DOD only: {len(missing_dod)}\n")
        f.write(f"Total with missing date info: {len(missing_both) + len(missing_dob) + len(missing_dod)}\n")

        if missing_both:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"MISSING BOTH DOB AND DOD ({len(missing_both)} occupants)\n")
            f.write(f"{'=' * 80}\n")
            for occ in missing_both:
                f.write(f"  {occ['lot_id']:<15} {occ['name']}\n")

        if missing_dob:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"MISSING DOB ONLY ({len(missing_dob)} occupants)\n")
            f.write(f"{'=' * 80}\n")
            for occ in missing_dob:
                f.write(f"  {occ['lot_id']:<15} {occ['name']:<40} DOD: {occ['death_date']}\n")

        if missing_dod:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"MISSING DOD ONLY ({len(missing_dod)} occupants)\n")
            f.write(f"{'=' * 80}\n")
            for occ in missing_dod:
                f.write(f"  {occ['lot_id']:<15} {occ['name']:<40} DOB: {occ['birth_date']}\n")

        f.write(f"\n{'=' * 80}\n")

    print(f"\nReport saved to: {output_file}")

if __name__ == '__main__':
    check_missing_dates()
