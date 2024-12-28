async function validateAndUpdateForm(event) {
    console.log("Starting validateAndUpdateForm");
    event.preventDefault();  // Zabraňuje výchozímu odeslání formuláře

    const form = document.getElementById('update-form');
    console.log(form)
    console.log("Form element obtained:", form);


    const author = document.getElementById('update-author').value;
    const title = document.getElementById('update-title').value;
    const year = document.getElementById('update-year').value;
    const pages = document.getElementById('update-pages').value;

    console.log(`Author: ${author}, Title: ${title}, Year: ${year}, Pages: ${pages}`);

    // Zjištění výběru obrázku
    const selectedOption = document.querySelector('input[name="update-img-option"]:checked').value;

    if (!author) {
        alert('Autor musí být vyplněn');
        return false;
    }

    if (!title) {
        alert('Název knihy musí být vyplněn');
        return false;
    }

    // Convert year and pages to numbers before checking
    const yearValue = year == "" ? null : parseInt(year, 10);
    const pagesValue = pages === "" ? null : parseInt(pages, 10);
    
    // Vytvoření FormData objektu
    const formData = new FormData();

    // Check if year is valid
    if (year && yearValue > 0) {
        formData.append('year', yearValue);
    }

    // Check if pages are valid
    if (pages && pagesValue > 0) {
        formData.append('pages', pagesValue);
    }
    
    // Přidání základních polí do FormData
    formData.append('title', title);
    formData.append('author', author);

    
    formData.append('subtitle', document.getElementById('update-subtitle').value);
    formData.append('description', document.getElementById('update-description').value);
    formData.append('language', document.getElementById('update-language').value);
    formData.append('original-title', document.getElementById('original-title').value);
    formData.append('bookid', document.getElementById('update-bookid').value);
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

    // Přidání informací o obrázku na základě vybrané možnosti
    if (selectedOption === 'upload-img') {
        const fileInput = document.getElementById('update-img-file');
        const file = fileInput.files[0];

        if (file) {
            console.log(`Odesílám soubor: ${file.name}`);
            formData.append('img', file);  // Přidáme soubor do FormData
            formData.append('update-img-option', 'upload-img'); // Přidáme informaci o vybrané možnosti
        } else {
            alert('Musíte vybrat obrázek pro nahrání!');
            return false;
        }
    } else if (selectedOption === 'google-id') {
        const googleId = document.getElementById('update-googleid').value;
        if (googleId) {
            console.log(`Použit Google ID: ${googleId}`);
            formData.append('img', googleId);  // Přidáme Google ID do 'img' pole
            formData.append('update-img-option', 'google-id');
        } else {
            alert("Zadejte Google ID!");
            return false;
        }
    } else if (selectedOption === 'no-img') {
        console.log("Použit výchozí obrázek: noimg.png");
        formData.append('img', 'noimg.png');  // Přidáme 'noimg.png' do 'img' pole
        formData.append('update-img-option', 'no-img');
    }

    // Přidání žánrů
    const genreInputs = Array.from(document.querySelectorAll('#update-selected-genres li input[type="hidden"]'));
    genreInputs.forEach(input => {
        formData.append('genres', input.value);
    });

    // Přidání ISBN
    const isbnFieldGroups = document.querySelectorAll('.update-isbn-field-group');
    isbnFieldGroups.forEach((group, index) => {
        const isbnInput = group.querySelector(`input[id^="update-isbn-identifier-"]`);
        const isbnTypeSelect = group.querySelector(`select[id^="update-isbn-type-"]`);
        if (isbnInput && isbnTypeSelect) {
            const isbnValue = isbnInput.value;
            const isbnType = isbnTypeSelect.value;
            const publisherInput = document.getElementById('update-publisherid');
            let publisherId = publisherInput ? publisherInput.value : null;
            if (!publisherId) {
                publisherId = null; // Nastavit na null, pokud je prázdný nebo undefined
            }
            if (isbnValue) {
                const isbnData = JSON.stringify({ identifier: isbnValue, type: isbnType });
                formData.append('isbns', isbnData);
                formData.append('publisherid',publisherId)
            }
            
        }
    });

    // Přidání dalších autorů
    const authorInputs = Array.from(document.querySelectorAll('#update-authors input[name="authors"]'));
    authorInputs.forEach(input => {
        formData.append('authors', input.value);
    });

    // Odeslání dat na server
    try {
        const response = await fetch(`/scripts/update_book/${formData.get('bookid')}/`, {
            method: 'POST',
            body: formData,  // Odesíláme FormData
        });

        const data = await response.json();
        if (data.success) {
            alert('Kniha úspěšně upravena!');
            removeUrlParams();
            location.reload();
        } else if (data.error) {
            alert(data.error);
        } else {
            alert('Nepodařilo se upravit knihu.');
        }
    } catch (error) {
        console.error('Error updating book:', error);
        alert('Nastala chyba při úpravě knihy. Zkuste to prosím znovu');
    }
}