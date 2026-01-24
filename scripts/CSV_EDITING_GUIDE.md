# Guide to Safely Editing CSV Files

## The Header Problem

When you sort a CSV file in most editors (including VS Code), **the header row gets sorted along with the data**. This causes the header to move to a random line (alphabetically sorted), breaking the website's ability to load data.

### Example of the Problem:
```
Before Sort (correct):
Line 1: "lot_id","name","status","veteran",...
Line 2: "CYA1-L1","Watson H. Thurston","Occupant","Yes",...
Line 3: "CYA1-L2","Sue Thurston","Occupant","",...

After Sort (BROKEN):
Line 1: "CYA1-L1","Watson H. Thurston","Occupant","Yes",...
Line 2: "CYA1-L2","Sue Thurston","Occupant","",...
Line 255: "lot_id","name","status","veteran",...  ← Header moved!
```

## Safe Editing Methods

### Method 1: Use Python Scripts (Recommended)
Always use `csv.DictReader` and `csv.DictWriter` which automatically handle headers:

```python
import csv

# Read
with open('data/occupants.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)  # Automatically uses first row as header
    fieldnames = reader.fieldnames
    occupants = list(reader)

# Modify data here
# ...

# Write (header is automatically written first)
with open('data/occupants.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()  # Writes header first
    writer.writerows(occupants)
```

### Method 2: Manual Editing with Protection
If you must manually edit and sort:

1. **Before sorting:**
   - Copy the header row (line 1)
   - Delete the header row from the file

2. **Sort the data**

3. **After sorting:**
   - Paste the header back as line 1
   - Save the file

4. **Run the fix script:**
   ```bash
   python3 scripts/fix_csv_headers.py
   ```

### Method 3: Use Excel/Google Sheets (with caution)
- Excel and Google Sheets can "freeze" the header row so it doesn't sort
- **CAUTION:** These programs may change the CSV format (quotes, line endings)
- Always run the fix script after using spreadsheet software

## Quick Fix After Sorting

If you accidentally sorted and the header moved, run:

```bash
cd "/Users/robertsylvester/Desktop/OICA Sandbox/OICA New Website"
python3 scripts/fix_csv_headers.py
```

This script will:
- Find the header row wherever it is
- Move it back to line 1
- Keep all data rows intact

## How to Tell if Headers are Broken

**Symptoms:**
- Cemetery viewer shows no data
- Cemetery records page is blank
- Browser console shows parsing errors

**Quick Check:**
```bash
head -1 data/occupants.csv
```

Should show:
```
"lot_id","name","status","veteran","former_name","birth_date","death_date","notes"
```

If it shows data instead (like `"CYA1-L1","Watson H. Thurston",...`), the header is missing/moved.

## Best Practices

### ✓ DO:
- Use Python scripts with `csv.DictReader/DictWriter`
- Run `fix_csv_headers.py` after any manual editing
- Test the website after CSV changes
- Keep backups before major edits

### ✗ DON'T:
- Sort CSV files without removing the header first
- Use text editors that don't understand CSV format
- Forget to verify the header position after editing
- Directly edit CSVs in production without testing

## Available Helper Scripts

All scripts automatically preserve headers:

- `add_veteran_column.py` - Updates veteran status
- `fix_lot_status.py` - Updates lot availability
- `update_cremation_vault_status.py` - Updates burial types
- `validate_data.py` - Checks data consistency
- **`fix_csv_headers.py`** - Repairs header positions (run anytime)

## Emergency Recovery

If the website stops working after CSV edits:

1. **Check headers:**
   ```bash
   python3 scripts/fix_csv_headers.py
   ```

2. **Verify files:**
   ```bash
   head -1 data/occupants.csv
   head -1 data/lots.csv
   head -1 data/plots.csv
   ```

3. **Restore from backup if needed**

4. **Test the website**

---

**Remember:** The header row must ALWAYS be line 1 in all CSV files!
