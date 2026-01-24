#!/usr/bin/env python3
"""
Fix veterans.csv by adding a Suffix column and moving suffixes from Middle Name/Initial.
"""

import csv
import re

def parse_middle_and_suffix(middle_field):
    """
    Parse the middle name/initial field to separate actual middle name from suffix.
    Returns (middle_name, suffix)
    """
    if not middle_field or middle_field.strip() == '':
        return ('', '')

    middle = middle_field.strip()

    # Common suffixes to look for
    suffix_patterns = [
        r'\s+(Jr\.?|Sr\.?|II|III|IV|M\.?D\.?|Ph\.?D\.?|Capt\.?|Dr\.?)$',
        r'^(Jr\.?|Sr\.?|II|III|IV)$',  # Entire field is just a suffix
    ]

    for pattern in suffix_patterns:
        match = re.search(pattern, middle, re.IGNORECASE)
        if match:
            suffix = match.group(1)
            # Remove suffix from middle name
            middle_clean = re.sub(pattern, '', middle, flags=re.IGNORECASE).strip()
            return (middle_clean, suffix)

    # Check if the field contains multiple parts where last part might be suffix
    parts = middle.split()
    if len(parts) >= 2:
        last_part = parts[-1]
        # Check if last part looks like a suffix
        if re.match(r'^(Jr\.?|Sr\.?|II|III|IV|M\.?D\.?|Ph\.?D\.?|Capt\.?|Dr\.?)$', last_part, re.IGNORECASE):
            suffix = last_part
            middle_clean = ' '.join(parts[:-1])
            return (middle_clean, suffix)

    # No suffix found
    return (middle, '')

def main():
    print("Reading veterans.csv...")

    # Read current veterans.csv
    with open('data/veterans.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        veterans = list(reader)

    print(f"Loaded {len(veterans)} veteran records")
    print()

    # Add Suffix column after Middle Name/Initial
    old_fieldnames = list(fieldnames)
    middle_index = old_fieldnames.index('Middle Name/Initial')
    new_fieldnames = old_fieldnames[:middle_index+1] + ['Suffix'] + old_fieldnames[middle_index+1:]

    print("Parsing middle names and suffixes...")
    changes = []

    for vet in veterans:
        middle_field = vet.get('Middle Name/Initial', '')
        middle_clean, suffix = parse_middle_and_suffix(middle_field)

        # Store parsed values
        vet['Middle Name/Initial'] = middle_clean
        vet['Suffix'] = suffix

        # Track changes for reporting
        if suffix:
            name = f"{vet.get('First Name', '')} {middle_field} {vet.get('Last Name', '')}".strip()
            changes.append({
                'name': name,
                'original_middle': middle_field,
                'new_middle': middle_clean,
                'suffix': suffix
            })

    print(f"Found {len(changes)} records with suffixes to move:")
    print()
    for i, change in enumerate(changes, 1):
        print(f"{i:2d}. {change['name']:<45}")
        print(f"    Middle: '{change['original_middle']}' → '{change['new_middle']}'  Suffix: '{change['suffix']}'")

    print()

    # Write updated veterans.csv
    print("Writing updated veterans.csv...")
    with open('data/veterans.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(veterans)

    print(f"✓ Successfully updated veterans.csv with Suffix column")
    print(f"  Total records: {len(veterans)}")
    print(f"  Records with suffixes: {len(changes)}")
    print()
    print("New column structure:")
    for i, field in enumerate(new_fieldnames, 1):
        print(f"  {i}. {field}")

if __name__ == '__main__':
    main()
