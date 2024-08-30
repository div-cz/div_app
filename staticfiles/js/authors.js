async function createAuthor(tab) {
    const authorInputId = tab === 'isbn' ? 'isbn-author' : 'manual-author';
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
            const authoridInput = tab === 'isbn' ? 'isbn-authorid' : 'manual-authorid';
            const authoridDisplay = tab === 'isbn' ? 'isbn-authorid-display' : 'manual-authorid-display';
            document.getElementById(authoridInput).value = data.authorid;
            document.getElementById(authoridDisplay).value = data.authorid;
            alert('Author created and ID added.');
        } else {
            alert(`Failed to create author: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error}`);
    }
}

async function verifyAuthor(tab) {
    const authorInputId = tab === 'isbn' ? 'isbn-author' : 'manual-author';
    const author = document.getElementById(authorInputId).value;
    if (!author) {
        alert('Please enter an author name.');
        return;
    }

    console.log('Fetching author data...');

    try {
        const response = await fetch(`/scripts/verify-author/?author=${encodeURIComponent(author)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            const authoridInput = tab === 'isbn' ? 'isbn-authorid' : 'manual-authorid';
            const authoridDisplay = tab === 'isbn' ? 'isbn-authorid-display' : 'manual-authorid-display';
            document.getElementById(authoridInput).value = data.authorid;
            document.getElementById(authoridDisplay).value = data.authorid;
            alert('Author verified and ID added.');
        } else {
            alert(data.error || 'Author not found in database.');
        }

    } catch (error) {
        console.error('Error verifying author:', error);
        alert(`Error verifying author: ${error}`);
    }
}
