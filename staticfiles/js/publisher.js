async function searchPublishers(tab) {
    const query = document.getElementById(`${tab}-publisher-search`).value;
    if (query.length > 2) {
        const response = await fetch(`/api/book_publisher/?search=${query}`);
        const data = await response.json();
        const publisherResults = document.getElementById(`${tab}-publisher-results`);
        publisherResults.innerHTML = '';
        data.results.forEach(publisher => {
            const li = document.createElement('li');
            li.classList.add('list-group-item');
            li.textContent = publisher.publishername;
            li.onclick = () => {
                addPublisher(tab, publisher.publisherid, publisher.publishername);
                publisherResults.innerHTML = '';  // Zavření seznamu
            };
            publisherResults.appendChild(li);
        });
    }
}

function addPublisher(tab, id, name) {
    const selectedPublisher = document.getElementById(`${tab}-selected-publisher`);
    selectedPublisher.innerHTML = '';
    const li = document.createElement('li');
    li.classList.add('list-group-item');
    li.textContent = name;
    const removeButton = document.createElement('button');
    removeButton.textContent = 'Remove';
    removeButton.onclick = () => {
        selectedPublisher.innerHTML = '';
        document.getElementById(`${tab}-publisherid`).value = '';
    };
    li.appendChild(removeButton);
    selectedPublisher.appendChild(li);

    document.getElementById(`${tab}-publisherid`).value = id;
    document.getElementById(`${tab}-publisher-search`).value = '';
}
