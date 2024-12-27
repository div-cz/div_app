document.getElementById('fetch-book-details-btn').addEventListener('click', async function() {
    const bookId = document.getElementById('book-id').value;

    if (bookId) {
        try {
            const response = await fetch(`/scripts/get-book-details/${bookId}/`);
            const data = await response.json();

            if (data.error) {
                alert(data.error);
            } else {
                // Zobrazí sekci update-details
                document.getElementById('update-details').style.display = 'block';

                // Vyplnění formuláře získanými daty
                document.getElementById('update-title').value = data.title || '';
                document.getElementById('update-author').value = data.author || '';
                document.getElementById('update-year').value = data.year || '';
                document.getElementById('update-pages').value = data.pages || '';
                document.getElementById('update-subtitle').value = data.subtitle || '';
                document.getElementById('update-description').value = data.description || '';
                document.getElementById('update-language').value = data.language || '';
                document.getElementById('update-img').value = data.img || '';
                document.getElementById('update-googleid').value = data.googleid || '';

                // Přidání autorů
                if (data.writers) {
                    data.writers.forEach(author => {
                        addAuthor('update', author.id, author.name);
                    });
                }

                // Přidání žánrů
                if (data.genres) {
                    data.genres.forEach(genre => {
                        addGenre('update', genre.id, genre.name);
                    });
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
