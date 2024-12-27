async function fetchBookDetails(tab) {
    
    console.log('Fetching book details...');

    const isbnInputId = tab === 'isbn' ? 'isbn1' : 'manual-isbn1';
    const detailsSectionId = tab === 'isbn' ? 'isbn-details' : 'manual-details';
    const titleInputId = tab === 'isbn' ? 'isbn-title' : 'manual-title';
    const authorInputId = tab === 'isbn' ? 'isbn-author' : 'manual-author';
    const yearInputId = tab === 'isbn' ? 'isbn-year' : 'manual-year';
    const pagesInputId = tab === 'isbn' ? 'isbn-pages' : 'manual-pages';
    const subtitleInputId = tab === 'isbn' ? 'isbn-subtitle' : 'manual-subtitle';
    const descriptionInputId = tab === 'isbn' ? 'isbn-description' : 'manual-description';
    const languageInputId = tab === 'isbn' ? 'isbn-language' : 'manual-language';
    const imgInputId = tab === 'isbn' ? 'isbn-img' : 'manual-img';
    const googleidInputId = tab === 'isbn' ? 'isbn-googleid' : 'manual-googleid';

    const genreResultsId = tab === 'isbn' ? 'isbn-selected-genres' : 'manual-selected-genres';
    const publisherResultsId = tab === 'isbn' ? 'isbn-selected-publisher' : 'manual-selected-publisher';

    const isbn1 = document.getElementById(isbnInputId).value;

    if (isbn1) {
        try {
            const response = await fetch(`/scripts/fetch-book-details/?isbn=${isbn1}`);
            console.log('API response received');
            const data = await response.json();
            console.log('Data parsed from JSON:', data);

            if (data) {
                document.getElementById(detailsSectionId).style.display = 'block'; // Zobrazí pole po úspěšném načtení dat

                if (document.getElementById(titleInputId)) {
                    document.getElementById(titleInputId).value = data.title || '';
                }
                if (document.getElementById(authorInputId)) {
                    document.getElementById(authorInputId).value = data.author || '';
                }
                if (document.getElementById(yearInputId)) {
                    document.getElementById(yearInputId).value = data.year || '';
                }
                if (document.getElementById(pagesInputId)) {
                    document.getElementById(pagesInputId).value = data.pages || '';
                }
                if (document.getElementById(subtitleInputId)) {
                    document.getElementById(subtitleInputId).value = data.subtitle || '';
                }
                if (document.getElementById(descriptionInputId)) {
                    document.getElementById(descriptionInputId).value = data.description || '';
                }
                if (document.getElementById(languageInputId)) {
                    document.getElementById(languageInputId).value = data.language || '';
                }
                if (document.getElementById(imgInputId)) {
                    document.getElementById(imgInputId).value = data.googleid ? data.googleid : 'noimg.png';
                }
                if (document.getElementById(googleidInputId)) {
                    document.getElementById(googleidInputId).value = data.googleid || '';
                }

                // Přidání ISBN hodnot
                if (data.isbns) {
                    data.isbns.forEach((isbn) => {
                        if (isbn.type === 'ISBN_13' && document.getElementById(isbnInputId)) {
                            document.getElementById(isbnInputId).value = isbn.identifier;
                        } else if (isbn.type === 'ISBN_10' && document.getElementById(`${tab}-isbn2`)) {
                            document.getElementById(`${tab}-isbn2`).value = isbn.identifier;
                        } else if (isbn.type === 'OTHER' && document.getElementById(`${tab}-isbnOther`)) {
                            document.getElementById(`${tab}-isbnOther`).value = isbn.identifier;
                        }
                    });
                }

                if (data.genres) {
                    data.genres.forEach(genre => {
                        addGenre('isbn',genre.id, genre.name);
                    });
                }
                      
                if (data.publisher) {
                    addPublisher('isbn', data.publisher.id || null, data.publisher.name);
                }

            } else {
                alert('Book not found!');
            }
        } catch (error) {
            console.error('Error fetching book details:', error);
        }
    } else {
        alert('Please enter an ISBN.');
    }
}
