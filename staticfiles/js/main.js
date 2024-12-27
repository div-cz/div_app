document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed in main.js');

    // Tlačítka pro fetchování detailů knihy
    const isbnFetchButton = document.getElementById('isbn-fetch-book-details-btn');
    if (isbnFetchButton) {
        isbnFetchButton.addEventListener('click', () => {
            console.log('Start fetching book details for ISBN tab...');
            fetchBookDetails('isbn');
        });
    } else {
        console.log('Fetch Book Details button for ISBN not found');
    }

    // Tlačítka pro ověření autora
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

    const updateVerifyButton = document.getElementById('update-verify-author-btn');
    if (updateVerifyButton) {
        updateVerifyButton.addEventListener('click', function() {
            console.log('Verify Author button clicked in UPDATE tab');
            verifyAuthor('update');
        });
    } else {
        console.log('Verify Author button for Update not found');
    }

    // Tlačítka pro vytvoření autora
    const manualCreateButton = document.getElementById('manual-create-author-btn');
    if (manualCreateButton) {
        manualCreateButton.addEventListener('click', function() {
            createAuthor('manual');
        });
    } else {
        console.log('Create Author button for manual not found');
    }
    
    const updateCreateButton = document.getElementById('update-create-author-btn');
    if (updateCreateButton) {
        updateCreateButton.addEventListener('click', function() {
            createAuthor('update');
        });
    } else {
        console.log('Create Author button for update not found');
    }

    const isbnCreateButton = document.getElementById('isbn-create-author-btn');
    if (isbnCreateButton) {
        isbnCreateButton.addEventListener('click', function() {
            createAuthor('isbn');
        });
    } else {
        console.log('Create Author button for ISBN not found');
    }

    // Skrytí tlačítek pro vytvoření autora na začátku
    hideCreateAuthorButtons();

    // Přidání event listeneru pro tlačítka "Add Book"
    const isbnAddBookButton = document.querySelector('#isbn-form button[type="submit"]');
    const manualAddBookButton = document.querySelector('#manual-form button[type="submit"]');

    if (isbnAddBookButton) {
        isbnAddBookButton.addEventListener('click', function(event) {
            console.log('ISBN Add Book button clicked');
            event.preventDefault();
            validateForm('isbn');
        });
    }

    if (manualAddBookButton) {
        manualAddBookButton.addEventListener('click', function(event) {
            console.log('Manual Add Book button clicked');
            event.preventDefault();
            validateForm('manual');
        });
    }

    // Přidání event listenerů pro vyhledávání žánrů a vydavatelů
    document.getElementById('isbn-genre-search').addEventListener('input', () => searchGenres('isbn'));
    document.getElementById('manual-genre-search').addEventListener('input', () => searchGenres('manual'));
    document.getElementById('update-genre-search').addEventListener('input', () => searchGenres('update'));
    document.getElementById('isbn-publisher-search').addEventListener('input', () => searchPublishers('isbn'));
    document.getElementById('manual-publisher-search').addEventListener('input', () => searchPublishers('manual'));
    document.getElementById('update-author-search').addEventListener('input', () => searchAuthor('update'));
});

function hideCreateAuthorButtons() {
    const buttons = [
        document.getElementById('isbn-create-author-btn'),
        document.getElementById('manual-create-author-btn'),
        document.getElementById('update-create-author-btn')
    ];

    buttons.forEach(button => {
        if (button) {
            button.style.display = 'none';
        }
    });
}

async function checkAndSubmitForm(tab) {
    const titleInputId = tab === 'isbn' ? 'isbn-title' : (tab === 'manual' ? 'manual-title' : 'update-title');
    const authorIdInputId = tab === 'isbn' ? 'isbn-authorid' : (tab === 'manual' ? 'manual-authorid' : 'update-authorid');
    
    const title = document.getElementById(titleInputId).value;
    const authorid = document.getElementById(authorIdInputId).value;

    if (!title || !authorid) {
        alert('Title and Author ID are required.');
        return false;
    }

    try {
        const response = await fetch(`/scripts/check-book-exists/?title=${encodeURIComponent(title)}&authorid=${encodeURIComponent(authorid)}`);
        const data = await response.json();

        if (data.exists) {
            alert('This book already exists.');
            return false;
        } else {
            document.querySelector(`#${tab}-form`).submit();
        }
    } catch (error) {
        console.error('Error checking book existence:', error);
        alert('Failed to check if the book exists.');
        return false;
    }
}

async function validateForm(tab) {
    console.log('Validating form for tab:', tab);
    
    const authorIdInputId = tab === 'isbn' ? 'isbn-authorid' : (tab === 'manual' ? 'manual-authorid' : 'update-authorid');
    const titleInputId = tab === 'isbn' ? 'isbn-title' : (tab === 'manual' ? 'manual-title' : 'update-title');
    const yearInputId = tab === 'isbn' ? 'isbn-year' : (tab === 'manual' ? 'manual-year' : 'update-year');
    const pagesInputId = tab === 'isbn' ? 'isbn-pages' : (tab === 'manual' ? 'manual-pages' : 'update-pages');

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

    // Kontrola platnosti roku, pokud je zadaný
    if (!year || (!/^\d{4}$/.test(year) || year < 1500 || year > 2100)) {
        alert('Year must be a number between 1500 and 2100.');
        return false;
    }

    // Kontrola platnosti stránek, pokud je zadaný
    if (!pages || !/^\d+$/.test(pages) || pages < 1 || pages > 10000) {
        alert('Pages must be a number between 1 and 10000.');
        return false;
    }

    // Kontrola existence knihy a následné odeslání formuláře
    await checkAndSubmitForm(tab);
}

