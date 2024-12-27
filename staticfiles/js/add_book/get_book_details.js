document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed in getBookDetails.js');

    // Načtení dat na základě book_id z URL
    const urlParams = new URLSearchParams(window.location.search);
    const bookIdFromUrl = urlParams.get('book_id');
    const bookIdInput = document.getElementById('book-id');

    if (bookIdFromUrl || (bookIdInput && bookIdInput.value)) {
        const bookId = bookIdFromUrl || bookIdInput.value;
        fetchBookDetailsById(bookId);
    }

    // Přidání listeneru na změnu hodnoty v poli `book-id`
    if (bookIdInput) {
        bookIdInput.addEventListener('input', () => {
            clearForm(); // Vymaže formulář, pokud se změní hodnota v poli
        });
    }

    // Přidání listeneru na odeslání formuláře
    const updateBookButton = document.querySelector('#update-form button[type="submit"]');
    if (updateBookButton) {
        updateBookButton.addEventListener('click', validateAndUpdateForm);
    }

    // Přidání listenerů pro vyhledávání žánrů a vydavatelů
    document.getElementById('update-genre-search').addEventListener('input', () => searchGenres('update'));
    document.getElementById('update-publisher-search').addEventListener('input', () => searchPublishers('update'));
});

/**
 * Načte detaily knihy na základě jejího ID
 * @param {string} bookId - ID knihy
 */
async function fetchBookDetailsById(bookId) {
    console.log(`Fetching book details for book ID: ${bookId}`);
    try {
        const response = await fetch(`/scripts/get_book_details/${bookId}/`);
        const data = await response.json();

        if (data.error) {
            alert(data.error);
        } else {
            populateBookDetails(data);
            // Kontrola existence a přidání `update-bookid`
            if (!document.getElementById('update-bookid')) {
                const hiddenBookIdField = document.createElement('input');
                hiddenBookIdField.type = 'hidden';
                hiddenBookIdField.id = 'update-bookid';
                hiddenBookIdField.value = bookId;
                document.getElementById('update-form').appendChild(hiddenBookIdField);
                console.log('Hidden book ID element přidán:', hiddenBookIdField);
            }
        }
        
    } catch (error) {
        console.error('Error fetching book details:', error);
        alert('Chyba při načítání dat');
    }
}

/**
 * Naplní formulář detaily knihy
 * @param {object} data - Data knihy získaná z API
 */
function populateBookDetails(data) {
    document.getElementById('update-details').style.display = 'block';

    // Naplnění polí hodnotami
    document.getElementById('update-title').value = data.title || '';
    document.getElementById('update-author').value = data.author || '';
    document.getElementById('update-year').value = data.year || '';
    document.getElementById('update-pages').value = data.pages || '';
    document.getElementById('update-subtitle').value = data.subtitle || '';
    document.getElementById('update-description').value = data.description || '';
    document.getElementById('update-language').value = data.language || '';
    document.getElementById('update-img').value = data.img || 'noimg.png';
    document.getElementById('update-googleid').value = data.googleid || '';
    document.getElementById('original-title').value = data.title || '';

    // Přidání ISBN
    const isbnFieldsContainer = document.getElementById('update-isbn-fields-container');
    isbnFieldsContainer.innerHTML = ''; // Vymaže existující pole

    if (data.isbn && data.isbn.length > 0) {
        document.getElementById('update-publisher-section').style.display = 'block';
        data.isbn.forEach((isbn, index) => {
            const isbnFieldGroup = document.createElement('div');
            isbnFieldGroup.className = 'form-group update-isbn-field-group';

            isbnFieldGroup.innerHTML = `
                <label for="update-isbn-identifier-${index}">ISBN:</label>
                <input type="text" id="update-isbn-identifier-${index}" name="update-isbn-identifier-${index}" value="${isbn.isbn}" class="readonly">
                <label for="update-isbn-type-${index}">Type:</label>
                <select id="update-isbn-type-${index}" name="update-isbn-type-${index}" class="readonly">
                    <option value="ISBN_10" ${isbn.isbntype === 'ISBN_10' ? 'selected' : ''}>ISBN 10</option>
                    <option value="ISBN_13" ${isbn.isbntype === 'ISBN_13' ? 'selected' : ''}>ISBN 13</option>
                    <option value="OTHER" ${isbn.isbntype === 'OTHER' ? 'selected' : ''}>Other</option>
                </select>
                                        `;

            isbnFieldsContainer.appendChild(isbnFieldGroup);
            if (isbn.publisher) {
                addPublisher('update', isbn.publisherid || null, isbn.publisher);
            }
        });
    }
    else {
        console.log("aaaaa")
        document.getElementById('update-publisher-search').style.display= 'none';
    }

    // Přidání autorů a žánrů
    if (data.writers) {
        data.writers.forEach(author => addAdditionalAuthor('update', author.id, author.name));
    }
    if (data.genres) {
        data.genres.forEach(genre => addGenre('update', genre.id, genre.name));
    }
}

/**
 * Vymaže formulář a skryje detaily
 */
function clearForm() {
    document.getElementById('update-details').style.display = 'none';

    // Vymazání všech polí
    const fieldsToClear = [
        'update-title',
        'update-author',
        'update-year',
        'update-pages',
        'update-subtitle',
        'update-description',
        'update-language',
        'update-img',
        'update-googleid',
        'original-title',
    ];
    fieldsToClear.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) field.value = '';
    });

    document.getElementById('update-isbn-fields-container').innerHTML = '';
    document.getElementById('update-additional-authors').innerHTML = '';
    document.getElementById('update-genres').innerHTML = '';
}