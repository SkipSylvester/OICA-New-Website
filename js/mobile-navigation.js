/**
 * Mobile-friendly touch navigation handler
 * Handles hamburger menu and touch/click-friendly dropdowns
 */

(function() {
    'use strict';

    // Detect if we're on a touch device
    const isTouchDevice = ('ontouchstart' in window) ||
                         (navigator.maxTouchPoints > 0) ||
                         (navigator.msMaxTouchPoints > 0);

    // Initialize when DOM is ready
    function initMobileNav() {
        // Hamburger menu toggle
        const hamburgerBtn = document.getElementById('hamburger-btn');
        const navMenu = document.getElementById('nav-menu');

        if (hamburgerBtn && navMenu) {
            hamburgerBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                navMenu.classList.toggle('active');

                // Update aria attribute for accessibility
                const isExpanded = navMenu.classList.contains('active');
                hamburgerBtn.setAttribute('aria-expanded', isExpanded);

                // Change icon
                const icon = hamburgerBtn.querySelector('.hamburger-icon');
                if (icon) {
                    icon.textContent = isExpanded ? '✕' : '☰';
                }
            });

            // Close menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!e.target.closest('nav')) {
                    navMenu.classList.remove('active');
                    hamburgerBtn.setAttribute('aria-expanded', 'false');
                    const icon = hamburgerBtn.querySelector('.hamburger-icon');
                    if (icon) {
                        icon.textContent = '☰';
                    }
                }
            });
        }

        // Dropdown handlers
        const dropdowns = document.querySelectorAll('.dropdown');

        dropdowns.forEach(function(dropdown) {
            const trigger = dropdown.querySelector('h1');
            const content = dropdown.querySelector('.dropdown-content');

            if (!trigger || !content) return;

            // On touch devices, add click handlers
            if (isTouchDevice) {
                // Prevent default link behavior if it's wrapped in an anchor
                trigger.style.cursor = 'pointer';

                trigger.addEventListener('click', function(e) {
                    // If the h1 contains a link that's just for navigation (not a dropdown)
                    // let it proceed normally
                    if (!content.children.length) return;

                    e.preventDefault();
                    e.stopPropagation();

                    // Toggle the dropdown
                    const isOpen = content.classList.contains('show');

                    // Close all other dropdowns first
                    document.querySelectorAll('.dropdown-content.show').forEach(function(openContent) {
                        if (openContent !== content) {
                            openContent.classList.remove('show');
                        }
                    });

                    // Toggle this dropdown
                    if (isOpen) {
                        content.classList.remove('show');
                    } else {
                        content.classList.add('show');
                    }
                });
            }

            // On mobile screens (regardless of touch), convert to click-based
            if (window.innerWidth <= 768) {
                trigger.style.cursor = 'pointer';

                trigger.addEventListener('click', function(e) {
                    if (!content.children.length) return;

                    e.preventDefault();
                    e.stopPropagation();

                    // Toggle the dropdown
                    const isOpen = content.classList.contains('show');

                    // Close all other dropdowns
                    document.querySelectorAll('.dropdown-content.show').forEach(function(openContent) {
                        if (openContent !== content) {
                            openContent.classList.remove('show');
                        }
                    });

                    // Toggle this dropdown
                    content.classList.toggle('show');
                });
            }
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-content.show').forEach(function(content) {
                    content.classList.remove('show');
                });
            }
        });
    }

    // Initialize when DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileNav);
    } else {
        initMobileNav();
    }

    // Re-initialize on window resize (if switching between desktop/mobile)
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Close all dropdowns on resize
            document.querySelectorAll('.dropdown-content.show').forEach(function(content) {
                content.classList.remove('show');
            });
        }, 250);
    });

})();
