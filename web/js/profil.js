document.addEventListener('DOMContentLoaded', function() {
    // Funkce na aktivaci konkrétního tabu
    function activateTab(tabId) {
        document.querySelectorAll('.tab-show').forEach(tabContent => {
            tabContent.classList.remove('active');
        });
        document.querySelectorAll('.nav-tabs-link').forEach(tab => {
            tab.classList.remove('active');
        });
        const targetTab = tabId.replace('tab-', '');
        document.getElementById(targetTab).classList.add('active');
        document.getElementById('tab-' + targetTab).classList.add('active');
    }

    // Kontrola, jestli je v URL fragment (část po #)
    const hash = window.location.hash.substring(1);  // Získá fragment bez #
    if (hash) {
        activateTab('tab-' + hash);  // Aktivuje příslušný tab
    }

    // Přepínání tabů po kliknutí
    document.querySelectorAll('.nav-tabs-link').forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            const targetTab = this.getAttribute('id');
            activateTab(targetTab);
            // Aktualizace URL bez reloadu stránky
            history.pushState(null, null, '#' + targetTab.replace('tab-', ''));
        });
    });
});


function updateNavTabSelector(activeTab) {
    const parent = document.querySelector('.nav-tabs'); // Rodičovský prvek
    const background = parent.querySelector('.background'); // Posuvné podbarvení

    // Najdeme pozici aktivní záložky
    const activeRect = activeTab.getBoundingClientRect();
    const parentRect = parent.getBoundingClientRect();

    // Správný výpočet posunu s ohledem na scrollování
    const left = activeRect.left - parentRect.left + parent.scrollLeft;
    const width = activeRect.width;

    // Aktualizujeme aktivní třídu
    parent.querySelectorAll('.nav-tabs-link').forEach(link => link.classList.remove('active'));
    activeTab.classList.add('active');
}

// Inicializace při načtení stránky
window.addEventListener('DOMContentLoaded', () => {
    const initialTab = document.querySelector('.nav-tabs-link.active');
    if (initialTab) {
        updateNavTabSelector(initialTab);
    }
});



document.addEventListener("DOMContentLoaded", function () {
    // Zkontrolujte, zda URL obsahuje hash
    if (window.location.hash) {
        const hash = window.location.hash;
        // Najděte sekci podle ID hashe
        const targetElement = document.querySelector(hash);
        if (targetElement) {
            // Scroll na pozici daného elementu
            targetElement.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }
});

// Přečte parametry v URL a pokud obsahuje fav_creators_page nebo fav_characters_page tak scrolluje na daný div element
document.addEventListener('DOMContentLoaded', function () {
const urlParams = new URLSearchParams(window.location.search);

if (urlParams.has('fav_creators_page')) {
    const favCreatorsSection = document.getElementById('tvurci');
    if (favCreatorsSection) {
        setTimeout(() => {
            favCreatorsSection.scrollIntoView({ behavior: 'smooth' });
        }, 100);
    }
}
if (urlParams.has('fav_characters_page')) {
    const favCreatorsSection = document.getElementById('postavy');
    if (favCreatorsSection) {
        setTimeout(() => {
            favCreatorsSection.scrollIntoView({ behavior: 'smooth' });
        }, 100);
    }
}
});




/* VYHLEDÁVÁNÍ NA PROFILU */
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
                    resultsContainer.innerHTML = '<li class="list-group-item">Žádný uživatel nenalezen.</li>';
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