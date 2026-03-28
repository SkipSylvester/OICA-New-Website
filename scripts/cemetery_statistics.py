#!/usr/bin/env python3
"""
ORRS ISLAND CEMETERY ASSOCIATION - Statistics Generator
Generates comprehensive cemetery statistics from CSV data files.
"""

import csv
from datetime import datetime
from collections import defaultdict, Counter
import os
import sys

def read_csv(filename):
    """Read a CSV file and return list of dictionaries."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"Error: Could not find {filename}")
        sys.exit(1)

def count_image_plots(plots):
    """Count plots that have monument images."""
    plots_with_images = 0
    total_images = 0

    for plot in plots:
        images = plot.get('monument_images', '').strip()
        if images:
            plots_with_images += 1
            # Count semicolon-separated images
            total_images += len([img for img in images.split(';') if img.strip()])

    return plots_with_images, total_images

def calculate_section_stats(plots, lots, occupants):
    """Calculate statistics by section."""
    sections = defaultdict(lambda: {'plots': 0, 'lots': 0, 'occupants': 0})

    # Count plots by section
    for plot in plots:
        section = plot['section_name']
        sections[section]['plots'] += 1

    # Count lots by section (via plot_id)
    for lot in lots:
        plot_id = lot['plot_id']
        # Find the section for this plot
        for plot in plots:
            if plot['plot_id'] == plot_id:
                section = plot['section_name']
                sections[section]['lots'] += 1
                break

    # Count occupants by section (via lot_id -> plot_id)
    lot_to_plot = {lot['lot_id']: lot['plot_id'] for lot in lots}
    plot_to_section = {plot['plot_id']: plot['section_name'] for plot in plots}

    for occupant in occupants:
        lot_id = occupant['lot_id']
        if lot_id in lot_to_plot:
            plot_id = lot_to_plot[lot_id]
            if plot_id in plot_to_section:
                section = plot_to_section[plot_id]
                sections[section]['occupants'] += 1

    # Calculate occupancy rates
    for section in sections.values():
        if section['lots'] > 0:
            section['occupancy_rate'] = (section['occupants'] / section['lots']) * 100
        else:
            section['occupancy_rate'] = 0

    return dict(sections)

def calculate_lot_status(lots):
    """Calculate lot status statistics."""
    status_counts = Counter()

    for lot in lots:
        status = lot.get('status', 'Unknown')
        status_counts[status] += 1

    return status_counts

def count_occupied_lots(lots, occupants):
    """Count occupied vs empty lots."""
    occupied_lot_ids = {occ['lot_id'] for occ in occupants}
    occupied = len(occupied_lot_ids)
    total = len(lots)
    empty = total - occupied

    return occupied, empty

def calculate_record_completeness(occupants):
    """Calculate percentage of records with birth and death dates."""
    total = len(occupants)
    birth_dates = sum(1 for occ in occupants if occ.get('birth_date', '').strip())
    death_dates = sum(1 for occ in occupants if occ.get('death_date', '').strip())

    return birth_dates, death_dates

def calculate_ownership(plots):
    """Calculate plot ownership statistics."""
    total = len(plots)
    with_purchaser = sum(1 for plot in plots
                        if plot.get('purchaser', '').strip() and
                        plot['purchaser'].strip().lower() != 'unknown')
    with_current_owner = sum(1 for plot in plots
                            if plot.get('current_owner', '').strip() and
                            plot['current_owner'].strip().lower() != 'unknown')

    return with_purchaser, with_current_owner

def generate_text_report(plots, lots, occupants, veterans):
    """Generate a plain text version of the statistics report."""
    today = datetime.now().strftime("%B %d, %Y")

    # Basic counts
    total_plots = len(plots)
    total_lots = len(lots)
    total_occupants = len(occupants)
    avg_lots_per_plot = total_lots / total_plots if total_plots > 0 else 0

    # Section statistics
    section_stats = calculate_section_stats(plots, lots, occupants)

    # Occupant status
    status_counts = Counter(occ.get('status', 'Other') for occ in occupants)

    # Lot status
    lot_status = calculate_lot_status(lots)

    # Occupied vs empty
    occupied_lots, empty_lots = count_occupied_lots(lots, occupants)
    avg_occupancy = (sum(s['occupants'] for s in section_stats.values()) / total_lots * 100) if total_lots > 0 else 0

    # Veterans
    total_veterans = len(veterans)

    # Monument images
    plots_with_images, total_images = count_image_plots(plots)
    avg_images = total_images / plots_with_images if plots_with_images > 0 else 0

    # Record completeness
    birth_dates, death_dates = calculate_record_completeness(occupants)

    # Ownership
    with_purchaser, with_current_owner = calculate_ownership(plots)

    # Generate plain text report
    report = f"""================================================================================
