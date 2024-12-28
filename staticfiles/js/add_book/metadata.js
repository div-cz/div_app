// Vydavatele 

let addedPublisher = new Set();
// Hledani vydavatele
async function searchPublishers(tab) {
    const query = document.getElementById(`${tab}-publisher-search`).value;
    if (query.length > 2) {
        fetch(`/scripts/search_publisher/?search=${query}`)
            .then(response => response.json())
            .then(data => {
                const publisherResults = document.getElementById(`${tab}-publisher-results`);
                publisherResults.innerHTML = '';
                data.results.forEach(publisher => {
                    const li = document.createElement('li');
                    li.classList.add('list-group-item');
                    li.textContent = publisher.publishername;
                    li.onclick = () => {
                        addPublisher(tab, publisher.publisherid, publisher.publishername);  // Předání obou argumentů
                        publisherResults.innerHTML = '';  // Zavření seznamu
                    };
                    publisherResults.appendChild(li);
                });
            });
    }
}
//Pridani vydavatele
function addPublisher(tab, id = null, name) {
    const selectedPublisher = document.getElementById(`${tab}-selected-publisher`);
    const publisherInput = document.getElementById(`${tab}-publisherid`); // Hlavní skryté pole pro publisherid

    // Ověření, zda `selectedPublisher` a `publisherInput` existují
    if (!selectedPublisher) {
        console.error(`Element ${tab}-selected-publisher not found.`);
        return;
    }

    addedPublisher.clear()

    // Odstranění předchozího vydavatele ze seznamu a množiny
    const existingPublisher = selectedPublisher.querySelector('li[data-id]');
    if (existingPublisher) {
        const existingPublisherId = existingPublisher.getAttribute('data-id');
        if (existingPublisherId) {
            console.log(`Removing publisher with ID ${existingPublisherId} from Set`);
            addedPublisher.delete(existingPublisherId);  // Odstraníme ID vydavatele ze Setu
            console.log(`Publisher with ID ${existingPublisherId} removed from Set`);
        }
        selectedPublisher.innerHTML = '';  // Vymažeme obsah seznamu

        // Ladicí výpis pro kontrolu obsahu Setu po odstranění
        console.log('Current Set content after removal:', Array.from(addedPublisher));
    }

    // Přidání nového vydavatele
    const publisher = { id: id || name, name: name };

    // Přidání vydavatele do seznamu a množiny
    console.log(`Adding new publisher with ID ${publisher.id} to the list`);
    addItemToList(publisher, selectedPublisher, 'publisherid', addedPublisher);
    
    publisherInput.value = publisher.id;
    console.log(`Hodnota publisherid nastavena na: ${publisherInput.value}`);  // Ladicí výpis pro ověření

    // Vyčištění pole pro vyhledávání vydavatelů
    const searchField = document.getElementById(`${tab}-publisher-search`);
    if (searchField) {
        searchField.value = '';  
    }
}


/// Zanry
let addedGenres = new Set();
// Hledani zanru
async function searchGenres(tab) {

    const query = document.getElementById(`${tab}-genre-search`).value;
    if (query.length > 2) {
        const response = await fetch(`/scripts/search_genres/?search=${query}`);
        const data = await response.json();
        const genreResults = document.getElementById(`${tab}-genre-results`);
        genreResults.innerHTML = '';
        data.results.forEach(genre => {
            const li = document.createElement('li');
            li.classList.add('list-group-item');
            li.textContent = genre.genrename;
            li.onclick = () => {
                addGenre(tab, genre.genreid, genre.genrename);
                genreResults.innerHTML = '';  // Zavření seznamu
            };
            genreResults.appendChild(li);
        });
    }
}
// Pridani zanru
function addGenre(tab, id, name) {
    const selectedGenres = document.getElementById(`${tab}-selected-genres`);
    
    // Kontrola, zda bylo přidáno maximálně 5 žánrů
    if (addedGenres.size >= 5) {
        alert('Můžeš přidat maximálně 5 žánrů');
        return;
    }

    const genre = { id: id, name: name };

    // Přidání žánru do seznamu a množiny
    addItemToList(genre, selectedGenres, 'genres[]', addedGenres);

    // Vyčištění pole pro vyhledávání žánrů
    document.getElementById(`${tab}-genre-search`).value = '';

    // Výpis obsahu množiny addedGenres
    console.log('Current genres in Set:', Array.from(addedGenres));
}
