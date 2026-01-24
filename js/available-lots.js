/**
 * Available Lots Configuration
 * Loads and displays available cemetery lots categorized by section
 */

document.addEventListener('DOMContentLoaded', function() {
    const oldYardDiv = document.getElementById('oldYardLots');
    const upperTerraceDiv = document.getElementById('upperTerraceLots');
    const intervaleTerraceDiv = document.getElementById('intervaleTerraceLots');

    if (!oldYardDiv || !upperTerraceDiv || !intervaleTerraceDiv) {
        console.error('Available lots container elements not found');
        return;
    }

    // Show loading message
    oldYardDiv.innerHTML = '<p class="loading">Loading...</p>';
    upperTerraceDiv.innerHTML = '<p class="loading">Loading...</p>';
    intervaleTerraceDiv.innerHTML = '<p class="loading">Loading...</p>';

    // Parse the CSV file
    Papa.parse('data/available_lots.csv', {
        download: true,
        header: true,
        skipEmptyLines: true,
        complete: function(results) {
            let oldYardHtml = 'Old Yard Lots</br>';
            let upperTerraceHtml = 'Upper Terrace Lots</br>';
            let intervaleTerraceHtml = 'Intervale Terrace Lots</br>';

            let oldYardCount = 0;
            let upperTerraceCount = 0;
            let intervaleTerraceCount = 0;

            results.data.forEach(function(lot) {
                if (lot['plot_id'] && lot['lots_available']) {
                    const plotId = lot['plot_id'].toUpperCase();
                    const lotsText = lot['lots_available'];
                    const link = '<a href="cemetery-viewer.html?plot=' + plotId + '">' +
                                plotId + '-' + lotsText + '</a></br>\n';

                    // Count lots (count dashes and commas to estimate number of lots)
                    const lotCount = (lotsText.match(/[\d]/g) || []).length;

                    // Categorize by section
                    if (plotId.startsWith('OY')) {
                        oldYardHtml += link;
                        oldYardCount += lotCount;
                    } else if (plotId.startsWith('UT')) {
                        upperTerraceHtml += link;
                        upperTerraceCount += lotCount;
                    } else if (plotId.startsWith('IT')) {
                        intervaleTerraceHtml += link;
                        intervaleTerraceCount += lotCount;
                    }
                }
            });

            // Add counts to section headers
            oldYardHtml += 'Total Old Yard Lots = ' + oldYardCount + '</br></br>';
            upperTerraceHtml += 'Total Upper Terrace Lots = ' + upperTerraceCount + '</br></br>';
            intervaleTerraceHtml += 'Total Intervale Terrace Lots = ' + intervaleTerraceCount + '</br></br>';

            // Update displays
            oldYardDiv.innerHTML = oldYardHtml;
            upperTerraceDiv.innerHTML = upperTerraceHtml;
            intervaleTerraceDiv.innerHTML = intervaleTerraceHtml;

            // Update total
            const totalLots = oldYardCount + upperTerraceCount + intervaleTerraceCount;
            const totalElement = document.getElementById('totalLots');
            if (totalElement) {
                totalElement.innerHTML = 'Total Available Lots = ' + totalLots;
            }
        },
        error: function(error) {
            const errorMsg = '<p style="color: red; text-align: center;">Error loading available lots data.</p>';
            oldYardDiv.innerHTML = errorMsg;
            upperTerraceDiv.innerHTML = errorMsg;
            intervaleTerraceDiv.innerHTML = errorMsg;
            console.error('Error loading CSV:', error);
        }
    });
});