ORRS ISLAND CEMETERY ASSOCIATION - COMPREHENSIVE STATISTICS
Updated: {today}
================================================================================

OVERALL CEMETERY
--------------------------------------------------------------------------------
Total Plots:                    {total_plots:>8}
Total Lots:                     {total_lots:>8}
Total Occupants/Records:        {total_occupants:>8}
Average Lots per Plot:          {avg_lots_per_plot:>8.2f}

================================================================================
BREAKDOWN BY SECTION
================================================================================
"""

    # Sort sections by name
    for section_name in sorted(section_stats.keys()):
        stats = section_stats[section_name]
        report += f"\n{section_name}\n"
        report += f"  Plots:           {stats['plots']:>6}\n"
        report += f"  Lots:            {stats['lots']:>6}\n"
        report += f"  Occupants:       {stats['occupants']:>6}\n"
        report += f"  Occupancy Rate:  {stats['occupancy_rate']:>5.1f}%\n"

    report += f"""
================================================================================
OCCUPANT STATUS
================================================================================
"""

    # Sort status by count (descending)
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_occupants * 100) if total_occupants > 0 else 0
        report += f"{status:.<30} {count:>6} ({pct:>5.1f}%)\n"

    report += f"""
================================================================================
LOT STATUS
================================================================================
"""
    for status, count in sorted(lot_status.items()):
        pct = (count / total_lots * 100) if total_lots > 0 else 0
        report += f"{status:.<30} {count:>6} lots ({pct:>5.1f}%)\n"

    report += f"""
================================================================================
LOT OCCUPANCY
================================================================================
Occupied Lots:                  {occupied_lots:>8} ({occupied_lots/total_lots*100:>5.1f}%)
Empty Lots:                     {empty_lots:>8} ({empty_lots/total_lots*100:>5.1f}%)
Average Occupancy Rate:         {avg_occupancy:>7.1f}%

================================================================================
MILITARY VETERANS
================================================================================
Total Veterans:                 {total_veterans:>8}

NOTE: Veteran count sourced from veterans.csv (authoritative list). This
includes all veterans regardless of burial status (occupants, reserved spaces,
memorials).

================================================================================
MONUMENT IMAGES
================================================================================
Plots with Images:              {plots_with_images:>8} ({plots_with_images/total_plots*100:>5.1f}%)
Total Images:                   {total_images:>8}
Avg Images per Plot:            {avg_images:>8.1f}

================================================================================
RECORD COMPLETENESS
================================================================================
Birth Dates:                    {birth_dates:>8} ({birth_dates/total_occupants*100:>5.1f}%)
Death Dates:                    {death_dates:>8} ({death_dates/total_occupants*100:>5.1f}%)

================================================================================
PLOT OWNERSHIP
================================================================================
Plots with Purchaser:           {with_purchaser:>8} ({with_purchaser/total_plots*100:>5.1f}%)
Plots with Current Owner:       {with_current_owner:>8} ({with_current_owner/total_plots*100:>5.1f}%)

================================================================================
KEY INSIGHTS
================================================================================

