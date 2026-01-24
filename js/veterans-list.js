/**
 * Veterans List Configuration
 * Loads and displays the military veterans list
 */

document.addEventListener('csvLoaderReady', function() {
    loadCSVList({
        csvPath: 'data/veterans.csv',
        targetElementId: 'veteranList',
        loadingMessage: 'Loading veterans list...',
        errorMessage: 'Error loading veterans list. Please ensure data/veterans.csv exists.',
        renderRow: function(veteran) {
            // Build the name
            let name = veteran['Last Name'];
            if (veteran['First Name']) {
                name += ', ' + veteran['First Name'];
            }
            if (veteran['Middle Name/Initial']) {
                name += ' ' + veteran['Middle Name/Initial'];
            }

            // Build the dates
            let dates = '';
            if (veteran['Birth Year'] || veteran['Death Year']) {
                dates = ' ' + (veteran['Birth Year'] || '') + '-' + (veteran['Death Year'] || '');
            }

            // Build the service info
            let service = '';
            if (veteran['Branch'] || veteran['Service Period']) {
                service = ' - ' + (veteran['Branch'] || '') +
                         (veteran['Branch'] && veteran['Service Period'] ? ', ' : '') +
                         (veteran['Service Period'] || '');
            }

            // Build the link to cemetery viewer
            if (veteran['Record ID']) {
                const plotId = veteran['Record ID'].toUpperCase();
                return '<a href="cemetery-viewer.html?plot=' + plotId + '">' +
                       name + dates + service + '</a></br>\n';
            }

            return '';
        }
    });
});
