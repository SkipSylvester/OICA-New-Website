#!/usr/bin/env python3
"""
Data Validation Script for OICA Cemetery
Checks for discrepancies between available_lots.csv, occupants.csv, and lots.csv
"""

import csv
from pathlib import Path
from collections import defaultdict

# Configuration
BASE_DIR = Path(__file__).parent
AVAILABLE_LOTS_CSV = BASE_DIR / 'data' / 'available_lots.csv'
OCCUPANTS_CSV = BASE_DIR / 'data' / 'occupants.csv'
LOTS_CSV = BASE_DIR / 'data' / 'lots.csv'

def parse_available_lots(lots_str):
    """Parse the lots_available field (e.g., '1,5' -> [1, 5])"""
    if not lots_str or lots_str.strip() == '':
        return []
    return [int(lot.strip()) for lot in lots_str.split(',')]

def validate_data():
    """Check for discrepancies between the CSV files"""

    print("=" * 100)
    print("OICA Cemetery - Data Validation Report")
    print("=" * 100)
    print()

    # Read available_lots.csv
    available_lots_data = {}  # {plot_id: [lot_numbers]}
    with open(AVAILABLE_LOTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            plot_id = row['plot_id']
            lots = parse_available_lots(row['lots_available'])
            available_lots_data[plot_id] = lots

    print(f"Available Lots CSV: {len(available_lots_data)} plots with available lots")
    print()

    # Read lots.csv
    lots_data = {}  # {lot_id: lot_info}
    lots_by_plot = defaultdict(list)  # {plot_id: [lot_info]}
    with open(LOTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lot_id = row['lot_id']
            plot_id = row['plot_id']
            lots_data[lot_id] = row
            lots_by_plot[plot_id].append(row)

    print(f"Lots CSV: {len(lots_data)} total lots across {len(lots_by_plot)} plots")
    print()

    # Read occupants.csv
    occupants_data = defaultdict(list)  # {lot_id: [occupant_info]}
    with open(OCCUPANTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lot_id = row['lot_id']
            occupants_data[lot_id].append(row)

    print(f"Occupants CSV: {len(occupants_data)} lots with occupants")
    total_occupants = sum(len(occs) for occs in occupants_data.values())
    print(f"Total occupants: {total_occupants}")
    print()

    # Validation checks
    discrepancies = []

    print("=" * 100)
    print("VALIDATION CHECKS")
    print("=" * 100)
    print()

    # Check 1: Available lots vs lots.csv status
    print("CHECK 1: Available lots CSV vs Lots CSV status consistency")
    print("-" * 100)

    mismatches = []
    for plot_id, available_lot_nums in available_lots_data.items():
        if plot_id not in lots_by_plot:
            mismatches.append({
                'plot_id': plot_id,
                'issue': f"Plot {plot_id} in available_lots.csv but not found in lots.csv"
            })
            continue

        plot_lots = lots_by_plot[plot_id]

        for lot_info in plot_lots:
            lot_number = int(lot_info['lot_number'])
            status = lot_info['status']
            lot_id = lot_info['lot_id']

            # If lot is marked available in lots.csv
            if status == 'Available':
                # It should be in available_lots.csv
                if lot_number not in available_lot_nums:
                    mismatches.append({
                        'plot_id': plot_id,
                        'lot_id': lot_id,
                        'lot_number': lot_number,
                        'issue': f"Lot {lot_number} is 'Available' in lots.csv but NOT listed in available_lots.csv"
                    })

            # If lot is NOT available (Occupied, Partially Occupied, Reserved)
            else:
                # It should NOT be in available_lots.csv
                if lot_number in available_lot_nums:
                    mismatches.append({
                        'plot_id': plot_id,
                        'lot_id': lot_id,
                        'lot_number': lot_number,
                        'status': status,
                        'issue': f"Lot {lot_number} is '{status}' in lots.csv but IS listed as available in available_lots.csv"
                    })

    if mismatches:
        print(f"Found {len(mismatches)} mismatches:\n")
        for match in mismatches:
            print(f"  {match['plot_id']} (Lot {match.get('lot_number', '?')}): {match['issue']}")
        print()
    else:
        print("✓ No mismatches found - available_lots.csv is consistent with lots.csv")
        print()

    # Check 2: Lots status vs actual occupants
    print("CHECK 2: Lots CSV status vs actual occupants in occupants.csv")
    print("-" * 100)

    status_mismatches = []
    for lot_id, lot_info in lots_data.items():
        status = lot_info['status']
        occupants = occupants_data.get(lot_id, [])
        num_occupants = len(occupants)

        # Count non-Reserved occupants
        actual_occupants = [occ for occ in occupants if occ['status'] != 'Reserved']
        num_actual = len(actual_occupants)

        # Reserved occupants
        reserved_occupants = [occ for occ in occupants if occ['status'] == 'Reserved']
        num_reserved = len(reserved_occupants)

        # Validation logic
        if status == 'Available':
            if num_actual > 0:
                status_mismatches.append({
                    'lot_id': lot_id,
                    'status': status,
                    'occupants': num_actual,
                    'issue': f"Marked 'Available' but has {num_actual} actual occupants"
                })
        elif status == 'Occupied' or status == 'Fully Occupied':
            if num_actual == 0:
                status_mismatches.append({
                    'lot_id': lot_id,
                    'status': status,
                    'occupants': num_actual,
                    'issue': f"Marked '{status}' but has NO actual occupants"
                })
        elif status == 'Partially Occupied':
            if num_actual == 0:
                status_mismatches.append({
                    'lot_id': lot_id,
                    'status': status,
                    'occupants': num_actual,
                    'issue': f"Marked 'Partially Occupied' but has NO actual occupants"
                })

    if status_mismatches:
        print(f"Found {len(status_mismatches)} status mismatches:\n")
        for match in status_mismatches:
            print(f"  {match['lot_id']}: {match['issue']}")
        print()
    else:
        print("✓ No status mismatches - lots.csv status matches occupants.csv")
        print()

    # Check 3: Orphaned occupants (lot_id not in lots.csv)
    print("CHECK 3: Orphaned occupants (lot_id not found in lots.csv)")
    print("-" * 100)

    orphaned = []
    for lot_id, occupants in occupants_data.items():
        if lot_id not in lots_data:
            for occ in occupants:
                orphaned.append({
                    'lot_id': lot_id,
                    'name': occ['name'],
                    'status': occ['status']
                })

    if orphaned:
        print(f"Found {len(orphaned)} orphaned occupants:\n")
        for occ in orphaned:
            print(f"  {occ['lot_id']}: {occ['name']} ({occ['status']})")
        print()
    else:
        print("✓ No orphaned occupants - all lot_ids in occupants.csv exist in lots.csv")
        print()

    # Check 4: Lots with multiple occupants in same lot_id
    print("CHECK 4: Lots with multiple occupants (shared lots)")
    print("-" * 100)

    shared_lots = []
    for lot_id, occupants in occupants_data.items():
        if len(occupants) > 1:
            names = [occ['name'] for occ in occupants]
            shared_lots.append({
                'lot_id': lot_id,
                'count': len(occupants),
                'names': names
            })

    if shared_lots:
        print(f"Found {len(shared_lots)} lots with multiple occupants:\n")
        for lot in shared_lots[:20]:  # Show first 20
            print(f"  {lot['lot_id']}: {lot['count']} occupants - {', '.join(lot['names'])}")
        if len(shared_lots) > 20:
            print(f"  ... and {len(shared_lots) - 20} more")
        print()
    else:
        print("No lots with multiple occupants")
        print()

    # Summary
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"Available lots mismatches: {len(mismatches)}")
    print(f"Status mismatches: {len(status_mismatches)}")
    print(f"Orphaned occupants: {len(orphaned)}")
    print(f"Shared lots: {len(shared_lots)}")
    print()

    if len(mismatches) == 0 and len(status_mismatches) == 0 and len(orphaned) == 0:
        print("✓ All validation checks passed!")
    else:
        print("⚠ Issues found - review discrepancies above")

    return {
        'available_lots_mismatches': mismatches,
        'status_mismatches': status_mismatches,
        'orphaned_occupants': orphaned,
        'shared_lots': shared_lots
    }

if __name__ == '__main__':
    results = validate_data()
