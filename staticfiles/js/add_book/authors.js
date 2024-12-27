let addedAuthors = new Set();  // Sada pro sledování přidaných autorů
let mainAuthorId = null;  // Zde budeme sledovat ID hlavního autora

document.addEventListener('DOMContentLoaded', function () {
    // Přidání hlavního autora do addedAuthors
    const mainAuthorIdElement = document.getElementById('update-authorid');
    if (mainAuthorIdElement && mainAuthorIdElement.value) {
        const mainAuthorId = Number(mainAuthorIdElement.value);
        addedAuthors.add(mainAuthorId);
        console.log(`Main author with ID ${mainAuthorId} added to addedAuthors.`);
    }
});


let searchTimeouts = {};  // Ukládá timeouty pro každé vyhledávací pole zvlášť

async function searchAuthor(tab, inputFieldId, isMainAuthor = true) {
    const inputField = document.getElementById(inputFieldId);
    if (!inputField) {
        console.error(`Invalid input field ID: ${inputFieldId} in tab: ${tab}`);
        return;
    }

    const query = inputField.value.trim();
    const resultListId = isMainAuthor ? `${tab}-author-results` : `${tab}-author-search-results`;

    if (query.length < 3) {
        const authorResults = document.getElementById(resultListId);
        if (authorResults) {
            authorResults.innerHTML = '';
        }
        return;
    }

    if (!/^[\p{L}0-9\s'-]+$/u.test(query)) {
        console.log('Query contains invalid characters.');
        return;
    }

    console.log(`Searching for authors with query: ${query}`);

    // Získání ID knihy
    const bookIdElement = document.getElementById(`${tab}-bookid`);
    const bookId = bookIdElement ? bookIdElement.value : null;

    // Získání ID již vybraných autorů
    let selectedAuthorIds = Array.from(addedAuthors);

    // Přidáme ID hlavního autora, pokud je definován
    const mainAuthorIdElement = document.getElementById(`${tab}-authorid`);
    if (mainAuthorIdElement && mainAuthorIdElement.value) {
        const mainAuthorId = Number(mainAuthorIdElement.value);
        if (!selectedAuthorIds.includes(mainAuthorId)) {
            selectedAuthorIds.push(mainAuthorId);
        }
    }

    const url = new URL('/scripts/search_authors/', window.location.origin);
    url.searchParams.append('search', query);
    if (bookId) {
        url.searchParams.append('book_id', bookId);
    }
    if (selectedAuthorIds.length > 0) {
        url.searchParams.append('exclude_authors', selectedAuthorIds.join(','));
    }

    console.log('Exclude authors parameter:', selectedAuthorIds.join(','));

    try {
        const response = await fetch(url.toString());

        const authorResults = document.getElementById(resultListId);
        authorResults.innerHTML = '';

        if (!response.ok) {
            console.error(`Error fetching authors: ${response.statusText}`);
            authorResults.innerHTML = '<li class="list-group-item">Error fetching authors.</li>';
            return;
        }

        const data = await response.json();

        if (Array.isArray(data.results) && data.results.length > 0) {
            data.results.forEach(author => {
                const birthYear = author.birthyear ? author.birthyear : '-';
                const li = document.createElement('li');
                li.textContent = `${author.full_name} (${birthYear})`;
                li.classList.add('list-group-item');
                li.onclick = () => {
                    if (isMainAuthor) {
                        addAuthor(tab, author.authorid, author.full_name);
                    } else {
                        addAdditionalAuthor(tab, author.authorid, author.full_name);
                    }
                    authorResults.innerHTML = '';
                };
                authorResults.appendChild(li);
            });
        } else {
            authorResults.innerHTML = '<li class="list-group-item">Nebyl nalezen žádný autor. Bude vytvořen nový</li>';
        }

    } catch (error) {
        console.error('Error searching authors:', error);
        const authorResults = document.getElementById(resultListId);
        authorResults.innerHTML = '<li class="list-group-item">Chyba při vyhledávání autora</li>';
    }
}

// Definice debounce funkce ( prodlevy pri hledani )
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}

// Vytvoření debounced verze funkce searchAuthor
const debouncedSearchAuthor = debounce(searchAuthor, 300); // Nastavte zpoždění podle potřeby

