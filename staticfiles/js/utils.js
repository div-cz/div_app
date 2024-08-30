function splitName(fullName) {
    const nameParts = fullName.trim().split(' ');
    const firstname = nameParts[0] || '';
    const lastname = nameParts.length > 1 ? nameParts[nameParts.length - 1] : '';
    const middlename = nameParts.length > 2 ? nameParts.slice(1, -1).join(' ') : '';
    return [firstname, middlename, lastname];
}


function handleFormSubmit(event) {
    event.preventDefault();

    // Kontrola povinných polí
    const title = document.getElementById('title').value;
    const author = document.getElementById('author').value;
    const year = document.getElementById('year').value;
    const authorid = document.getElementById('authorid').value;
    const description = document.getElementById('description').value;

    if (!title || !author || !year || !authorid) {
        alert('Title, Author, Year, and Author ID are required.');
        return;
    }

    // Oříznutí popisu, pokud je delší než 1800 znaků
    if (description.length > 1800) {
        document.getElementById('description').value = description.slice(0, 1795) + '.....';
    }

    const isbn1 = document.getElementById('isbn1').value;
    const isbn2 = document.getElementById('isbn2').value;

    const isbn1Input = document.createElement('input');
    isbn1Input.type = 'hidden';
    isbn1Input.name = 'isbns';
    isbn1Input.value = JSON.stringify({ identifier: isbn1, type: 'ISBN_13' });

    const isbn2Input = document.createElement('input');
    isbn2Input.type = 'hidden';
    isbn2Input.name = 'isbns';
    isbn2Input.value = JSON.stringify({ identifier: isbn2, type: 'ISBN_10' });

    this.appendChild(isbn1Input);
    this.appendChild(isbn2Input);

    this.submit();
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
