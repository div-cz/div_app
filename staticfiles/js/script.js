
/* TOGGLE */
document.addEventListener('DOMContentLoaded', function() {
    const menuIcon = document.getElementById("menu-icon");
    const menuSection = document.getElementById("menu-section");
    const menuOpen = document.getElementById("menu-open");
    const menuClose = document.getElementById("menu-close");
    const menu = document.getElementById('menu');

    if (menuIcon && menuSection && menuOpen && menuClose) {
        menuIcon.addEventListener("click", function() {
            menuSection.classList.toggle("hidden");
            menuOpen.classList.toggle("hidden");
            menuClose.classList.toggle("hidden");
            menu.classList.toggle("hidden");
        });
    }

    /* DARK / LIGHT MODE */
    const sunIcon = document.querySelector(".sun");
    const moonIcon = document.querySelector(".moon");

    if (sunIcon && moonIcon) {
        const userTheme = localStorage.getItem("theme");
        const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches;

        const iconToggle = () => {
            sunIcon.classList.toggle("display-none");
            moonIcon.classList.toggle("display-none");
        };

        const themeCheck = () => {
            if (userTheme === "dark" || (!userTheme && systemTheme)) {
                document.documentElement.classList.add("dark");
                moonIcon.classList.add("display-none");
                // Deaktivace .bg-light ve dark mode
                document.querySelector(".bg-light").classList.add("bg-dark"); // Přepínání pozadí pro dark mode
                return;
            }
            sunIcon.classList.add("display-none");
            document.querySelector('.navbar').classList.add('light-navbar');
            document.querySelector('.footer').classList.add('light-footer');
            // Aktivace .bg-light ve světle
            document.querySelector(".bg-light").classList.remove("bg-dark"); // Zpět na světlejší režim
        };

        const themeSwitch = () => {
            if (document.documentElement.classList.contains("dark")) {
                document.documentElement.classList.remove("dark");
                localStorage.setItem("theme", "light");
                document.querySelector('.navbar').classList.add('light-navbar');
                document.querySelector('.footer').classList.add('light-footer');
                iconToggle();
                // Aktivace .bg-light ve světle
                document.querySelector(".bg-light").classList.remove("bg-dark");
                return;
            }
            document.documentElement.classList.add("dark");
            localStorage.setItem("theme", "dark");
            document.querySelector('.navbar').classList.remove('light-navbar');
            document.querySelector('.footer').classList.remove('light-footer');
            iconToggle();
            // Deaktivace .bg-light ve dark mode
            document.querySelector(".bg-light").classList.add("bg-dark");
        };

        sunIcon.addEventListener("click", () => {
            themeSwitch();
        });

        moonIcon.addEventListener("click", () => {
            themeSwitch();
        });

        themeCheck();
    }
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


