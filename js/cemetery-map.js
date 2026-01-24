/**
 * Cemetery Interactive Map System - Phase 1
 * Adds visual overlays, hover tooltips, and status indicators to the static cemetery map
 */

document.addEventListener('DOMContentLoaded', function() {
    // Configuration
    const SECTION_COLORS = {
        'Church Yard': '#FF6B6B',
        'Old Yard': '#4ECDC4',
        'New Yard': '#95E1D3',
        'Upper Terrace': '#F38181',
        'Intervale Terrace': '#AA96DA'
    };

    const STATUS_COLORS = {
        'Available': 'rgba(76, 175, 80, 0.3)',      // Green
        'Partially Occupied': 'rgba(255, 235, 59, 0.3)', // Yellow
        'Fully Occupied': 'rgba(158, 158, 158, 0.3)',   // Gray
        'Not Available': 'rgba(244, 67, 54, 0.3)'       // Red
    };

    // State
    let plotData = {};
    let lotData = {};
    let occupantData = {};
    let currentHighlightSection = null;
    let currentTooltipStyle = 'detailed'; // Options: 'basic', 'detailed', 'occupants', 'full'

    // Initialize the map
    function init() {
        console.log('Cemetery Map: Initializing...');
        loadData();
    }

    // Load all cemetery data
    function loadData() {
        let plotsLoaded = false;
        let lotsLoaded = false;
        let occupantsLoaded = false;

        // Check if all data is loaded and initialize map
        function checkAllDataLoaded() {
            if (plotsLoaded && lotsLoaded && occupantsLoaded) {
                console.log('All data loaded, initializing map...');
                enhanceMapAreas();
                setupMapInteractions();
                createLegend();
            }
        }

        // Load plots data
        Papa.parse('data/plots.csv', {
            download: true,
            header: true,
            skipEmptyLines: true,
            complete: function(results) {
                results.data.forEach(plot => {
                    plotData[plot.plot_id] = plot;
                });
                console.log(`Loaded ${Object.keys(plotData).length} plots`);
                plotsLoaded = true;
                checkAllDataLoaded();
            },
            error: function(error) {
                console.error('Error loading plots.csv:', error);
            }
        });

        // Load lots data
        Papa.parse('data/lots.csv', {
            download: true,
            header: true,
            skipEmptyLines: true,
            complete: function(results) {
                results.data.forEach(lot => {
                    lotData[lot.lot_id] = lot;
                });
                console.log(`Loaded ${Object.keys(lotData).length} lots`);
                lotsLoaded = true;
                checkAllDataLoaded();
            },
            error: function(error) {
                console.error('Error loading lots.csv:', error);
            }
        });

        // Load occupants data
        Papa.parse('data/occupants.csv', {
            download: true,
            header: true,
            skipEmptyLines: true,
            complete: function(results) {
                results.data.forEach(occupant => {
                    const lotId = occupant.lot_id;
                    if (!occupantData[lotId]) {
                        occupantData[lotId] = [];
                    }
                    occupantData[lotId].push(occupant);
                });
                console.log(`Loaded ${results.data.length} occupants`);
                occupantsLoaded = true;
                checkAllDataLoaded();
            },
            error: function(error) {
                console.error('Error loading occupants.csv:', error);
            }
        });
    }

    // Enhance all map areas with data-driven attributes
    function enhanceMapAreas() {
        const areas = document.querySelectorAll('area[href*="cemetery-viewer.html"]');

        areas.forEach(area => {
            // Extract plot ID from href
            const href = area.getAttribute('href');
            const match = href.match(/plot=([A-Z0-9]+)/);
            if (!match) return;

            const plotId = match[1];
            const plot = plotData[plotId];

            if (!plot) return;

            // Get lot status for this plot
            const plotStatus = getPlotStatus(plotId);

            // Add data attributes
            area.setAttribute('data-plot-id', plotId);
            area.setAttribute('data-section', plot.section_name);
            area.setAttribute('data-status', plotStatus.status);
            area.setAttribute('data-occupant-count', plotStatus.occupantCount);
            area.setAttribute('data-available-count', plotStatus.availableCount);

            // Remove the title attribute to prevent browser's default tooltip
            area.removeAttribute('title');

            // Store plot data for dynamic tooltip generation
            area.plotData = plot;
            area.plotStatus = plotStatus;
        });

        console.log(`Enhanced ${areas.length} map areas`);
    }

    // Determine plot status based on lot data
    function getPlotStatus(plotId) {
        // Get all lots for this plot
        const plotLots = Object.values(lotData).filter(lot =>
            lot.lot_id.startsWith(plotId + '-')
        );

        let occupiedCount = 0;
        let availableCount = 0;
        let totalCount = plotLots.length;

        plotLots.forEach(lot => {
            const status = lot.status || '';
            const lotId = lot.lot_id;
            const hasOccupants = occupantData[lotId] && occupantData[lotId].length > 0;

            if (status === 'Available') {
                availableCount++;
            } else if (hasOccupants || status === 'Occupied' || status === 'Fully Occupied') {
                occupiedCount++;
            }
        });

        let overallStatus = 'Unknown';
        if (totalCount === 0) {
            overallStatus = 'Unknown';
        } else if (availableCount === totalCount) {
            overallStatus = 'Available';
        } else if (occupiedCount === totalCount) {
            overallStatus = 'Fully Occupied';
        } else if (availableCount > 0) {
            overallStatus = 'Partially Occupied';
        } else {
            overallStatus = 'Not Available';
        }

        return {
            status: overallStatus,
            occupantCount: Object.values(occupantData).filter(occs =>
                occs.some(o => o.lot_id.startsWith(plotId + '-'))
            ).reduce((sum, occs) => sum + occs.length, 0),
            availableCount: availableCount,
            totalLots: totalCount
        };
    }

    // Create tooltip HTML content
    // tooltipStyle options: 'basic', 'detailed', 'occupants', 'full'
    function createTooltipContent(plotId, plot, status, tooltipStyle = 'detailed') {
        let content = '';

        switch(tooltipStyle) {
            case 'basic':
                // Minimal info - just plot ID and status
                content = `<strong>${plotId}</strong><br>`;
                content += `${plot.section_name}<br>`;
                content += `<span style="color: ${getStatusColor(status.status)}">${status.status}</span>`;
                break;

            case 'detailed':
                // Default - plot info with counts
                content = `<strong>${plotId}</strong><br>`;
                content += `${plot.section_name}<br>`;
                content += `<div style="margin-top: 5px; padding-top: 5px; border-top: 1px solid rgba(255,255,255,0.3);">`;
                content += `Status: <span style="color: ${getStatusColor(status.status)}">${status.status}</span><br>`;

                if (status.totalLots > 0) {
                    content += `Total lots: ${status.totalLots}<br>`;
                }
                if (status.occupantCount > 0) {
                    content += `Occupants: ${status.occupantCount}<br>`;
                }
                if (status.availableCount > 0) {
                    content += `<span style="color: #76c7c0;">Available: ${status.availableCount}</span>`;
                }
                content += `</div>`;

                // Add purchaser if available
                if (plot.purchaser && plot.purchaser !== 'Unknown') {
                    content += `<div style="margin-top: 5px; font-size: 11px; color: #ccc;">Original Purchaser: ${plot.purchaser}</div>`;
                }
                break;

            case 'occupants':
                // Show occupant names
                content = `<strong>${plotId}</strong> - ${plot.section_name}<br>`;
                content += `<div style="margin-top: 5px; padding-top: 5px; border-top: 1px solid rgba(255,255,255,0.3);">`;

                const plotOccupants = getPlotOccupants(plotId);
                if (plotOccupants.length > 0) {
                    content += `<strong>Occupants (${plotOccupants.length}):</strong><br>`;
                    plotOccupants.forEach(occ => {
                        content += `• ${occ.name}`;
                        if (occ.veteran === 'Yes') {
                            content += ` 🇺🇸`;
                        }
                        content += `<br>`;
                    });
                } else {
                    content += `<span style="color: #76c7c0;">No occupants - ${status.availableCount} available</span>`;
                }
                content += `</div>`;
                break;

            case 'full':
                // Complete information including occupants and images
                content = `<strong>${plotId}</strong> - ${plot.section_name}<br>`;
                content += `<span style="color: ${getStatusColor(status.status)}">${status.status}</span>`;

                // Purchaser
                if (plot.purchaser && plot.purchaser !== 'Unknown') {
                    content += `<br><small>Purchaser: ${plot.purchaser}</small>`;
                }

                content += `<div style="margin-top: 5px; padding-top: 5px; border-top: 1px solid rgba(255,255,255,0.3);">`;

                // Occupants
                const fullOccupants = getPlotOccupants(plotId);
                if (fullOccupants.length > 0) {
                    content += `<strong>Occupants (${fullOccupants.length}):</strong><br>`;
                    fullOccupants.slice(0, 5).forEach(occ => {
                        content += `• ${occ.name}`;
                        if (occ.veteran === 'Yes') content += ` 🇺🇸`;
                        if (occ.death_date) content += ` (${occ.death_date})`;
                        content += `<br>`;
                    });
                    if (fullOccupants.length > 5) {
                        content += `<small>...and ${fullOccupants.length - 5} more</small><br>`;
                    }
                } else {
                    content += `No occupants<br>`;
                }

                // Available lots
                if (status.availableCount > 0) {
                    content += `<span style="color: #76c7c0;">Available lots: ${status.availableCount}</span><br>`;
                }

                // Monument images
                if (plot.monument_images) {
                    const imageCount = plot.monument_images.split(';').length;
                    content += `<small>📷 ${imageCount} monument image${imageCount > 1 ? 's' : ''}</small>`;
                }

                content += `</div>`;
                content += `<div style="margin-top: 5px; font-size: 10px; color: #999;">Click for full details</div>`;
                break;
        }

        return content;
    }

    // Helper: Get color for status
    function getStatusColor(status) {
        const colorMap = {
            'Available': '#76c7c0',
            'Partially Occupied': '#ffeb3b',
            'Fully Occupied': '#9e9e9e',
            'Not Available': '#f44336'
        };
        return colorMap[status] || '#ffffff';
    }

    // Helper: Get all occupants for a plot
    function getPlotOccupants(plotId) {
        const occupants = [];
        Object.keys(occupantData).forEach(lotId => {
            if (lotId.startsWith(plotId + '-')) {
                occupantData[lotId].forEach(occ => {
                    occupants.push(occ);
                });
            }
        });
        return occupants;
    }

    // Setup map interactions (hover, click)
    function setupMapInteractions() {
        const mapContainer = document.getElementById('Map');
        if (!mapContainer) return;

        // Create tooltip element
        const tooltip = document.createElement('div');
        tooltip.id = 'map-tooltip';
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            display: none;
            max-width: 200px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        `;
        document.body.appendChild(tooltip);

        // Add hover listeners to all map areas
        const areas = document.querySelectorAll('area[data-plot-id]');

        areas.forEach(area => {
            area.addEventListener('mouseenter', function(e) {
                const plotId = this.getAttribute('data-plot-id');
                const status = this.getAttribute('data-status');

                // Generate tooltip content dynamically based on current style
                const content = createTooltipContent(
                    plotId,
                    this.plotData,
                    this.plotStatus,
                    currentTooltipStyle
                );

                tooltip.innerHTML = content;
                tooltip.style.display = 'block';

                // Add status color indicator
                const statusColor = STATUS_COLORS[status] || 'rgba(128, 128, 128, 0.3)';
                tooltip.style.borderLeft = `4px solid ${statusColor.replace('0.3', '1')}`;
            });

            area.addEventListener('mousemove', function(e) {
                tooltip.style.left = (e.pageX + 15) + 'px';
                tooltip.style.top = (e.pageY + 15) + 'px';
            });

            area.addEventListener('mouseleave', function() {
                tooltip.style.display = 'none';
            });
        });

        console.log('Map interactions setup complete');
    }

    // Create map controls
    function createLegend() {
        const mapContainer = document.getElementById('Map');
        if (!mapContainer) return;

        const legend = document.createElement('div');
        legend.id = 'map-legend';
        legend.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            font-size: 12px;
            z-index: 100;
            min-width: 200px;
        `;

        let legendHTML = '<strong style="display: block; margin-bottom: 10px;">Hover Detail Level</strong>';

        // Add tooltip style selector
        legendHTML += '<select id="tooltip-style" style="width: 100%; padding: 5px;">';
        legendHTML += '<option value="basic">Basic - ID and Status</option>';
        legendHTML += '<option value="detailed" selected>Detailed - Counts and Purchaser</option>';
        legendHTML += '<option value="occupants">Occupants - Show Names</option>';
        legendHTML += '<option value="full">Full - Everything</option>';
        legendHTML += '</select>';

        legend.innerHTML = legendHTML;
        mapContainer.appendChild(legend);

        // Add tooltip style selector functionality
        document.getElementById('tooltip-style').addEventListener('change', function() {
            currentTooltipStyle = this.value;
            console.log(`Tooltip style changed to: ${currentTooltipStyle}`);
        });

        console.log('Map controls created');
    }

    // Initialize when DOM is ready
    init();
});
