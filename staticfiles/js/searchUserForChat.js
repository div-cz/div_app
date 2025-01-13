document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('chatSearchInput');
    const searchButton = document.getElementById('chatSearchButton');
    const resultsContainer = document.getElementById('chatSearchResults');

    // Function to perform AJAX search
    function performSearch(query) {
        if (!query.trim()) {
            resultsContainer.innerHTML = ''; // Clear results if input is empty
            return;
        }

        fetch(`/search_user_in_chat/?q=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Clear previous results
                resultsContainer.innerHTML = '';

                if (data.users.length > 0) {
                    data.users.forEach(user => {
                        const userItem = document.createElement('li');
                        userItem.classList.add('list-group-item');
                        userItem.innerHTML = `
                            <a href="/ucet/zprava-pro-${user.id}/">${user.username}</a>
                        `;
                        resultsContainer.appendChild(userItem);
                    });
                } else {
                    resultsContainer.innerHTML = '<li class="list-group-item">No users found.</li>';
                }
            })
            .catch(error => {
                console.error('Error fetching search results:', error);
            });
    }

    // Event listener for search input
    searchInput.addEventListener('input', function () {
        performSearch(searchInput.value);
    });

    // Optional: Perform search on button click
    searchButton.addEventListener('click', function () {
        performSearch(searchInput.value);
    });
});