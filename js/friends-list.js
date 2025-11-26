/**
 * Friends List Configuration
 * Loads and displays the Friends of the Cemetery honorees list
 */

document.addEventListener('csvLoaderReady', function() {
    loadCSVList({
        csvPath: 'data/friends.csv',
        targetElementId: 'friendsList',
        loadingMessage: 'Loading Friends list...',
        errorMessage: 'Error loading Friends list. Please ensure friends.csv exists.',
        renderRow: function(friend) {
            if (friend['plot_id'] && friend['name']) {
                const plotId = friend['plot_id'].toUpperCase();
                return '<a href="cemetery-viewer-v9.html?plot=' + plotId + '">' +
                       friend['name'] + '</a></br>\n';
            }
            return '';
        }
    });
});
