// Listenery pro tlacitka 
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed in add_book.js');

    // Automaticky otevře první záložku
    const defaultTab = document.getElementById("defaultOpen");
    if (defaultTab) {
        defaultTab.click();
    } else {
        console.log('Default tab not found');
    }

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
    document.getElementById('isbn-publisher-search').addEventListener('input', () => searchPublishers('isbn'));

    document.getElementById('manual-genre-search').addEventListener('input', () => searchGenres('manual'));
    document.getElementById('manual-publisher-search').addEventListener('input', () => searchPublishers('manual'));

    // Přidání tříd podle vyplněnosti polí
    document.querySelectorAll('input').forEach(function(input) {
        input.addEventListener('input', function() {
            if (input.value === '') {
                input.classList.add('empty-input');
                input.classList.remove('filled-input');
            } else {
                input.classList.add('filled-input');
                input.classList.remove('empty-input');
            }
        });
    });
});

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

async function validateForm(tab) {
    const form = document.getElementById(`${tab}-form`);
    
    // Odstranění všech dříve přidaných skrytých polí
    const existingHiddenInputs = form.querySelectorAll('input[name="isbns"], input[name="genres"]');
    existingHiddenInputs.forEach(input => input.remove());

    const authorInputId = `${tab}-author`;
    const titleInputId = `${tab}-title`;
    const yearInputId = `${tab}-year`;
    const pagesInputId = `${tab}-pages`;
    const descriptionInputId = `${tab}-description`;

    const author = document.getElementById(authorInputId).value.trim();

    const title = document.getElementById(titleInputId).value.trim();
    const year = document.getElementById(yearInputId).value.trim();
    const pages = document.getElementById(pagesInputId).value.trim();
    let description = document.getElementById(descriptionInputId).value.trim();

    console.log(`Validating form for tab: ${tab}`);
    console.log(`Author: ${author}, Title: ${title}`);

    if (!author) {
        alert('Autor musí být vyplněn');
        return false;
    }

    if (!title) {
        alert('Název knihy musí být vyplněn');
        return false;
    }

    // Převedení na čísla před ověřením
    const yearValue = parseInt(year, 10);
    const pagesValue = parseInt(pages, 10);

    // Kontrola roku
    if (year && yearValue < 1) {
        alert('Rok musí být vyšší než 0');
        return false;
    }

    // Kontrola počtu stránek
    if (pages && pagesValue < 1) {
        alert('Počet stran musí být vyšší než 0');
        return false;
    }

    if (description.length > 1800) {
        description = description.slice(0, 1795) + '.....';
        document.getElementById(descriptionInputId).value = description;
    }

    // Získání ISBN polí podle režimu
    if (tab === 'manual') {
        const isbnFieldsContainer = document.getElementById('manual-isbn-fields-container');
        isbnFieldGroups = isbnFieldsContainer.querySelectorAll('.manual-isbn-field-group');
    } else if (tab === 'isbn') {
        const isbnFieldsContainer = document.getElementById('isbn-isbn-fields-container');
        isbnFieldGroups = isbnFieldsContainer.querySelectorAll('.isbn-isbn-field-group');
    }

    // Zjištění, jaká volba obrázku byla vybrána
    const selectedOption = document.querySelector(`input[name="${tab}-img-option"]:checked`).value;
    if (selectedOption === 'upload-img') {
        const fileInput = document.getElementById(`${tab}-img-file`);
        if (!fileInput.files.length) {
            alert('Musíte vybrat obrázek pro nahrání!');
            return false;
        }
    }

    console.log(`ISBN Field Groups found: ${isbnFieldGroups.length}`);
    const addedIsbns = new Set(); // Set pro uložení přidaných ISBN, aby se zabránilo duplikátům

    if (isbnFieldGroups && isbnFieldGroups.length > 0) {
        for (let index = 0; index < isbnFieldGroups.length; index++) {
            const group = isbnFieldGroups[index];
            const isbnInputElement = group.querySelector(`input[id^="${tab}-isbn-identifier-"]`);

            if (isbnInputElement) {  // Zkontrolujeme, zda existuje
                const isbnValue = isbnInputElement.value;
                console.log(`Processing ISBN: ${isbnValue}`);

                if (isbnValue) {
                    const isbnExists = await checkIsbnExists(isbnValue);
                    console.log(`Checking ISBN: ${isbnValue}, Exists: ${isbnExists}`);

                    if (isbnExists) {
                        alert(`ISBN ${isbnValue} již existuje v databázi.`);
                        return false;  // Zastaví odeslání formuláře
                    } else {
                        const isbnType = group.querySelector(`select[id^="${tab}-isbn-type-"]`).value;
                        console.log(`Adding ISBN: ${isbnValue}, Type: ${isbnType}`);
                        
                        const isbnInput = document.createElement('input');
                        isbnInput.type = 'hidden';
                        isbnInput.name = 'isbns';
                        isbnInput.value = JSON.stringify({ identifier: isbnValue, type: isbnType });
                        form.appendChild(isbnInput);
                        addedIsbns.add(isbnValue); // Přidání ISBN do setu, aby se předešlo duplikaci
                        
                    }
                }
            } else {
                console.log(`No ISBN input found for ${tab}-isbn-identifier-${index}`);
            }
        }
    } else {
        console.log(`No ISBN Field Groups found for ${tab}`);
    }

    // Přidání vybraných žánrů do formuláře
    const genreInputs = document.querySelectorAll(`#${tab}-selected-genres li`);
    genreInputs.forEach(input => {
        const genreId = input.querySelector('input[type="hidden"]').value;
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'genres';
        hiddenInput.value = genreId;
        form.appendChild(hiddenInput);
        console.log(`Added hidden genre input: ${genreId}`);
    });

    // Odeslání formuláře, pokud vše proběhlo v pořádku
    await checkAndSubmitForm(tab, false);  // Kontrola, zda kniha již neexistuje při přidání
}

