#!/usr/bin/env python3
"""
Fix Lot Status Script for OICA Cemetery
Corrects the status field in lots.csv based on purchased_rights and occupancy
Regenerates available_lots.csv with only unpurchased lots
"""

import csv
from pathlib import Path
from collections import defaultdict

# Configuration
BASE_DIR = Path(__file__).parent
LOTS_CSV = BASE_DIR / 'data' / 'lots.csv'
OCCUPANTS_CSV = BASE_DIR / 'data' / 'occupants.csv'
AVAILABLE_LOTS_CSV = BASE_DIR / 'data' / 'available_lots.csv'

def fix_lot_status(dry_run=True):
    """
    Fix lot status based on proper logic:
    - Available: purchased_rights = 0 (unpurchased, for sale)
    - Unoccupied: purchased_rights > 0, no occupants (purchased but empty)
    - Partially Occupied: purchased_rights > 0, has occupants, remaining_rights > 0
    - Fully Occupied: purchased_rights > 0, remaining_rights = 0
    """

    # Exceptions: Lots that should remain "Not Available" for special reasons
    KEEP_NOT_AVAILABLE = {
        'OYK1-L1',   # Partially occupied by vault, physical obstruction
        'UTB25-L1',  # Buffer space, not a full width lot
    }

    print("=" * 100)
    if dry_run:
        print("DRY RUN - Lot Status Fix Analysis")
    else:
        print("FIXING LOT STATUS")
    print("=" * 100)
    print()

    # Read occupants.csv
    occupants_by_lot = defaultdict(list)
    with open(OCCUPANTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lot_id = row['lot_id']
            # Only count actual occupants, not Reserved
            if row['status'] != 'Reserved':
                occupants_by_lot[lot_id].append(row)

    # Read lots.csv
    with open(LOTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        lots = list(reader)

    # Analyze and fix status
    changes = []
    status_counts = {
        'Available': 0,
        'Unoccupied': 0,
        'Partially Occupied': 0,
        'Fully Occupied': 0,
        'Occupied': 0,
        'Not Available': 0
    }

    for lot in lots:
        lot_id = lot['lot_id']
        purchased_rights = int(lot.get('purchased_rights', 0))
        remaining_rights = int(lot.get('remaining_rights', 0))
        current_status = lot['status']

        num_occupants = len(occupants_by_lot.get(lot_id, []))

        # Check if this lot should remain "Not Available"
        if lot_id in KEEP_NOT_AVAILABLE:
            new_status = 'Not Available'
        # Determine correct status
        elif purchased_rights == 0:
            # Unpurchased - truly available for sale
            new_status = 'Available'
        elif num_occupants == 0:
            # Purchased but no occupants yet
            new_status = 'Unoccupied'
        elif remaining_rights > 0:
            # Has occupants but space remains
            new_status = 'Partially Occupied'
        else:
            # No remaining rights
            new_status = 'Fully Occupied'

        status_counts[new_status] += 1

        # Record change if status differs
        if current_status != new_status:
            changes.append({
                'lot_id': lot_id,
                'old_status': current_status,
                'new_status': new_status,
                'purchased_rights': purchased_rights,
                'remaining_rights': remaining_rights,
                'num_occupants': num_occupants
            })

            # Update the lot data
            lot['status'] = new_status

    # Display analysis
    print("STATUS DISTRIBUTION:")
    print("-" * 100)
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count} lots")
    print()

    print(f"CHANGES NEEDED: {len(changes)}")
    print("-" * 100)

    if changes:
        # Group by type of change
        by_change_type = defaultdict(list)
        for change in changes:
            key = f"{change['old_status']} → {change['new_status']}"
            by_change_type[key].append(change)

        for change_type, items in sorted(by_change_type.items()):
            print(f"\n{change_type}: {len(items)} lots")
            print()
            # Show first 5 examples
            for item in items[:5]:
                print(f"  {item['lot_id']}:")
                print(f"    Purchased: {item['purchased_rights']}, Remaining: {item['remaining_rights']}, Occupants: {item['num_occupants']}")
            if len(items) > 5:
                print(f"    ... and {len(items) - 5} more")
        print()
    else:
        print("✓ No changes needed - all statuses are correct!")
        print()

    if dry_run:
        print("=" * 100)
        print("This was a DRY RUN. No files were modified.")
        print("Run with --apply to make these changes.")
        print("=" * 100)
        return False

    # Apply changes - write lots.csv
    print("Writing updated lots.csv...")
    with open(LOTS_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(lots)
    print(f"✓ Updated {len(changes)} lot statuses in lots.csv")
    print()

    # Generate new available_lots.csv (only unpurchased lots)
    print("Generating new available_lots.csv (unpurchased lots only)...")

    available_by_plot = defaultdict(list)
    for lot in lots:
        if lot['status'] == 'Available':  # Only unpurchased
            plot_id = lot['plot_id']
            lot_number = int(lot['lot_number'])
            available_by_plot[plot_id].append(lot_number)

    # Sort and write
    with open(AVAILABLE_LOTS_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['plot_id', 'lots_available'])

        for plot_id in sorted(available_by_plot.keys()):
            lot_numbers = sorted(available_by_plot[plot_id])
            lots_str = ','.join(str(n) for n in lot_numbers)
            writer.writerow([plot_id, lots_str])

    print(f"✓ Generated available_lots.csv with {len(available_by_plot)} plots")
    print(f"  Total unpurchased lots: {sum(len(lots) for lots in available_by_plot.values())}")
    print()

    print("=" * 100)
    print("✓ ALL CHANGES APPLIED SUCCESSFULLY!")
    print("=" * 100)

    return True

if __name__ == '__main__':
    import sys

    # Check for --apply flag
    apply_changes = '--apply' in sys.argv

    success = fix_lot_status(dry_run=not apply_changes)

    if not apply_changes:
        print()
        print("To apply these changes, run:")
        print("  python3 fix_lot_status.py --apply")