CURRENT STATUS:
- Cemetery is {occupied_lots/total_lots*100:.1f}% occupied ({occupied_lots} occupied lots out of {total_lots} total)
- {empty_lots} empty lots remaining
- {total_veterans} military veterans (including occupants, reserved spaces, and memorials)
- Record completeness: {birth_dates/total_occupants*100:.1f}% have birth dates, {death_dates/total_occupants*100:.1f}% have death dates
- Monument image coverage: {plots_with_images/total_plots*100:.1f}% of plots documented

SECTION OCCUPANCY (Highest to Lowest):
"""

    # List sections by occupancy rate
    sorted_sections = sorted(section_stats.items(), key=lambda x: x[1]['occupancy_rate'], reverse=True)
    for section_name, stats in sorted_sections:
        report += f"- {section_name}: {stats['occupancy_rate']:.1f}% occupied ({stats['occupants']}/{stats['lots']} lots)\n"

    report += f"""
================================================================================
Generated: {today}
Data Sources: plots.csv, lots.csv, occupants.csv, veterans.csv
================================================================================
"""

    return report

def generate_report(plots, lots, occupants, veterans):
    """Generate the complete statistics report."""
    today = datetime.now().strftime("%B %d, %Y")

    # Basic counts
    total_plots = len(plots)
    total_lots = len(lots)
    total_occupants = len(occupants)
    avg_lots_per_plot = total_lots / total_plots if total_plots > 0 else 0

    # Section statistics
    section_stats = calculate_section_stats(plots, lots, occupants)

    # Occupant status
    status_counts = Counter(occ.get('status', 'Other') for occ in occupants)

    # Lot status
    lot_status = calculate_lot_status(lots)

    # Occupied vs empty
    occupied_lots, empty_lots = count_occupied_lots(lots, occupants)
    avg_occupancy = (sum(s['occupants'] for s in section_stats.values()) / total_lots * 100) if total_lots > 0 else 0

    # Veterans
    total_veterans = len(veterans)

    # Monument images
    plots_with_images, total_images = count_image_plots(plots)
    avg_images = total_images / plots_with_images if plots_with_images > 0 else 0

    # Record completeness
    birth_dates, death_dates = calculate_record_completeness(occupants)

    # Ownership
    with_purchaser, with_current_owner = calculate_ownership(plots)

    # Generate markdown report
    report = f"""# ORRS ISLAND CEMETERY ASSOCIATION - COMPREHENSIVE STATISTICS
**Updated: {today}**

---

## OVERALL CEMETERY

| Metric | Current |
|--------|--------:|
| **Total Plots** | {total_plots} |
| **Total Lots** | {total_lots} |
| **Total Occupants/Records** | {total_occupants} |
| **Average Lots per Plot** | {avg_lots_per_plot:.2f} |

---

## BREAKDOWN BY SECTION

| Section | Plots | Lots | Occupants | Occupancy Rate |
|---------|------:|-----:|----------:|---------------:|
"""

    # Sort sections by name
    for section_name in sorted(section_stats.keys()):
        stats = section_stats[section_name]
        report += f"| **{section_name}** | {stats['plots']} | {stats['lots']} | {stats['occupants']} | {stats['occupancy_rate']:.1f}% |\n"

    report += f"""
---

## OCCUPANT STATUS

| Status | Count | Percentage |
|--------|------:|-----------:|
"""

    # Sort status by count (descending)
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_occupants * 100) if total_occupants > 0 else 0
        report += f"| **{status}** | {count} | {pct:.1f}% |\n"

    report += f"""
---

## LOT STATUS

"""
    for status, count in sorted(lot_status.items()):
        pct = (count / total_lots * 100) if total_lots > 0 else 0
        report += f"- **{status}:** {count} lots ({pct:.1f}%)\n"

    report += f"""
---

## LOT OCCUPANCY

- **Occupied Lots:** {occupied_lots} ({occupied_lots/total_lots*100:.1f}%)
- **Empty Lots:** {empty_lots} ({empty_lots/total_lots*100:.1f}%)
- **Average Occupancy Rate:** {avg_occupancy:.1f}%

---

## MILITARY VETERANS

| Metric | Current |
|--------|--------:|
| **Total Veterans** | {total_veterans} |