// Přidání event listeneru pro vstupní pole
document.querySelectorAll('input[id$="-author"], input[id$="-author-search"]').forEach(input => {
   input.addEventListener('input', function () {
        const tab = this.id.split('-')[0];  // Identifikace záložky (isbn, manual, update)
        const isMainAuthor = this.id.includes('-author-search') ? false : true;

        if (this.value.length > 2) {
            debouncedSearchAuthor(tab, this.id, isMainAuthor);  // Použití debounced funkce
        } else {
           const resultId = isMainAuthor ? `${tab}-author-results` : `${tab}-author-search-results`;
            const authorResults = document.getElementById(resultId);
            if (authorResults) {
                authorResults.innerHTML = '';  // Skrytí výsledků, pokud dotaz není validní
         }
        }
    });
});

// Funkce pro přidání hlavního autora
function addAuthor(tab, id, name) {
    const authorIdInputId = `${tab}-authorid`;
    const authorInputId = `${tab}-author`;
    const resultId = `${tab}-author-results`;  // Přidáno pro skrytí výsledků

    const authorIdInput = document.getElementById(authorIdInputId);
    const authorInput = document.getElementById(authorInputId);
    const authorResults = document.getElementById(resultId);  // Skrytí výsledků po výběru

    if (!authorInput) {
        console.error(`Element with id ${authorIdInputId} or ${authorInputId} not found.`);
        return;
    }

    // Nastavení ID autora, zobrazení jména a skrytí výsledků vyhledávání
    authorInput.value = name;
    if (authorResults) {
        authorResults.innerHTML = '';  // Vyčištění seznamu po výběru autora
    }

    // Vyčištění seznamu výsledků vyhledávání
    authorResults.innerHTML = '';
}

// Funkce pro přidání dalších autorů
function addAdditionalAuthor(tab, id, name) {
    const authorsList = document.getElementById(`${tab}-authors`);
    console.log('authorsList:', authorsList);

    if (!authorsList) {
        console.error(`Element with id ${tab}-authors not found.`);
        return;
    }

    const authorId = Number(id);

    // Zkontroluj, jestli už autor existuje v seznamu a pokud ano, přepsat
    const existingInput = authorsList.querySelector(`input[value="${authorId}"]`);
    if (existingInput) {
        console.log(`Author with ID ${authorId} is already added.`);
        return;
    }

    const li = document.createElement('li');
    li.classList.add('list-group-item');

    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = 'authors';
    hiddenInput.value = authorId;

    const authorNameSpan = document.createElement('span');
    authorNameSpan.textContent = name;

    const removeButton = document.createElement('button');
    removeButton.textContent = 'Remove';
    removeButton.classList.add('btn', 'btn-sm', 'btn-danger', 'ml-2');
    removeButton.onclick = () => {
        authorsList.removeChild(li);
        addedAuthors.delete(authorId);
        console.log(`Author with ID ${authorId} removed. Current Set:`, Array.from(addedAuthors));
    };

    li.appendChild(hiddenInput);
    li.appendChild(authorNameSpan);
    li.appendChild(removeButton);

    authorsList.appendChild(li);
    console.log('Added li to authorsList:', authorsList);
    console.log('Current authorsList HTML:', authorsList.innerHTML);

    addedAuthors.add(authorId);
    console.log(`Author with ID ${authorId} added. Current Set:`, Array.from(addedAuthors));
}

// Funkce pro skrytí výsledků, když kliknete mimo vyhledávací pole
document.addEventListener('click', function (event) {
    const authorInputs = document.querySelectorAll('input[id$="-author"], input[id$="-author-search"]');
    
    authorInputs.forEach(input => {
        const resultsList = document.getElementById(`${input.id.replace('-author', '')}-author-results`);
        const searchResultsList = document.getElementById(`${input.id.replace('-author-search', '')}-author-search-results`);
        
        if (resultsList && !input.contains(event.target) && !resultsList.contains(event.target)) {
            resultsList.innerHTML = '';  // Skryje výsledky vyhledávání při kliknutí mimo
        }

        if (searchResultsList && !input.contains(event.target) && !searchResultsList.contains(event.target)) {
            searchResultsList.innerHTML = '';  // Skryje výsledky vyhledávání dalších autorů při kliknutí mimo
        }
    });
});