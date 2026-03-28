# Cemetery Map Hover Tooltip Styles Guide

The enhanced cemetery map now offers **4 different tooltip detail levels** that you can select from the legend dropdown.

## Tooltip Style Options

### 1. Basic - ID and Status
**Best for**: Quick scanning, minimal visual clutter

**Shows**:
- Plot ID (e.g., "CYA1")
- Section name (e.g., "Church Yard")
- Status with color coding

**Example**:
```
CYA1
Church Yard
Fully Occupied
```

---

### 2. Detailed - Counts and Purchaser (DEFAULT)
**Best for**: General use, balanced information

**Shows**:
- Plot ID and section
- Status with color
- Total lots in plot
- Number of occupants
- Number of available lots
- Original purchaser (if known)

**Example**:
```
CYA1
Church Yard
─────────────────
Status: Fully Occupied
Total lots: 4
Occupants: 4

Original Purchaser: Watson A. Thurston
```

---

### 3. Occupants - Show Names
**Best for**: Genealogy research, finding specific people

**Shows**:
- Plot ID and section
- List of all occupant names
- Veteran flag (🇺🇸) for veterans
- If no occupants, shows available lot count

**Example**:
```
CYA1 - Church Yard
─────────────────
Occupants (4):
• Watson H. Thurston 🇺🇸
• Sue Thurston
• Arthur G. Thurston
• Hazel Thurston
```

**Empty Plot Example**:
```
NYA5 - New Yard
─────────────────
No occupants - 4 available
```

---

### 4. Full - Everything
**Best for**: Complete information at a glance

**Shows**:
- Plot ID and section
- Status with color
- Original purchaser
- All occupant names with death dates
- Veteran flags
- Available lot count
- Monument image count
- "Click for full details" prompt

**Example**:
```
CYA1 - Church Yard
Fully Occupied
Purchaser: Watson A. Thurston
─────────────────
Occupants (4):
• Watson H. Thurston 🇺🇸 (1940)
• Sue Thurston (1940)
• Arthur G. Thurston (1972)
• Hazel Thurston (1982)

📷 4 monument images

Click for full details
```

**With Many Occupants**:
```
OYA1 - Old Yard
Fully Occupied
─────────────────
Occupants (8):
• John Smith (1895)
• Mary Smith (1902)
• William Jones 🇺🇸 (1918)
• Sarah Jones (1920)
• Robert Brown (1935)
...and 3 more

📷 2 monument images

Click for full details
```

---

## How to Change Tooltip Style

1. Open `cemetery-map.html` in your browser
2. Look for the legend box in the **top right corner** of the map
3. Find the dropdown labeled **"Hover Detail Level"**
4. Select your preferred style:
   - Basic
   - Detailed (default)
   - Occupants
   - Full

The tooltip style changes **immediately** - just hover over any plot to see the new format.

---

## Use Cases by Style

### For Website Visitors:
- **Basic**: Mobile users or those who want minimal information
- **Detailed**: Most users - good balance of info without overwhelming
- **Occupants**: People searching for specific family members
- **Full**: Researchers wanting maximum information before clicking

### For Cemetery Management:
- **Detailed**: Check availability status quickly
- **Occupants**: Verify who's buried where
- **Full**: Complete overview for lot sales and planning

### For Genealogists:
- **Occupants**: Fast name scanning across plots
- **Full**: See dates and veteran status immediately

---

## Color Coding

All tooltip styles use color coding for status:
- **Green** (#76c7c0) - Available lots
- **Yellow** (#ffeb3b) - Partially Occupied
- **Gray** (#9e9e9e) - Fully Occupied
- **Red** (#f44336) - Not Available

The tooltip border also shows the status color.

---

## Technical Notes

- Tooltips update in real-time when you change the style
- No page reload required
- Data is loaded once and formatted dynamically
- Veteran flags (🇺🇸) only show for confirmed veterans (122 in database)
- Death dates shown when available in occupants.csv
- Monument image counts from plots.csv

---

## Future Enhancements (Phase 2+)

Potential additions to tooltips:
- Thumbnail preview of monument images
- Birth dates alongside death dates
- Lot-level breakdown (L1, L2, L3, L4)
- GPS coordinates
- Link to Google Maps
- Family relationship indicators
- Burial type indicators (cremation, vault)

---

## Customization

To change the default tooltip style, edit `js/cemetery-map.js` line 28:
```javascript
let currentTooltipStyle = 'detailed'; // Change to: 'basic', 'occupants', or 'full'
```

To modify what information appears in each style, edit the `createTooltipContent()` function starting at line 180.
