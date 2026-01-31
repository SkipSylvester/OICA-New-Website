# OICA Interactive Cemetery Mapping System - Project Plan

## Vision
Create a comprehensive, zoomable overhead mapping system of the OICA Cemetery that allows users to:
- View the entire cemetery from above
- Zoom in on specific sections, plots, and individual lots
- Click on any location to see occupant information and historical details
- View monument images directly on the map
- Navigate intuitively between cemetery sections

## Current State (Phase 0)

### Existing Assets
- **Static image map**: `images/OICA imap 2021.jpg` (1200px wide)
- **HTML imagemap**: `cemetery-grounds.html` with 428+ clickable plot regions
- **Complete database**:
  - 340 plots across 5 sections
  - 1,597 lots
  - 997 occupants with historical data
  - Veteran information (122 veterans marked)
  - Monument images organized by section
- **Five cemetery sections**:
  - Church Yard (CY) - 24 plots
  - Old Yard (OY) - 156 plots
  - New Yard (NY) - 56 plots
  - Upper Terrace (UT) - 78 plots
  - Intervale Terrace (IT) - 76 plots (some commented out)

### Current Limitations
- Static image map doesn't zoom smoothly
- Can only click plot-level, not individual lots
- No visual indication of available lots vs occupied
- No section-level navigation
- Monument images separate from map view

## Future Phases

### Phase 1: Enhanced Static Map (Foundation)
**Goal**: Improve current image map with better interactivity and visual information

**Features**:
1. **Visual lot status overlay**
   - Color-code plots by availability
   - Green = available lots
   - Gray = fully occupied
   - Yellow = partially occupied
   - Red = not available (obstructions)

2. **Hover tooltips**
   - Show plot ID on hover
   - Display occupant count
   - Show availability status

3. **Section highlighting**
   - Ability to highlight entire sections
   - Section boundary overlays
   - Section-specific information panels

4. **Responsive design**
   - Better mobile/tablet support
   - Pan and zoom controls
   - Touch-friendly interface

**Technical Approach**:
- Use JavaScript canvas or SVG overlays on existing image
- Add CSS for hover effects
- Integrate with existing data/lots.csv for status info

### Phase 2: Individual Lot Clickability
**Goal**: Allow clicking on individual lots within plots

**Features**:
1. **Lot-level mapping**
   - Generate coordinates for each lot within a plot
   - 4 lots per plot (L1-L4) arranged north to south
   - Click individual lot to see specific occupant

2. **Plot detail view**
   - Popup showing all 4 lots in a plot
   - Visual representation of lot layout
   - Click lot to go to occupant details

3. **Monument image integration**
   - Show monument thumbnails on map
   - Click image to view full size
   - Associate images with specific lots

**Technical Approach**:
- Calculate lot subdivisions within plot rectangles
- Use JavaScript to create dynamic clickable regions
- Create popup modal system for plot details

### Phase 3: Overhead Photo Integration
**Goal**: Replace static diagram with actual overhead photography

**Prerequisites**:
- Obtain high-resolution overhead photos of cemetery
  - Drone photography (recommended)
  - Or aerial photography
  - Or satellite imagery
- Photos for each section separately
- Georeferenced if possible

**Features**:
1. **Photo-based map**
   - Real overhead view of cemetery
   - Zoomable to see individual monuments
   - Aligned with database coordinates

2. **Plot overlay system**
   - Transparent overlay showing plot boundaries
   - Toggle on/off to see raw photo
   - Lot subdivisions visible at high zoom

3. **Photo stitching**
   - Combine section photos into cohesive whole
   - Smooth transitions between sections
   - Consistent scale across sections

**Technical Approach**:
- Use Leaflet.js or OpenLayers for map framework
- Create custom tile layers if needed
- Establish coordinate system mapping database IDs to photo locations

### Phase 4: Advanced Zoom and Navigation
**Goal**: Smooth, Google Maps-style zoom and pan

**Features**:
1. **Multi-level zoom**
   - Level 0: Entire cemetery overview
   - Level 1: Section view
   - Level 2: Plot cluster view
   - Level 3: Individual plot view
   - Level 4: Individual lot/monument detail

2. **Smart information density**
   - Show appropriate detail level at each zoom
   - Hide labels when zoomed out
   - Progressive detail revelation

