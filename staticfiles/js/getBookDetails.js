document.getElementById('fetch-book-details-btn').addEventListener('click', async function() {
    const bookId = document.getElementById('book-id').value;

    if (bookId) {
        try {
            console.log(bookId);
            const response = await fetch(`/scripts/get_book_details/${bookId}/`);
            const data = await response.json();

            if (data.error) {
                alert(data.error);
            } else {
                // Vyplnění formuláře získanými daty
                document.getElementById('title').value = data.title || '';
                document.getElementById('author').value = data.author || '';
                document.getElementById('year').value = data.year || '';
                document.getElementById('pages').value = data.pages || '';
                document.getElementById('subtitle').value = data.subtitle || '';
                document.getElementById('description').value = data.description || '';
                document.getElementById('language').value = data.language || '';
                document.getElementById('img').value = data.img || '';
                document.getElementById('googleid').value = data.googleid || '';

                // Genres
                const genreList = document.getElementById('selected-genres');
                genreList.innerHTML = '';
                data.genres.forEach(genre => {
                    const li = document.createElement('li');
                    li.classList.add('list-group-item');
                    li.textContent = genre.name;
                    genreList.appendChild(li);

                    const hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.name = 'genres';
                    hiddenInput.value = genre.id;
                    genreList.appendChild(hiddenInput);
                });

                // Publisher
                if (data.publisher) {
                    const publisherList = document.getElementById('selected-publisher');
                    publisherList.innerHTML = '';
                    const li = document.createElement('li');
                    li.classList.add('list-group-item');
                    li.textContent = data.publisher.name;
                    publisherList.appendChild(li);

                    const hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.name = 'publisherid';
                    hiddenInput.value = data.publisher.id;
                    publisherList.appendChild(hiddenInput);
                }
            }
        } catch (error) {
            console.error('Error fetching book details:', error);
            alert('Failed to fetch book details.');
        }
    } else {
        alert('Please enter a Book ID.');
    }
});