**📝 Note:** Veteran count sourced from veterans.csv (authoritative list). This includes all veterans regardless of burial status (occupants, reserved spaces, memorials).

---

## MONUMENT IMAGES

| Metric | Current |
|--------|--------:|
| **Plots with Images** | {plots_with_images} ({plots_with_images/total_plots*100:.1f}%) |
| **Total Images** | {total_images} |
| **Avg Images/Plot** | {avg_images:.1f} |

---

## RECORD COMPLETENESS

| Metric | Current |
|--------|--------:|
| **Birth Dates** | {birth_dates} ({birth_dates/total_occupants*100:.1f}%) |
| **Death Dates** | {death_dates} ({death_dates/total_occupants*100:.1f}%) |

---

## PLOT OWNERSHIP

| Metric | Current |
|--------|--------:|
| **Plots with Purchaser** | {with_purchaser} ({with_purchaser/total_plots*100:.1f}%) |
| **Plots with Current Owner** | {with_current_owner} ({with_current_owner/total_plots*100:.1f}%) |

---

## KEY INSIGHTS

### 🎯 Current Status
- **Cemetery is {occupied_lots/total_lots*100:.1f}% occupied** ({occupied_lots} occupied lots out of {total_lots} total)
- **{empty_lots} empty lots remaining**
- **{total_veterans} military veterans** (including occupants, reserved spaces, and memorials)
- **Record completeness:** {birth_dates/total_occupants*100:.1f}% have birth dates, {death_dates/total_occupants*100:.1f}% have death dates
- **Monument image coverage:** {plots_with_images/total_plots*100:.1f}% of plots documented

### 📊 Section Occupancy
"""

    # List sections by occupancy rate
    sorted_sections = sorted(section_stats.items(), key=lambda x: x[1]['occupancy_rate'], reverse=True)
    for section_name, stats in sorted_sections:
        report += f"- **{section_name}:** {stats['occupancy_rate']:.1f}% occupied ({stats['occupants']}/{stats['lots']} lots)\n"

    report += f"""
---

*Generated: {today}*
*Data Sources: plots.csv, lots.csv, occupants.csv, veterans.csv*
"""

    return report

def main():
    """Main function."""
    # Determine data directory path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(parent_dir, 'data')

    print("ORRS Island Cemetery Association - Statistics Generator")
    print("=" * 60)
    print()

    # Read CSV files
    print("Reading data files...")
    plots = read_csv(os.path.join(data_dir, 'plots.csv'))
    lots = read_csv(os.path.join(data_dir, 'lots.csv'))
    occupants = read_csv(os.path.join(data_dir, 'occupants.csv'))
    veterans = read_csv(os.path.join(data_dir, 'veterans.csv'))

    print(f"  - {len(plots)} plots")
    print(f"  - {len(lots)} lots")
    print(f"  - {len(occupants)} occupants")
    print(f"  - {len(veterans)} veterans")
    print()

    # Generate reports
    print("Generating statistics reports...")
    markdown_report = generate_report(plots, lots, occupants, veterans)
    text_report = generate_text_report(plots, lots, occupants, veterans)

    # Save reports
    today = datetime.now().strftime("%Y-%m-%d")
    md_output_file = os.path.join(parent_dir, f"Cemetery Statistics {today}.md")
    txt_output_file = os.path.join(parent_dir, f"Cemetery Statistics {today}.txt")

    with open(md_output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_report)

    with open(txt_output_file, 'w', encoding='utf-8') as f:
        f.write(text_report)

    print(f"✓ Markdown report saved to: {md_output_file}")
    print(f"✓ Text report saved to:     {txt_output_file}")
    print()
    print("Summary:")
    print(f"  - Total Plots: {len(plots)}")
    print(f"  - Total Lots: {len(lots)}")
    print(f"  - Total Occupants: {len(occupants)}")
    print(f"  - Total Veterans: {len(veterans)}")
    print(f"  - Occupancy: {len([o for o in occupants]) / len(lots) * 100:.1f}%")

if __name__ == '__main__':
    main()
