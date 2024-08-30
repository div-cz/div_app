const panels = document.querySelectorAll('.panel');
let currentIndex = 0; // Index aktuálně aktivního panelu

function removeActiveClasses() {
    panels.forEach(panel => {
        panel.classList.remove('active');
    });
}

function setActivePanel(index) {
    removeActiveClasses();
    panels[index].classList.add('active');
}

// Nastavení iniciálního panelu jako aktivního
setActivePanel(currentIndex);

// Automatické přepínání panelů po 10 sekundách (10000 ms)
setInterval(() => {
    currentIndex = (currentIndex + 1) % panels.length; // Posun na další panel a zpět na první po posledním
    setActivePanel(currentIndex);
}, 5000);

// Zajistíme, že ruční kliknutí na panel přepíše automatický přepínač
panels.forEach((panel, index) => {
    panel.addEventListener('click', () => {
        currentIndex = index; // Nastaví aktuální panel na index kliknutého panelu
        setActivePanel(currentIndex);
    });
});



document.addEventListener('DOMContentLoaded', function() {
    // Získáme CSRF token z vygenerovaného skrytého inputu
    var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    document.querySelectorAll('.btn-action').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault(); // Zamezíme výchozí akci tlačítka, pokud je nějaká

            var movieId = button.getAttribute('data-game-id');
            var listType = button.getAttribute('data-list-type');
            var thankYouMessage = document.getElementById('add-thankyou');

            // Odesílání požadavku na server
            fetch("/hra/add-to-list/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken  // Přidání CSRF token
                },
                body: JSON.stringify({
                    media_id: gameId,
                    list_type: listType,
                    media_type: "game"
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.action === "added") {
                        thankYouMessage.textContent = button.getAttribute('data-message-added'); 
                    } else if (data.action === "removed") {
                        thankYouMessage.textContent = button.getAttribute('data-message-removed'); 
                    }
                    thankYouMessage.style.display = 'block';

                    // Skryjeme hlášku po 4 sekundách
                    setTimeout(function() {
                        thankYouMessage.style.display = 'none';
                    }, 4000);
                } else {
                    alert("Něco se pokazilo. Zkuste to prosím znovu.");
                }
            });
        });
    });
});