3. **Mini-map navigator**
   - Small overview map showing current view location
   - Quick jump to sections
   - Breadcrumb navigation

4. **Search and find**
   - Search by occupant name
   - Auto-zoom to their location
   - Highlight their monument

**Technical Approach**:
- Implement tile-based zoom system
- Create image pyramid (multiple resolution levels)
- Use Leaflet.js with custom markers

### Phase 5: AI-Enhanced Features (Future/Advanced)
**Goal**: Leverage AI for enhanced user experience

**Features**:
1. **AI monument recognition**
   - Automatically identify monuments in photos
   - Extract text from headstones
   - Match to database records
   - Suggest database corrections

2. **Historical narrative**
   - AI-generated historical context
   - Family relationship visualization
   - Timeline views of burials
   - Notable person identification

3. **3D visualization**
   - 3D models of monuments
   - Virtual cemetery tour
   - Augmented reality overlay for on-site visits

4. **Predictive analytics**
   - Cemetery capacity planning
   - Historical trend analysis
   - Preservation needs identification

## Data Requirements

### Coordinate System Needed
To map database to photos, we need:

1. **Plot corner coordinates**
   - Either GPS coordinates for each plot
   - Or pixel coordinates on reference photo
   - Stored in new `plot_coordinates.csv`

2. **Section boundaries**
   - Polygon definitions for each section
   - Used for section highlighting and navigation

3. **Lot subdivisions**
   - Mathematical rules for dividing plot into 4 lots
   - Standard layout: north to south (L1, L2, L3, L4)
   - Handle special cases (plots with fewer lots)

### New Data Files Needed
```
data/plot_coordinates.csv - GPS or pixel coords for each plot
data/section_boundaries.csv - Section polygon definitions
data/monument_positions.csv - Precise location of each monument
```

### Photo Requirements
When you're ready to provide photos:

1. **Overhead photos needed**:
   - Church Yard section
   - Old Yard section
   - New Yard section
   - Upper Terrace section
   - Intervale Terrace section
   - Full cemetery composite (if available)

2. **Photo specifications**:
   - High resolution (minimum 4000px on longest side)
   - Taken from directly overhead (nadir view)
   - Good lighting (overcast day ideal to avoid shadows)
   - Consistent scale across all sections
   - Include some overlap between sections

3. **Reference markers helpful**:
   - Known plot IDs visible in photos
   - Section boundaries marked
   - GPS coordinates of reference points

## Implementation Roadmap

### Immediate Next Steps (Phase 1)
1. Create JavaScript overlay system for current map
2. Add CSS styling for lot status colors
3. Integrate status data from lots.csv
4. Add hover tooltips showing plot information
5. Create section highlighting functionality

### After Phase 1 Complete
- User provides overhead photos
- Develop coordinate mapping system
- Build Phase 2 lot-level clickability

### Long-term Development
- Phases 3-5 as resources and technology allow
- Continuous refinement based on user feedback
- Integration of new historical research
- AI features as AI technology advances

## Technology Stack Recommendations

### Phase 1 (Current)
- Vanilla JavaScript
- CSS3 for styling
- HTML5 canvas or SVG for overlays
- PapaParse (already in use) for CSV data

### Phase 2-3 (With Photos)
- **Leaflet.js** - Open source, mobile-friendly mapping
  - OR **OpenLayers** - More features, steeper learning curve
- Custom tile generation for zoom levels
- JavaScript for interactivity

### Phase 4-5 (Advanced)
- **Mapbox GL JS** - Advanced visualization
- **Three.js** - 3D monument models
- **TensorFlow.js** - AI monument recognition
- Backend server for heavy processing (optional)

## Cost Considerations

### Free/Low Cost Options
- Leaflet.js - Free and open source
- Drone photos - Borrow/rent drone, DIY photography
- Self-hosted - Use existing web hosting
- OpenStreetMap base layers - Free

### Investment Options
- Professional drone photography service
- Mapbox (paid tiers for high usage)
- Cloud hosting for tile serving
- 3D scanning services for monuments

## Accessibility and Preservation

### Ensure System Is:
- Mobile responsive
- Screen reader compatible
- Printer-friendly
- Exportable data
- Future-proof file formats
- Well-documented for future maintainers

## Notes
- This is a living document
- Update as project evolves
- Track progress and decisions
- Document lessons learned
- Share with OICA board for input