async function checkAndSubmitForm(tab, isUpdate = false) {
    const form = document.getElementById(`${tab}-form`);
    
    // Vytvoříme prázdný FormData objekt
    const formData = new FormData();
    
    // Ručně přidáme všechny ostatní hodnoty z formuláře kromě 'img' a 'img-option'
    const elements = form.elements;
    for (let i = 0; i < elements.length; i++) {
        const element = elements[i];
        if (
            element.name &&
            element.name !== 'img' &&+
            element.name !== `${tab}-img-option` &&  // Vynecháme 'img-option'
            element.type !== 'file'
        ) {
            // Pro radio tlačítka přidáme pouze vybrané
            if (element.type === 'radio') {
                if (element.checked) {
                    formData.append(element.name, element.value);
                }
            } else {
                formData.append(element.name, element.value);
            }
        }
    }

    // Získáme hodnotu vybrané možnosti pro obrázek
    const selectedOption = document.querySelector(`input[name="${tab}-img-option"]:checked`).value;

    // Přidáme vybranou možnost 'img-option' do FormData
    formData.append(`${tab}-img-option`, selectedOption);

    // Logika pro zpracování obrázků
    if (selectedOption === 'upload-img') {
        const fileInput = document.getElementById(`${tab}-img-file`);
        const file = fileInput.files[0];

        if (file) {
            console.log(`Odesílám soubor: ${file.name}`);
            formData.append('img', file);  // Přidáme soubor do FormData
        } else {
            alert("Nevybrali jste žádný soubor!");
            return false;
        }
    } else if (selectedOption === 'no-img') {
        console.log("Použit výchozí obrázek: noimg.png");
        formData.append('img', 'noimg.png');  // Přidáme výchozí obrázek
    } else if (selectedOption === 'google-id') {
        const googleId = document.getElementById(`${tab}-googleid`).value;
        if (googleId) {
            console.log(`Použit Google ID: ${googleId}`);
            formData.append('img', googleId);  // Přidáme Google ID
        } else {
            alert("Zadejte Google ID!");
            return false;
        }
    }

    // Odeslání formuláře
    const submitUrl = form.action;
    try {
        const submitResponse = await fetch(submitUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),  // Přidání CSRF tokenu, pokud není automaticky zahrnut
            },  // Odeslání FormData včetně souborů
        });

        if (submitResponse.ok) {
            console.log('Formulář úspěšně odeslán');
            location.reload();  // Obnoví stránku po úspěšném odeslání
        } else {
            const errorText = await submitResponse.text();
            console.error('Chyba při odeslání formuláře', {
                status: submitResponse.status,
                statusText: submitResponse.statusText,
                responseText: errorText
            });
            alert(`Chyba při odeslání formuláře: ${submitResponse.statusText} (Status code: ${submitResponse.status}). Odpověď serveru: ${errorText}`);
        }
    } catch (error) {
        console.error('Chyba při odeslání formuláře:', error);
        alert('Chyba při odeslání formuláře.');
    }
}

// Vymazani formulare
function clearForm(tab) {
    const forms = ['isbn', 'manual'];

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

// Zmena tabu 
function openTab(evt, tabName) {
    var i, tabcontent, tablinks;

    // Skrytí všech tabů
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Odstranění "active" třídy ze všech odkazů
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Zobrazení aktuálního tabu
    document.getElementById(tabName).style.display = "block";
    if (evt) {
        evt.currentTarget.className += " active";

        // Resetování polí pouze při manuálním kliknutí
        const forms = ['isbn', 'manual', 'update'];
        forms.forEach((formTab) => {
            const authorIdInputId = `${formTab}-authorid`;
            const authorIdDisplayId = `${formTab}-authorid-display`;
            const statusElement = document.getElementById(`${formTab}-author-status`);

            if (document.getElementById(authorIdInputId)) {
                document.getElementById(authorIdInputId).value = ''; // Resetovat hodnotu ID autora
            }
            if (document.getElementById(authorIdDisplayId)) {
                document.getElementById(authorIdDisplayId).value = ''; // Resetovat zobrazení ID autora
            }
            if (statusElement) {
                statusElement.style.display = 'none'; // Skrytí statusu
            }
        });
    }

    // Skrytí detailů při přepnutí záložky
    if (tabName === 'isbn-tab') {
        document.getElementById('isbn-details').style.display = 'none';
    } else if (tabName === 'update-tab') {
        document.getElementById('update-details').style.display = 'none';
    }
}

//Vymazani formulare po zmacknuti tlacitka
document.querySelectorAll('.tablinks').forEach(button => {
    button.addEventListener('click', function(event) {
        const currentTab = event.target.id.replace('-tab-btn', ''); // Extrahuje název aktuální záložky
        clearForm(currentTab); // Vymaže všechny formuláře a množiny při přepnutí záložky
    });
});