#!/usr/bin/env python3
"""
Add veteran column to occupants.csv and populate it based on veterans.csv data.
"""

import csv
import re

def normalize_name(name):
    """Normalize a name for comparison by removing extra spaces and punctuation."""
    name = name.strip().lower()
    name = re.sub(r'[.,\-]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name

def parse_veteran_name(vet_row):
    """Parse veteran name from veterans.csv row."""
    first = vet_row.get('First Name', '').strip()
    middle = vet_row.get('Middle Name/Initial', '').strip()
    last = vet_row.get('Last Name', '').strip()
    suffix = vet_row.get('Suffix', '').strip()

    # Build full name variants with suffix
    if suffix:
        full_name_with_suffix = f"{first} {middle} {last} {suffix}".strip()
        full_name_with_suffix = re.sub(r'\s+', ' ', full_name_with_suffix)
        name_no_middle_with_suffix = f"{first} {last} {suffix}".strip()
    else:
        full_name_with_suffix = None
        name_no_middle_with_suffix = None

    # Build full name variants without suffix
    full_name = f"{first} {middle} {last}".strip()
    full_name = re.sub(r'\s+', ' ', full_name)
    name_no_middle = f"{first} {last}".strip()

    # Return all variants (with and without suffix)
    variants = [
        normalize_name(full_name),
        normalize_name(name_no_middle)
    ]

    if full_name_with_suffix:
        variants.append(normalize_name(full_name_with_suffix))
        variants.append(normalize_name(name_no_middle_with_suffix))

    return variants

def main():
    # Read veterans.csv
    print("Reading veterans.csv...")
    veterans = {}
    with open('data/veterans.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name_variants = parse_veteran_name(row)
            branch = row.get('Branch', '').strip()
            service = row.get('Service Period', '').strip()

            # Store all name variants
            for variant in name_variants:
                veterans[variant] = {'branch': branch, 'service': service}

    print(f"Loaded {len(veterans)} veteran name variants")

    # Read occupants.csv
    print("Reading occupants.csv...")
    with open('data/occupants.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        occupants = list(reader)

    # Check if veteran column already exists
    if 'veteran' not in fieldnames:
        fieldnames = list(fieldnames)
        # Add veteran column after status
        status_index = fieldnames.index('status')
        fieldnames.insert(status_index + 1, 'veteran')
        print("Added 'veteran' column to fieldnames")

    # Match occupants with veterans
    matches = 0
    for occ in occupants:
        name = occ.get('name', '').strip()
        normalized_name = normalize_name(name)

        if normalized_name in veterans:
            occ['veteran'] = 'Yes'
            matches += 1
        else:
            occ['veteran'] = ''

    print(f"\nMatched {matches} occupants as veterans")

    # Write updated occupants.csv
    print("\nWriting updated occupants.csv...")
    with open('data/occupants.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(occupants)

    print("✓ Successfully updated occupants.csv with veteran column")

    # Show some examples
    print("\nExample veterans found:")
    count = 0
    for occ in occupants:
        if occ.get('veteran') == 'Yes':
            print(f"  {occ['name']} - {occ['lot_id']}")
            count += 1
            if count >= 5:
                break

if __name__ == '__main__':
    main()
