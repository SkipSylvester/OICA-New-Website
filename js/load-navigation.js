/**
 * Load shared navigation component
 * This script fetches the navigation HTML and injects it into the page
 */
(function() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadNavigation);
    } else {
        loadNavigation();
    }

    function loadNavigation() {
        // Find the navigation placeholder
        const navPlaceholder = document.getElementById('nav-placeholder');

        if (!navPlaceholder) {
            console.warn('Navigation placeholder not found. Add <div id="nav-placeholder"></div> where you want the navigation to appear.');
            return;
        }

        // Fetch the navigation HTML
        fetch('includes/navigation.html')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Navigation file not found: ' + response.statusText);
                }
                return response.text();
            })
            .then(html => {
                // Insert the navigation HTML
                navPlaceholder.innerHTML = html;
            })
            .catch(error => {
                console.error('Error loading navigation:', error);
                navPlaceholder.innerHTML = '<p style="color: red;">Error loading navigation menu.</p>';
            });
    }
})();
