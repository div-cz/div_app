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

    // Aplikujeme nové hodnoty pro podbarvení
    background.style.transform = `translateX(${left}px)`;
    background.style.width = `${width}px`;

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



