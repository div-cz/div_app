document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       MENU TOGGLE
    ========================= */

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


    /* =========================
       DARK / LIGHT MODE
    ========================= */

    const sunIcon = document.querySelector(".sun");
    const moonIcon = document.querySelector(".moon");
    const html = document.documentElement;

    if (sunIcon && moonIcon) {

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
    }


    /* =========================
       LOGOUT AJAX
    ========================= */

    const logoutBtn = document.getElementById("logout-btn");

    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {

            const logoutForm = document.getElementById("logout-form");
            if (!logoutForm) return;

            const formData = new FormData(logoutForm);

            fetch(logoutForm.action, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": formData.get("csrfmiddlewaretoken")
                },
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert("Odhlášení se nezdařilo.");
                }
            })
            .catch(error => {
                console.error("Chyba při odhlášení:", error);
                alert("Odhlášení se nezdařilo.");
            });
        });
    }


    /* =========================
       RATING (detail)
    ========================= */

    document.querySelectorAll(".rating").forEach(ratingElement => {

        const ratingValue = parseInt(ratingElement.dataset.rating) || 0;

        let gradientColor;

        if (ratingValue >= 80) gradientColor = "#0a0";
        else if (ratingValue >= 60) gradientColor = "#FFD700";
        else if (ratingValue >= 40) gradientColor = "#1E90FF";
        else if (ratingValue >= 10) gradientColor = "#FF4500";
        else gradientColor = "#555";

        ratingElement.style.setProperty("--gradient-color", gradientColor);
        ratingElement.style.setProperty("--gradient-value", `${ratingValue}%`);

        const ratingInner = ratingElement.querySelector(".rating-inner");

        if (ratingInner) {
            ratingInner.innerHTML = `${ratingValue}<span>%</span>`;
        }

    });


    /* =========================
       RATING LIST
    ========================= */

    document.querySelectorAll(".rating-list").forEach(ratingElement => {

        const ratingValue = parseInt(ratingElement.dataset.rating) || 0;

        let gradientColor;

        if (ratingValue >= 80) gradientColor = "#0a0";
        else if (ratingValue >= 60) gradientColor = "#FFD700";
        else if (ratingValue >= 40) gradientColor = "#1E90FF";
        else if (ratingValue >= 10) gradientColor = "#FF4500";
        else gradientColor = "#555";

        ratingElement.style.setProperty("--gradient-color", gradientColor);
        ratingElement.style.setProperty("--gradient-value", `${ratingValue}%`);

        const ratingInner = ratingElement.querySelector(".rating-list-inner");

        if (ratingInner) {
            ratingInner.innerHTML = `${ratingValue}<span>%</span>`;
        }

    });


    /* =========================
       NOTIFICATION DROPDOWN
    ========================= */

    const bellBtn = document.getElementById("bellBtn");
    const dropbox = document.getElementById("dropbox");

    if (bellBtn && dropbox) {

        bellBtn.addEventListener("click", (e) => {

            e.stopPropagation();

            const isHidden = dropbox.classList.contains("hidden");

            dropbox.classList.toggle("hidden", !isHidden);
            bellBtn.setAttribute("aria-expanded", isHidden);
        });

        document.addEventListener("click", (e) => {
            if (!bellBtn.contains(e.target) && !dropbox.contains(e.target)) {
                dropbox.classList.add("hidden");
                bellBtn.setAttribute("aria-expanded", "false");
            }
        });

    }


    /* =========================
       RATING POPUP (MOBILE)
    ========================= */

    const popup = document.getElementById("ratingPopup");

    if (popup) {

        const closeBtn = popup.querySelector(".popup-close");

        document.querySelectorAll(".rating-popup-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                popup.style.display = "block";
            });
        });

        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                popup.style.display = "none";
            });
        }

        popup.addEventListener("click", e => {
            if (e.target === popup) {
                popup.style.display = "none";
            }
        });

    }


    /* =========================
       CUSTOM LIST MODAL
    ========================= */

    const modal = document.getElementById("listModal");
    const openBtn = document.getElementById("openListModal");
    const closeBtn = document.querySelector(".close-modal");

    if (modal && openBtn && closeBtn) {

        openBtn.addEventListener("click", () => {
            modal.style.display = "block";
        });

        closeBtn.addEventListener("click", () => {
            modal.style.display = "none";
        });

        window.addEventListener("click", (event) => {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        });
    }
    
    const userLists = document.querySelector(".user-lists");

    if (userLists) {
        userLists.addEventListener("click", (e) => {

            const item = e.target.closest(".list-item");
            if (!item) return;

            item.classList.toggle("active");

            const toggle = item.querySelector(".list-toggle");

            toggle.textContent = item.classList.contains("active") ? "✓" : "+";

            const listId = item.dataset.listId;

            console.log("toggle list:", listId);

        });
    }

});