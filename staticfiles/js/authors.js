
let addedAuthors = new Set();

async function createAuthor(tab) {
    const authorInputId = tab === 'isbn' ? 'isbn-author' : (tab === 'manual' ? 'manual-author' : 'update-author');

    const author = document.getElementById(authorInputId).value;
    const nameParts = author.trim().split(' ');

    if (nameParts.length < 2) {
        alert('Author name must contain at least two words.');
        return;
    }

    const [firstname, middlename, lastname] = splitName(author);
    try {
        const response = await fetch('/scripts/create-author/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ firstname, middlename, lastname })
        });
        const data = await response.json();
        if (data.success) {

            const authoridInput = tab === 'isbn' ? 'isbn-authorid' : (tab === 'manual' ? 'manual-authorid' : 'update-authorid');
            const authoridDisplay = tab === 'isbn' ? 'isbn-authorid-display' : (tab === 'manual' ? 'manual-authorid-display' : 'update-authorid-display');
            document.getElementById(authoridInput).value = data.authorid;
            document.getElementById(authoridDisplay).value = data.authorid;
            displayAuthorStatus(tab, 'created');

            alert('Author created and ID added.');
        } else {
            alert(`Failed to create author: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error}`);
    }
}

async function verifyAuthor(tab) {

    const authorInputId = tab === 'isbn' ? 'isbn-author' : (tab === 'manual' ? 'manual-author' : 'update-author');
    const author = document.getElementById(authorInputId).value;
    const createButtonId = tab === 'isbn' ? 'isbn-create-author-btn' : (tab === 'manual' ? 'manual-create-author-btn' : 'update-create-author-btn');
    const createButton = document.getElementById(createButtonId);
    const statusElement = document.getElementById(`${tab}-author-status`);


    if (!author) {
        alert('Please enter an author name.');
        return;
    }


    console.log('Fetching author data for', tab, 'tab...');


    try {
        const response = await fetch(`/scripts/verify-author/?author=${encodeURIComponent(author)}`);
        
        if (!response.ok) {

            if (response.status === 404) {
                alert('Author not found in the database. You can create a new author.');
                createButton.style.display = 'inline-block';
                statusElement.style.display = 'none'; // Hide status when author is not verified
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        } else {
            const data = await response.json();

            if (data.success) {
                const authoridInput = tab === 'isbn' ? 'isbn-authorid' : (tab === 'manual' ? 'manual-authorid' : 'update-authorid');
                const authoridDisplay = tab === 'isbn' ? 'isbn-authorid-display' : (tab === 'manual' ? 'manual-authorid-display' : 'update-authorid-display');
                document.getElementById(authoridInput).value = data.authorid;
                document.getElementById(authoridDisplay).value = data.authorid;
                displayAuthorStatus(tab, 'verified');
                createButton.style.display = 'none'; // Hide "Create Author" button after verification
                alert('Author verified and ID added.');
            } else {
                alert(data.error || 'Author not found in database.');
                createButton.style.display = 'inline-block'; // Show "Create Author" button if not verified
                statusElement.style.display = 'none'; // Hide status when author is not verified
            }
        }
    } catch (error) {
        console.error('Error verifying author:', error);
        alert('An error occurred while verifying the author. Please try again.');
    }
}


function showCreateAuthorButton(tab) {
    const createButton = document.getElementById(`${tab}-create-author-btn`);
    if (createButton) {
        createButton.style.display = 'block';
    }
}

async function searchAuthor(tab) {
    const query = document.getElementById(`${tab}-author-search`).value;
    if (query.length > 2) {
        const response = await fetch(`/api/book_authors/?search=${query}`);
        const data = await response.json();
        const authorResults = document.getElementById(`${tab}-author-results`);
        authorResults.innerHTML = '';

        // Filtrování výsledků, aby obsahovaly pouze autory, kteří ještě nebyli přidáni
        const filteredAuthors = data.results.filter(author => !addedAuthors.has(author.authorid));

        filteredAuthors.forEach(author => {
            const li = document.createElement('li');
            li.classList.add('list-group-item');
            li.textContent = author.full_name;
            li.onclick = () => {
                addAuthor(tab, author.authorid, author.full_name);
                authorResults.innerHTML = '';  // Clear the search results
            };
            authorResults.appendChild(li);
        });
    }
}

function addAuthor(tab, id, name) {
    const authorsResults = document.getElementById(`${tab}-authors`);
    if (addedAuthors.size >= 10) {
        alert('You can only add up to 10 autors.');
        return;
    }
    const author = { id: id, name: name };
    addItemToList(author, authorsResults, 'authors[]', addedAuthors);
    document.getElementById(`${tab}-author-search`).value = '';
}

function displayAuthorStatus(tab, status) {
    const statusElement = document.getElementById(`${tab}-author-status`);
    statusElement.textContent = status === 'verified' ? 'Verified' : 'Created';
    statusElement.className = `author-status ${status}`;
    statusElement.style.display = 'inline-block';
}

document.querySelectorAll('input[id$="-author"]').forEach(input => {
    input.addEventListener('input', function() {
        const tab = input.id.split('-')[0];
        const createButtonId = `${tab}-create-author-btn`;
        const createButton = document.getElementById(createButtonId);
        const statusElement = document.getElementById(`${tab}-author-status`);

        // Resetovat pole pro ID autora
        const authorIdInputId = `${tab}-authorid`;
        const authorIdDisplayId = `${tab}-authorid-display`;
        document.getElementById(authorIdInputId).value = '';
        document.getElementById(authorIdDisplayId).value = '';

        if (input.value === '') {
            createButton.style.display = 'none';
        } else {
            createButton.style.display = 'none'; // Hide the create button when author input is changed
            statusElement.style.display = 'none'; // Hide the status (verified/created)
        }
    });
});

