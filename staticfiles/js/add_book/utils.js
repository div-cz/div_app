// Rozdeleni jmena na dve / tri casti
function splitName(fullName) {
    const nameParts = fullName.trim().split(' ');
    const firstname = nameParts[0] || '';
    const lastname = nameParts.length > 1 ? nameParts[nameParts.length - 1] : '';
    const middlename = nameParts.length > 2 ? nameParts.slice(1, -1).join(' ') : '';
    return [firstname, middlename, lastname];
}

// Ziskani cookie pro csrf token
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

//pridani do seznamu
function addItemToList(item, listElement, inputName, set) {
    if (!listElement) {
        console.error(`Element with id ${listElement} does not exist.`);
        return;
    }

    const itemId = parseInt(item.id, 10); // Zajistíme, že ID je správného typu

    if (!set.has(itemId)) {
        set.add(itemId);  // Přidáme ID vydavatele do Setu
        console.log(`Added item with ID ${itemId} to Set`);

        const li = document.createElement('li');
        li.classList.add('list-group-item');
        li.textContent = item.name;
        li.setAttribute('data-id', itemId);  // Nastavení atributu data-id

        const removeButton = document.createElement('button');
        removeButton.textContent = 'Remove';
        removeButton.onclick = () => {
            listElement.removeChild(li);
            set.delete(itemId);  // Odstranění z množiny při smazání
            console.log(`Removed item with ID ${itemId} from Set`);
            console.log('Current Set content after manual removal:', Array.from(set));

            // Explicitně přistupujeme k `update-publisherid`
            const publisherInput = document.getElementById('update-publisherid');
            if (publisherInput) {
                publisherInput.value = '';  // Nastavíme na prázdno
                console.log('Publisher ID cleared in hidden input');
                console.log('Aktualizovaná hodnota publisherid:', publisherInput.value);
            } else {
                console.error("Skryté pole 'update-publisherid' nebylo nalezeno.");
            }
        };
        
        li.appendChild(removeButton);
        listElement.appendChild(li);

        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = inputName;
        hiddenInput.value = itemId;
        li.appendChild(hiddenInput); 
        
        console.log('Current Set content after addition:', Array.from(set));
    } else {
        console.log(`Item with ID ${itemId} already added.`);
    }
}

// Funkce na pridani ISBN po zmacknuti tlacitka
document.addEventListener('DOMContentLoaded', function () {
    const addIsbnButtons = document.querySelectorAll('.add-isbn-btn');

    addIsbnButtons.forEach(button => {
        const tab = button.getAttribute('data-tab');
        let isbnCount = 0;

        const isbnFieldsContainer = document.getElementById(`${tab}-isbn-fields-container`);
        const publisherSection = document.getElementById('update-publisher-section'); // Sekce vydavatele

        button.addEventListener('click', function () {
            if (isbnCount < 3) {
                const newIsbnFieldGroup = document.createElement('div');
                newIsbnFieldGroup.className = `form-group ${tab}-isbn-field-group`;

                newIsbnFieldGroup.innerHTML = `
                    <label for="${tab}-isbn-identifier-${isbnCount}">ISBN:</label>
                    <input type="text" id="${tab}-isbn-identifier-${isbnCount}" name="${tab}-isbn-identifier-${isbnCount}">
                    
                    <label for="${tab}-isbn-type-${isbnCount}">Type:</label>
                    <select id="${tab}-isbn-type-${isbnCount}" name="${tab}-isbn-type-${isbnCount}">
                        <option value="ISBN_10">ISBN 10</option>
                        <option value="ISBN_13">ISBN 13</option>
                        <option value="OTHER">Other</option>
                    </select>
                `;

                isbnFieldsContainer.appendChild(newIsbnFieldGroup);
                isbnCount++;

                // Zajistíme, že sekce s vydavatelem se zobrazí
                if (publisherSection) {
                    // Zobrazíme celý div
                    publisherSection.style.display = 'block';

                    // Zkontrolujeme a explicitně zobrazíme i všechny jeho děti
                    const children = publisherSection.querySelectorAll('input, ul, label');
                    children.forEach(child => {
                        child.style.display = ''; // Reset stylu
                    });
                }
            } else {
                alert("Můžete přidat maximálně 3 ISBN");
            }
        });
    });
});

// Function to derive authorId from author name if data-author-id is missing
async function deriveAuthorIdFromName(authorName) {
    try {
        // Placeholder: implement an API call or lookup here to get the authorId by authorName
        const response = await fetch(`/scripts/search_authors/?authorName=${encodeURIComponent(authorName)}`);
        if (response.ok) {
            const data = await response.json();
            return data.authorId || null;
        } else {
            console.warn('Failed to derive author ID from author name.');
            return null;
        }
    } catch (error) {
        console.error('Error deriving author ID from author name:', error);
        return null;
    }
}

function removeUrlParams() {
    // Získáme aktuální URL bez parametrů
    const cleanUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
    // Aktualizujeme URL bez znovunačtení stránky
    window.history.pushState({ path: cleanUrl }, "", cleanUrl);
}

// Asynchronní funkce pro kontrolu ISBN
async function checkIsbnExists(isbn) {
    try {
        const response = await fetch(`/scripts/check_isbn_exists/?isbn=${encodeURIComponent(isbn)}`);
        const data = await response.json();
        return data.exists;
    } catch (error) {
        console.error('Error checking ISBN existence:', error);
        return false;
    }
}

// Asynchronní funkce pro kontrolu ISBN
async function checkBookExists(title,authorid,exclude_authors) {
    try {
        const response = await fetch(`/scripts/check_book_exists/?title=${encodeURIComponent(title)}&authorid=${encodeURIComponent(authorid)}&exclude_book_id=${encodeURIComponent(exclude_authors)}`);
        const data = await response.json();
        return data.exists;
    } catch (error) {
        console.error('Error checking Book existence:', error);
        return false;
    }
}
