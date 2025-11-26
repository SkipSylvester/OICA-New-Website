/**
 * CSV List Loader
 * Reusable utility for loading and displaying CSV data as lists
 */

/**
 * Load a CSV file and render it as a list
 * @param {Object} config - Configuration object
 * @param {string} config.csvPath - Path to the CSV file
 * @param {string} config.targetElementId - ID of the element to populate
 * @param {string} config.loadingMessage - Message to show while loading
 * @param {string} config.errorMessage - Message to show on error
 * @param {Function} config.renderRow - Function that takes a data row and returns HTML string
 */
function loadCSVList(config) {
    const targetElement = document.getElementById(config.targetElementId);

    if (!targetElement) {
        console.error('Target element not found:', config.targetElementId);
        return;
    }

    // Show loading message
    targetElement.innerHTML = '<p class="loading">' + config.loadingMessage + '</p>';

    // Parse the CSV file
    Papa.parse(config.csvPath, {
        download: true,
        header: true,
        skipEmptyLines: true,
        complete: function(results) {
            let html = '';

            results.data.forEach(function(row) {
                const rowHtml = config.renderRow(row);
                if (rowHtml) {
                    html += rowHtml;
                }
            });

            targetElement.innerHTML = html;
        },
        error: function(error) {
            targetElement.innerHTML = '<p style="color: red; text-align: center;">' +
                config.errorMessage + '</p>';
            console.error('Error loading CSV:', error);
        }
    });
}

// Wait for DOM to be ready before allowing CSV loading
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        // Trigger custom event when ready
        document.dispatchEvent(new Event('csvLoaderReady'));
    });
} else {
    // Already loaded
    document.dispatchEvent(new Event('csvLoaderReady'));
}
