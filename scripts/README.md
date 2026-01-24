# OICA Cemetery Database Management Scripts

This folder contains Python scripts for managing and maintaining the OICA Cemetery database.

## ⚠️ IMPORTANT: CSV Header Protection

**CRITICAL:** When sorting CSV files in editors, the header row (line 1) gets sorted with the data and moves to a random line, **breaking the website**.

**After any manual CSV editing, ALWAYS run:**
```bash
python3 scripts/fix_csv_headers.py
```

See [CSV_EDITING_GUIDE.md](CSV_EDITING_GUIDE.md) for detailed instructions on safe CSV editing.

## Data Management Scripts

### fix_lot_status.py
**Purpose:** Corrects lot status based on purchased_rights and occupancy
- Distinguishes between Available (unpurchased) and Unoccupied (purchased but empty)
- Updates lots.csv with correct status values
- Regenerates available_lots.csv with only unpurchased lots
- Handles special exceptions (e.g., physical obstructions)

**Usage:**
```bash
# Dry run (preview changes)
python3 fix_lot_status.py

# Apply changes
python3 fix_lot_status.py --apply
```

### validate_data.py
**Purpose:** Validates consistency across all cemetery CSV files
- Checks available_lots.csv vs lots.csv consistency
- Verifies lot status matches actual occupants
- Identifies orphaned occupants
- Reports lots with multiple occupants

**Usage:**
```bash
python3 validate_data.py
```

### fix_csv_headers.py ⚠️ IMPORTANT
**Purpose:** Fixes CSV headers that got displaced during sorting
- Finds header rows that moved from line 1
- Moves headers back to line 1
- Verifies all CSV files have correct structure
- **Run this after any manual CSV editing/sorting**

**Usage:**
```bash
python3 fix_csv_headers.py
```

**When to use:**
- After sorting any CSV file in an editor
- When website stops loading data
- After manual edits to occupants.csv, lots.csv, or plots.csv
- As a safety check before deploying changes

### add_veteran_column.py
**Purpose:** Adds veteran column to occupants.csv and populates it from veterans.csv
- Matches occupant names with veteran records
- Adds 'veteran' column with 'Yes' for veterans, empty for non-veterans
- Uses fuzzy name matching to handle variations
- Updates cemetery viewer to display 🇺🇸 flag for veterans

**Usage:**
```bash
python3 add_veteran_column.py
```

**Note:** This script has already been run once. Re-running it will update the veteran column based on current veterans.csv data.

## Image Management Scripts

### verify_images.py
**Purpose:** Quick verification that all referenced monument images exist
- Reads monument_images field from plots.csv
- Checks if each image file exists in the correct section folder
- Reports missing images and statistics by section

**Usage:**
```bash
python3 verify_images.py
```

### image_inventory.py
**Purpose:** Creates comprehensive inventory of all monument images
- Lists all images referenced in plots.csv
- Identifies orphaned images (not referenced in database)
- Shows file sizes, modification dates
- Identifies images used by multiple plots
- Generates image_inventory_report.txt

**Usage:**
```bash
python3 image_inventory.py
```

### match_orphaned_images.py
**Purpose:** Finds and fixes orphaned monument images
- Extracts plot ID from filename using pattern matching
- Detects naming errors (extra dots, trailing spaces, etc.)
- Suggests which plot each orphaned image belongs to
- Can rename files and update plots.csv automatically

**Usage:**
```bash
# Dry run (preview changes)
python3 match_orphaned_images.py

# Apply changes (rename files and update plots.csv)
python3 match_orphaned_images.py --apply
```

## Report Generation Scripts

### missing_dates_report.py
**Purpose:** Generates report of occupants with missing birth or death dates
- Identifies records with incomplete date information
- Outputs both text and formatted reports
- Generates missing_dates_report.txt and missing_dates_report.pdf

**Usage:**
```bash
python3 missing_dates_report.py
```

### oldest_burials.py
**Purpose:** Generates report of oldest burial dates in the cemetery
- Sorts occupants by burial date (earliest first)
- Useful for historical research
- Generates oldest_burials_report.txt and oldest_burials_report_for_word.txt

**Usage:**
```bash
python3 oldest_burials.py
```

### oldest_at_death.py
**Purpose:** Generates report of occupants who lived the longest
- Calculates age at death from birth/death dates
- Sorts by age (oldest first)
- Generates oldest_at_death_report.txt and oldest_at_death_report_for_word.txt

**Usage:**
```bash
python3 oldest_at_death.py
```

## Data Files

All scripts operate on CSV files in the `../data/` directory:
- **lots.csv** - Individual lot information (status, purchased_rights, notes)
- **plots.csv** - Plot-level information (monument images, original purchaser)
- **occupants.csv** - Burial records (names, dates, status)
- **available_lots.csv** - Lists only unpurchased lots available for sale
- **veterans.csv** - Veteran burial records

## Important Notes

### Lot Status Categories
- **Available**: purchased_rights = 0 (unpurchased, for sale)
- **Unoccupied**: purchased_rights > 0, no occupants (purchased but empty)
- **Partially Occupied**: Has occupants, remaining_rights > 0
- **Fully Occupied**: remaining_rights = 0
- **Not Available**: Special cases (physical obstructions, buffer spaces)

### Special Cases
Some lots require manual exceptions:
- **OYK1-L1**: Partially occupied by vault (physical obstruction)
- **UTB25-L1**: Buffer space, not a full width lot

### Notes Field Convention
- Standard available lots should have note: "Unpurchased"
- Any lot with non-standard notes should be reviewed before automated changes

## Maintenance

When making changes to the database:
1. Run `validate_data.py` before changes to establish baseline
2. Make your changes
3. Run `validate_data.py` again to verify consistency
4. Check that available_lots.csv matches lots.csv status
