// Přidání event listeneru pro změnu hodnoty v poli v rámci fetchBookDetails
async function fetchBookDetails(tab) {
    console.log('Fetching book details...');

    const isbnInputId = tab === 'isbn' ? 'isbn1' : 'manual-isbn1';
    const detailsSectionId = tab === 'isbn' ? 'isbn-details' : 'manual-details';

    const isbnInput = document.getElementById(isbnInputId);
    const isbn1 = isbnInput?.value;

    if (isbn1) {
        try {
            const response = await fetch(`/scripts/fetch_book_details/?isbn=${isbn1}`);
            console.log('API response received');
            if (response.status === 429) {
                alert('Za to může Google, nejsou data :( !');
                return false;
            }
            const data = await response.json();
            console.log('Data parsed from JSON:', data);

            // Zkontrolujeme, jestli jsme získali nějaká data
            const detailsSection = document.getElementById(detailsSectionId);
            if (data && Object.keys(data).length > 0) {
                if (detailsSection) {
                    detailsSection.style.display = 'block'; // Zobrazí pole po úspěšném načtení dat
                }

                // Vyplnění polí podle získaných dat
                const titleElement = document.getElementById('isbn-title');
                if (titleElement) {
                    titleElement.value = data.title || '';
                }

                const authorElement = document.getElementById('isbn-author');
                if (authorElement) {
                    authorElement.value = data.author || '';
                }

                const yearElement = document.getElementById('isbn-year');
                if (yearElement) {
                    yearElement.value = data.year || '';
                }

                const pagesElement = document.getElementById('isbn-pages');
                if (pagesElement) {
                    pagesElement.value = data.pages || '';
                }

                const subtitleElement = document.getElementById('isbn-subtitle');
                if (subtitleElement) {
                    subtitleElement.value = data.subtitle || '';
                }

                const descriptionElement = document.getElementById('isbn-description');
                if (descriptionElement) {
                    descriptionElement.value = data.description || '';
                }

                const languageElement = document.getElementById('isbn-language');
                if (languageElement) {
                    languageElement.value = data.language || '';
                }

                const imgElement = document.getElementById('isbn-img');
                if (imgElement) {
                    imgElement.value = data.img || 'noimg.png';
                }

                const googleIdElement = document.getElementById('isbn-googleid');
                if (googleIdElement) {
                    googleIdElement.value = data.googleid || '';
                }

                // Dynamické přidání ISBN polí pro ISBN tab
                const isbnFieldsContainer = document.getElementById('isbn-isbn-fields-container');
                console.log(isbnFieldsContainer)
                if (isbnFieldsContainer) {
                    isbnFieldsContainer.innerHTML = '';  // Vymazání existujících polí
                    if (data.isbns && data.isbns.length > 0) {
                        data.isbns.forEach((isbn, index) => {
                            const isbnFieldGroup = document.createElement('div');
                            isbnFieldGroup.className = 'form-group isbn-isbn-field-group';

                            isbnFieldGroup.innerHTML = `
                                <label for="isbn-isbn-identifier-${index}">ISBN: ( bez pomlček, lomítek atd. )</label>
                                <input type="text" id="isbn-isbn-identifier-${index}" name="isbn-isbn-identifier-${index}" value="${isbn.identifier}">
                                <label for="isbn-isbn-type-${index}">Druh:</label>
                                <select id="isbn-isbn-type-${index}" name="isbn-isbn-type-${index}" disabled>
                                    <option value="ISBN_10" ${isbn.type === 'ISBN_10' ? 'selected' : ''}>ISBN 10</option>
                                    <option value="ISBN_13" ${isbn.type === 'ISBN_13' ? 'selected' : ''}>ISBN 13</option>
                                    <option value="OTHER" ${isbn.type === 'OTHER' ? 'selected' : ''}>Other</option>
                                </select>
                            `;

                            isbnFieldsContainer.appendChild(isbnFieldGroup);
                        });
                    }
                }
            } else {
                if (isbnInput) {
                    isbnInput.value = ''; // Vymaže ISBN z inputu
                }
                if (detailsSection) {
                    detailsSection.style.display = 'none'; // Skryje sekci detailů
                }
                alert('Nebyla nalezena žádna kniha podle zadaného ISBN.');
            }
        } catch (error) {
            console.error('Error fetching book details:', error);
            alert('Nastala chyba při načítání dat. Zkuste to prosím znovu');
        }
    } else {
        alert('Prosím vložte platné ISBN.');
    }
}
