/**
 * Cemetery Records Names List Configuration
 * Loads and displays all cemetery occupants in a 3-column format
 */

document.addEventListener('DOMContentLoaded', function() {
    const namesListDiv = document.getElementById('namesList');

    if (!namesListDiv) {
        console.error('Names list element not found');
        return;
    }

    // Show loading message
    namesListDiv.innerHTML = '<p class="loading">Loading names list...</p>';

    // Parse the CSV file
    Papa.parse('data/occupants.csv', {
        download: true,
        header: true,
        skipEmptyLines: true,
        complete: function(results) {
            // Create array of people with their info
            const people = [];

            results.data.forEach(function(person) {
                if (person['name'] && person['lot_id']) {
                    // Extract plot_id from lot_id (e.g., "CYA1-L4" -> "CYA1")
                    const plotId = person['lot_id'].split('-')[0].toUpperCase();
                    const nameOriginal = person['name'];
                    const status = person['status'];

                    // Convert "First Middle Last" to "Last, First Middle"
                    const nameParts = nameOriginal.trim().split(/\s+/);
                    let formattedName = nameOriginal; // default if parsing fails
                    if (nameParts.length >= 2) {
                        const lastName = nameParts[nameParts.length - 1];
                        const firstMiddle = nameParts.slice(0, -1).join(' ');
                        formattedName = lastName + ', ' + firstMiddle;
                    }

                    // Determine superscript based on status
                    let superscript = '';
                    if (status === 'Memorial') superscript = 'm';
                    else if (status === 'Reserved') superscript = 'r';
                    // Check notes for additional info
                    if (person['notes'] && person['notes'].includes('Cremation')) superscript = 'c';
                    if (person['notes'] && person['notes'].includes('Vault')) superscript = 'v';

                    people.push({
                        name: formattedName,
                        plotId: plotId,
                        superscript: superscript
                    });
                }
            });

            // Sort alphabetically by last name (which is now at the beginning)
            people.sort((a, b) => a.name.localeCompare(b.name));

            // Split into three columns
            const itemsPerColumn = Math.ceil(people.length / 3);
            let html = '<div class="names-columns">';

            for (let col = 0; col < 3; col++) {
                html += '<div class="names-column">';
                const start = col * itemsPerColumn;
                const end = Math.min(start + itemsPerColumn, people.length);

                for (let i = start; i < end; i++) {
                    const person = people[i];
                    html += '<a href="cemetery-viewer-v9.html?plot=' + person.plotId + '">' +
                            person.name + '</a>';
                    if (person.superscript) {
                        html += '<sup>' + person.superscript + '</sup>';
                    }
                    html += '</br>\n';
                }

                html += '</div>';
            }

            html += '</div>';

            namesListDiv.innerHTML = html;
        },
        error: function(error) {
            namesListDiv.innerHTML = '<p style="color: red; text-align: center;">Error loading names list. Please ensure data/occupants.csv exists.</p>';
            console.error('Error loading CSV:', error);
        }
    });
});
