
let addedGenres = new Set();


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
    // Kontrola, zda bylo přidáno maximálně 5 žánrů
    if (addedGenres.size >= 5) {
        alert('You can only add up to 5 genres.');
        return;
    }
    const genre = { id: id, name: name };
    addItemToList(genre, selectedGenres, 'genres[]', addedGenres);
    document.getElementById(`${tab}-genre-search`).value = '';  // Vyčištění pole pro vyhledávání žánrů

}
