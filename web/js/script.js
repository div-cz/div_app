
/* TOGGLE */
document.addEventListener("DOMContentLoaded", () => {

    /* MENU */
    const menuIcon = document.getElementById("menu-icon");
    const menuSection = document.getElementById("menu-section");
    const menuOpen = document.getElementById("menu-open");
    const menuClose = document.getElementById("menu-close");
    const menu = document.getElementById("menu");

    if (menuIcon && menuSection && menuOpen && menuClose && menu) {
        menuIcon.addEventListener("click", () => {
            menuSection.classList.toggle("hidden");
            menuOpen.classList.toggle("hidden");
            menuClose.classList.toggle("hidden");
            menu.classList.toggle("hidden");
        });
    }

    /* DARK / LIGHT MODE */
    const sunIcon = document.querySelector(".sun");
    const moonIcon = document.querySelector(".moon");

    if (!sunIcon || !moonIcon) return;

    const html = document.documentElement;

    const setInitialTheme = () => {
        const savedTheme = localStorage.getItem("theme");
        const systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

        if (savedTheme === "dark" || (!savedTheme && systemDark)) {
            html.classList.add("dark");
        } else {
            html.classList.remove("dark");
        }
    };

    const toggleTheme = () => {
        html.classList.toggle("dark");
        localStorage.setItem(
            "theme",
            html.classList.contains("dark") ? "dark" : "light"
        );
    };

    sunIcon.addEventListener("click", toggleTheme);
    moonIcon.addEventListener("click", toggleTheme);

    setInitialTheme();
});





document.addEventListener("DOMContentLoaded", function() {
    const logoutBtn = document.getElementById("logout-btn");

    // Zkontrolujeme, zda existuje prvek logout-btn
    if (logoutBtn) {
        logoutBtn.addEventListener("click", function() {
            const logoutForm = document.getElementById("logout-form");
            const formData = new FormData(logoutForm);

            fetch(logoutForm.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                },
                body: formData
            }).then(response => {
                if (response.ok) {
                    // Odhlášení bylo úspěšné
                    window.location.reload(); // Obnovíme stránku pro aktualizaci stavu
                } else {
                    alert("Odhlášení se nezdařilo.");
                }
            }).catch(error => {
                console.error("Chyba při odhlášení:", error);
                alert("Odhlášení se nezdařilo.");
            });
        });
    }
});




// RATING
document.addEventListener('DOMContentLoaded', () => {
    // Najdeme všechny elementy s třídou .rating
    const ratingElements = document.querySelectorAll('.rating');

    ratingElements.forEach(ratingElement => {
        // Získáme hodnotu hodnocení z datového atributu nebo DOM
        const ratingValue = parseInt(ratingElement.getAttribute('data-rating')) || 0;

        // Dynamický výběr barvy podle hodnocení
        let gradientColor;

        if (ratingValue >= 80) {
            gradientColor = '#0a0'; // Zelená
        } else if (ratingValue >= 60) {
            gradientColor = '#FFD700'; // Žlutá
        } else if (ratingValue >= 40) {
            gradientColor = '#1E90FF'; // Světle modrá
        } else if (ratingValue >= 10) {
            gradientColor = '#FF4500'; // Červená
        } else {
            gradientColor = '#555'; // Šedá
        }

        const gradientValue = `${ratingValue}%`;

        // Nastavení vlastností CSS proměnných pro každý element
        ratingElement.style.setProperty('--gradient-color', gradientColor);
        ratingElement.style.setProperty('--gradient-value', gradientValue);

        // Nastavení textu hodnocení uvnitř elementu
        const ratingInner = ratingElement.querySelector('.rating-inner');
        if (ratingInner) {
            ratingInner.innerHTML = `${ratingValue}<span>%</span>`;
        }
    });
});



// RATING-LIST -> ...list.html
document.addEventListener('DOMContentLoaded', () => {
    // Najdeme všechny elementy s třídou .rating
    const ratingElements = document.querySelectorAll('.rating-list');

    ratingElements.forEach(ratingElement => {
        // Získáme hodnotu hodnocení z datového atributu nebo DOM
        const ratingValue = parseInt(ratingElement.getAttribute('data-rating')) || 0;

        // Dynamický výběr barvy podle hodnocení
        let gradientColor;

        if (ratingValue >= 80) {
            gradientColor = '#0a0'; // Zelená
        } else if (ratingValue >= 60) {
            gradientColor = '#FFD700'; // Žlutá
        } else if (ratingValue >= 40) {
            gradientColor = '#1E90FF'; // Světle modrá
        } else if (ratingValue >= 10) {
            gradientColor = '#FF4500'; // Červená
        } else {
            gradientColor = '#555'; // Šedá
        }

        const gradientValue = `${ratingValue}%`;

        // Nastavení vlastností CSS proměnných pro každý element
        ratingElement.style.setProperty('--gradient-color', gradientColor);
        ratingElement.style.setProperty('--gradient-value', gradientValue);

        // Nastavení textu hodnocení uvnitř elementu
        const ratingInner = ratingElement.querySelector('.rating-list-inner');
        if (ratingInner) {
            ratingInner.innerHTML = `${ratingValue}<span>%</span>`;
        }
    });
});


const bellBtn = document.getElementById('bellBtn');
const dropbox = document.getElementById('dropbox');

if (bellBtn && dropbox) {

    bellBtn.addEventListener('click', () => {
        const isHidden = dropbox.classList.contains('hidden');
        dropbox.classList.toggle('hidden', !isHidden);
        bellBtn.setAttribute('aria-expanded', isHidden);
    });

    document.addEventListener('click', (e) => {
        if (!bellBtn.contains(e.target) && !dropbox.contains(e.target)) {
            dropbox.classList.add('hidden');
            bellBtn.setAttribute('aria-expanded', 'false');
        }
    });
}




  
// HODNOCENÍ POPUP NA MOBIL
document.addEventListener("DOMContentLoaded", () => {

    const openBtn = document.querySelector(".rating-popup-btn");
    const popup = document.getElementById("ratingPopup");
    const closeBtn = document.querySelector(".popup-close");

    if (openBtn) {
        openBtn.addEventListener("click", () => {
            popup.style.display = "block";
        });
    }

    closeBtn.addEventListener("click", () => {
        popup.style.display = "none";
    });

    // Zavření kliknutím mimo okno
    popup.addEventListener("click", e => {
        if (e.target === popup) popup.style.display = "none";
    });
});
