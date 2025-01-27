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