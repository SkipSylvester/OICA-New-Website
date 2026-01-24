#!/usr/bin/env python3
"""
Update occupants.csv status from 'Occupant' to 'Cremation' or 'Vault' based on live website data.
"""

import csv

# Names with Cremation status (from live website)
CREMATIONS = [
    "Bruce Linscott Allen", "Dorothy Atwood", "Marion P. Atwood", "Theodore P. Atwood",
    "Herbert A. Bailey", "Patricia A. Bailey", "Loretta M. Baker", "Armand L. Bernier",
    "Robert S. Black", "Jonathan (Jot) Bond", "Thomas H. Conway", "Eunice A. Curran",
    "Nancy A. Curran", "Phillip E. Curran", "Leo M. R. David", "Benjamin S. Edwards",
    "Harold (Bud) Edwards", "Abbot Fletcher", "Corinne E. Fletcher", "Eileen Fletcher",
    "Alice B. Forgit", "Raymond W. Forgit", "Norman L. Gay", "A. Milton George",
    "Judith M. Gerber", "Charles W. Gilliam Jr.", "Dewey L. Gilliam", "Iva G. Gilliam",
    "Sonia J. Gilliam", "Cynthia Paul Howard", "Richard A. Howard", "Ethel L. Ivey",
    "Arlene L. Johnson", "Arthur H. Johnson", "Frances L. Johnson", "Hugh E. Johnson",
    "Pemberton Everett Johnson", "Craig T. Lachapell", "Jeffery W. Lachapell",
    "Jerry Leeman", "Faith S. Linscott", "Leo G. Mercier", "Elaine I. Mercier",
    "Constance L. Sylvester Merrill", "Juliette Oddo", "David John Olson", "Ralph T. Perry",
    "Charles L. Raymond", "Lawrence E. Roche", "Jeanette Winchell Short",
    "Rosemary Carpenter Shove Shiras", "Linda Jean Smeal", "Lawrence W. Spellman",
    "Sandra Stewart", "Gerald B. Stilphen", "Harvey A. Stilphen", "Madelyn F. Stilphen",
    "Madelyn R. Stilphen", "Margaret Gordon Sumner", "Philip Edward Sumner",
    "Charles Henry Swan Jr.", "William G. E. Sweetman III", "Augustus Sylvester",
    "Janet Louise Puffer Sylvester", "Alice M. Thibault", "Lucien A. Thibault",
    "Donna L. Warner", "Diane Wheatley"
]

# Names with Vault status (from live website)
VAULTS = [
    "John Jack Anderson", "Elizabeth Johnson Bragdon", "Peter Jon Fides",
    "Debra Lyn Fuller", "Robert H. Fuller", "Barbara Gregoire Holman",
    "William R. Hudson", "Caroline L. Johnson", "Hugh E. Johnson",
    "Jeanette Pearl Johnson", "Libby Judkins", "Mary L. Libby", "Myron K Krueger",
    "Durward W. Lewis", "George E. Morgan", "Maxine Linscott Nelson",
    "Gladys M. Placey", "Beverly Ann Stilphen", "Robert Weatherill Winchell",
    "Ruth Edna Wilson"
]

def normalize_name(name):
    """Normalize name for comparison - remove extra spaces, punctuation variations"""
    name = name.strip()
    # Handle common variations
    name = name.replace(',', '')
    name = name.replace('.', '')
    name = name.replace('  ', ' ')
    return name.lower()

def main():
    print("Reading occupants.csv...")

    # Read occupants
    with open('data/occupants.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        occupants = list(reader)

    print(f"Loaded {len(occupants)} occupants")

    # Normalize reference names for matching
    cremation_names = {normalize_name(name): name for name in CREMATIONS}
    vault_names = {normalize_name(name): name for name in VAULTS}

    # Track changes
    cremation_changes = []
    vault_changes = []
    not_found = {'cremations': [], 'vaults': []}

    # Update status
    for occ in occupants:
        name = occ.get('name', '').strip()
        name_norm = normalize_name(name)
        current_status = occ.get('status', '')

        if name_norm in cremation_names:
            if current_status != 'Cremation':
                occ['status'] = 'Cremation'
                cremation_changes.append(f"{name} ({occ.get('lot_id')})")
        elif name_norm in vault_names:
            if current_status != 'Vault':
                occ['status'] = 'Vault'
                vault_changes.append(f"{name} ({occ.get('lot_id')})")

    # Check for names not found
    found_cremations = set()
    found_vaults = set()
    for occ in occupants:
        name_norm = normalize_name(occ.get('name', ''))
        if name_norm in cremation_names:
            found_cremations.add(name_norm)
        if name_norm in vault_names:
            found_vaults.add(name_norm)

    not_found['cremations'] = [cremation_names[n] for n in cremation_names if n not in found_cremations]
    not_found['vaults'] = [vault_names[n] for n in vault_names if n not in found_vaults]

    # Write updated data
    print("\nWriting updated occupants.csv...")
    with open('data/occupants.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(occupants)

    # Report results
    print('\n' + '='*80)
    print('CREMATION STATUS UPDATES')
    print('='*80)
    print(f'Total cremations to mark: {len(CREMATIONS)}')
    print(f'Successfully updated: {len(cremation_changes)}')
    if cremation_changes:
        print('\nUpdated to Cremation:')
        for change in cremation_changes[:10]:
            print(f'  ✓ {change}')
        if len(cremation_changes) > 10:
            print(f'  ... and {len(cremation_changes) - 10} more')

    if not_found['cremations']:
        print(f'\n⚠ Not found in occupants.csv ({len(not_found["cremations"])}):')
        for name in not_found['cremations'][:5]:
            print(f'  - {name}')
        if len(not_found['cremations']) > 5:
            print(f'  ... and {len(not_found["cremations"]) - 5} more')

    print('\n' + '='*80)
    print('VAULT STATUS UPDATES')
    print('='*80)
    print(f'Total vaults to mark: {len(VAULTS)}')
    print(f'Successfully updated: {len(vault_changes)}')
    if vault_changes:
        print('\nUpdated to Vault:')
        for change in vault_changes[:10]:
            print(f'  ✓ {change}')
        if len(vault_changes) > 10:
            print(f'  ... and {len(vault_changes) - 10} more')

    if not_found['vaults']:
        print(f'\n⚠ Not found in occupants.csv ({len(not_found["vaults"])}):')
        for name in not_found['vaults']:
            print(f'  - {name}')

    # Final status count
    print('\n' + '='*80)
    print('FINAL STATUS COUNT')
    print('='*80)
    status_counts = {}
    for occ in occupants:
        status = occ.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    for status in sorted(status_counts.keys()):
        print(f'{status:<20} {status_counts[status]:>4} records')

    print('='*80)
    print('✓ Update complete!')

if __name__ == '__main__':
    main()
