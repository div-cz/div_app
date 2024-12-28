
let addedPublisher = new Set();

async function searchPublishers(tab) {
    const query = document.getElementById(`${tab}-publisher-search`).value;
    if (query.length > 2) {
        fetch(`/api/book_publisher/?search=${query}`)
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

function addPublisher(tab, id = null, name) {
    const selectedPublisher = document.getElementById(`${tab}-selected-publisher`);

    // Ověření, zda element existuje
    if (!selectedPublisher) {
        console.error(`Element with id ${tab}-selected-publisher not found.`);
        return;
    }

    // Odstranění předchozího vydavatele ze seznamu a množiny
    const existingPublisher = selectedPublisher.querySelector('li[data-id]');
    if (existingPublisher) {
        const existingPublisherId = existingPublisher.getAttribute('data-id');
        if (existingPublisherId) {
            const publisherId = parseInt(existingPublisherId, 10); // Zajistíme, že ID je správného typu
            console.log(`Removing publisher with ID ${publisherId} from Set`);
            addedPublisher.delete(publisherId);  // Odstraníme ID vydavatele ze Setu
            console.log(`Publisher with ID ${publisherId} removed from Set`);
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

    // Vyčištění pole pro vyhledávání vydavatelů
    const searchField = document.getElementById(`${tab}-publisher-search`);
    if (searchField) {
        searchField.value = '';  
    }
}


