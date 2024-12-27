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

function addItemToList(item, listElement, inputName, set) {
    // Ověření, zda `listElement` existuje
    if (!listElement) {
        console.error(`Element with id ${listElement} does not exist.`);
        return;
    }

    const itemId = parseInt(item.id, 10); // Zajistíme, že ID je správného typu

    // Zkontrolujeme, jestli ID již není v Setu
    if (!set.has(itemId)) {
        set.add(itemId);  // Přidáme ID vydavatele do Setu
        console.log(`Added publisher with ID ${itemId} to Set`);

        const li = document.createElement('li');
        li.classList.add('list-group-item');
        li.textContent = item.name;
        li.setAttribute('data-id', itemId);  // Nastavení atributu data-id

        const removeButton = document.createElement('button');
        removeButton.textContent = 'Remove';
        removeButton.onclick = () => {
            listElement.removeChild(li);
            set.delete(itemId);  // Odstranění z množiny při smazání
            console.log(`Removed publisher with ID ${itemId} from Set`);
            console.log('Current Set content after manual removal:', Array.from(set));
        };
        li.appendChild(removeButton);
        listElement.appendChild(li);

        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = inputName;
        hiddenInput.value = itemId;
        listElement.appendChild(hiddenInput);
        
        // Ladicí výpis pro kontrolu obsahu Setu po přidání
        console.log('Current Set content after addition:', Array.from(set));
    } else {
        console.log(`Item with ID ${itemId} already added.`);
    }
}



function clearForm(tab) {
    const forms = ['isbn', 'manual', 'update'];

    forms.forEach((formTab) => {
        const form = document.getElementById(`${formTab}-form`);
        if (form) {
            form.reset();
        }

        const genresElement = document.getElementById(`${formTab}-selected-genres`);
        if (genresElement) {
            genresElement.innerHTML = '';
        }

        const publisherElement = document.getElementById(`${formTab}-selected-publisher`);
        if (publisherElement) {
            publisherElement.innerHTML = '';
        }

        const detailsElement = document.getElementById(`${formTab}-details`);
        if (detailsElement) {
            detailsElement.style.display = 'none'; // Skrytí detailů
        }
    });

    addedGenres.clear();
    addedPublisher.clear();
}

document.querySelectorAll('.tablinks').forEach(button => {
    button.addEventListener('click', function(event) {
        const currentTab = event.target.id.replace('-tab-btn', ''); // Extrahuje název aktuální záložky
        clearForm(currentTab); // Vymaže všechny formuláře a množiny při přepnutí záložky
    });
});