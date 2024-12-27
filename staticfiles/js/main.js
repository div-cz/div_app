document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed in main.js');
    const isbnFetchButton = document.getElementById('isbn-fetch-book-details-btn');
    if (isbnFetchButton) {
        isbnFetchButton.addEventListener('click', () => {
            console.log('Start fetching book details for ISBN tab...');
            fetchBookDetails('isbn');
        });
    } else {
        console.log('Fetch Book Details button for ISBN not found');
    }

    const manualVerifyButton = document.getElementById('manual-verify-author-btn');
    if (manualVerifyButton) {
        manualVerifyButton.addEventListener('click', function() {
            console.log('Verify Author button clicked in manual tab');
            verifyAuthor('manual');
        });
    } else {
        console.log('Verify Author button for manual not found');
    }

    const isbnVerifyButton = document.getElementById('isbn-verify-author-btn');
    if (isbnVerifyButton) {
        isbnVerifyButton.addEventListener('click', function() {
            console.log('Verify Author button clicked in ISBN tab');
            verifyAuthor('isbn');
        });
    } else {
        console.log('Verify Author button for ISBN not found');
    }

    const manualCreateButton = document.getElementById('manual-create-author-btn');
    if (manualCreateButton) {
        manualCreateButton.addEventListener('click', function() {
            createAuthor('manual');
        });
    } else {
        console.log('Create Author button for manual not found');
    }

    const isbnCreateButton = document.getElementById('isbn-create-author-btn');
    if (isbnCreateButton) {
        isbnCreateButton.addEventListener('click', function() {
            createAuthor('isbn');
        });
    } else {
        console.log('Create Author button for ISBN not found');
    }

    // Přidání event listeneru pro tlačítka "Add Book"
    const isbnAddBookButton = document.querySelector('#isbn-form button[type="submit"]');
    const manualAddBookButton = document.querySelector('#manual-form button[type="submit"]');

    isbnAddBookButton.addEventListener('click', function(event) {
        console.log('ISBN Add Book button clicked');
        event.preventDefault();
        validateForm('isbn');
    });

    manualAddBookButton.addEventListener('click', function(event) {
        console.log('Manual Add Book button clicked');
        event.preventDefault();
        validateForm('manual');
    });
   document.getElementById('isbn-genre-search').addEventListener('input', () => searchGenres('isbn'));
   document.getElementById('manual-genre-search').addEventListener('input', () => searchGenres('manual'));
   document.getElementById('isbn-publisher-search').addEventListener('input', () => searchPublishers('isbn'));
   document.getElementById('manual-publisher-search').addEventListener('input', () => searchPublishers('manual'));
});

function validateForm(tab) {
    console.log('Validating form for tab:', tab);
    
    const authorIdInputId = tab === 'isbn' ? 'isbn-authorid' : 'manual-authorid';
    const titleInputId = tab === 'isbn' ? 'isbn-title' : 'manual-title';
    const yearInputId = tab === 'isbn' ? 'isbn-year' : 'manual-year';
    const pagesInputId = tab === 'isbn' ? 'isbn-pages' : 'manual-pages';

    const authorId = document.getElementById(authorIdInputId).value;
    const title = document.getElementById(titleInputId).value;
    const year = document.getElementById(yearInputId).value;
    const pages = document.getElementById(pagesInputId).value;

    if (!authorId) {
        alert('Author ID is required.');
        return false;
    }

    if (!title) {
        alert('Title is required.');
        return false;
    }

    if (!/^\d{4}$/.test(year) || year < 1500 || year > 2100) {
        alert('Year must be a number between 1500 and 2100.');
        return false;
    }

    if (!pages || (!/^\d+$/.test(pages) || pages < 1 || pages > 10000)) {
        alert('Pages must be a number between 1 and 10000.');
        return false;
    }

    // Pokud je validace úspěšná, odeslat formulář
    document.querySelector(`#${tab}-form`).submit();
}
