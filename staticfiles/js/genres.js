async function searchGenres(tab) {

    const query = document.getElementById(`${tab}-genre-search`).value;
    if (query.length > 2) {
        const response = await fetch(`/api/genres/?search=${query}`);
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

function addGenre(tab, id, name) {
    const selectedGenres = document.getElementById(`${tab}-selected-genres`);
    const li = document.createElement('li');
    li.classList.add('list-group-item');
    li.textContent = name;
    const removeButton = document.createElement('button');
    removeButton.textContent = 'Remove';
    removeButton.onclick = () => selectedGenres.removeChild(li);
    li.appendChild(removeButton);
    selectedGenres.appendChild(li);

    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = 'genres';
    hiddenInput.value = id;
    li.appendChild(hiddenInput);
    document.getElementById(`${tab}-genre-search`).value = '';
}
