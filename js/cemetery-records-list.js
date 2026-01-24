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

                    // Convert "First Middle Last" or "First Middle Last, Suffix" to "Last, First Middle Suffix"
                    let formattedName = nameOriginal; // default if parsing fails

                    // Check if name already has a comma (indicating suffix like "Bailey, Jr.")
                    if (nameOriginal.includes(',')) {
                        // Name is like "Lawrence Bailey, Jr." - need to rearrange
                        const parts = nameOriginal.split(',').map(p => p.trim());
                        if (parts.length === 2) {
                            const mainName = parts[0].trim();
                            const suffix = parts[1].trim();

                            // Split main name into parts
                            const nameParts = mainName.split(/\s+/);
                            if (nameParts.length >= 2) {
                                const lastName = nameParts[nameParts.length - 1];
                                const firstMiddle = nameParts.slice(0, -1).join(' ');
                                formattedName = lastName + ', ' + firstMiddle + ' ' + suffix;
                            }
                        }
                    } else {
                        // No comma - check if last word is a suffix (Jr., Sr., II, III, IV, etc.)
                        const nameParts = nameOriginal.trim().split(/\s+/);
                        if (nameParts.length >= 2) {
                            const lastWord = nameParts[nameParts.length - 1];
                            // Check if last word is a suffix
                            if (/^(Jr\.?|Sr\.?|II|III|IV|V|VI)$/i.test(lastWord)) {
                                // Name is like "John Atwood Jr." - treat last word as suffix
                                const suffix = lastWord;
                                const nameWithoutSuffix = nameParts.slice(0, -1);
                                if (nameWithoutSuffix.length >= 2) {
                                    const lastName = nameWithoutSuffix[nameWithoutSuffix.length - 1];
                                    const firstMiddle = nameWithoutSuffix.slice(0, -1).join(' ');
                                    formattedName = lastName + ', ' + firstMiddle + ' ' + suffix;
                                } else if (nameWithoutSuffix.length === 1) {
                                    // Single name + suffix (shouldn't happen, but handle it)
                                    formattedName = nameWithoutSuffix[0] + ' ' + suffix;
                                }
                            } else {
                                // Normal "First Middle Last" format
                                const lastName = nameParts[nameParts.length - 1];
                                const firstMiddle = nameParts.slice(0, -1).join(' ');
                                formattedName = lastName + ', ' + firstMiddle;
                            }
                        }
                    }

                    // Determine superscript based on status
                    let superscript = '';
                    if (status === 'Cremation') superscript = 'c';
                    else if (status === 'Vault') superscript = 'v';
                    else if (status === 'Memorial') superscript = 'm';
                    else if (status === 'Reserved') superscript = 'r';

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
                    html += '<a href="cemetery-viewer.html?plot=' + person.plotId + '">' +
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
