const panels = document.querySelectorAll('.panel');


if (panels.length > 0) {
    let currentIndex = 0; // Index aktu�ln� aktivn�ho panelu

    function removeActiveClasses() {
        panels.forEach(panel => {
            panel.classList.remove('active');
        });
    }

    function setActivePanel(index) {
        removeActiveClasses();
        panels[index].classList.add('active');
    }

    // Nastaven� inici�ln�ho panelu jako aktivn�ho
    setActivePanel(currentIndex);

    // Automatick� p�ep�n�n� panel� po 10 sekund�ch (10000 ms)
    setInterval(() => {
        currentIndex = (currentIndex + 1) % panels.length; // Posun na dal�� panel a zp�t na prvn� po posledn�m
        setActivePanel(currentIndex);
    }, 5000);

    // Zajist�me, �e ru�n� kliknut� na panel p�ep�e automatick� p�ep�na�
    panels.forEach((panel, index) => {
        panel.addEventListener('click', () => {
            currentIndex = index; // Nastav� aktu�ln� panel na index kliknut�ho panelu
            setActivePanel(currentIndex);
        });
    });
}




document.addEventListener('DOMContentLoaded', function() {

    // Z�sk�me CSRF token z vygenerovan�ho skryt�ho inputu

    var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    document.querySelectorAll('.btn-action').forEach(function(button) {
        button.addEventListener('click', function(e) {

            e.preventDefault(); // Zamez�me v�choz� akci tla��tka, pokud je n�jak�

            var gameId = button.getAttribute('data-game-id');
            var listType = button.getAttribute('data-list-type');
            var thankYouMessage = document.getElementById('add-thankyou');

            // Odes�l�n� po�adavku na server

            fetch("/hra/add-to-list/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",

                    "X-CSRFToken": csrfToken  // P�id�n� CSRF token

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


                    // Skryjeme hl�ku po 4 sekund�ch

                    setTimeout(function() {
                        thankYouMessage.style.display = 'none';
                    }, 4000);
                } else {

                    alert("N�co se pokazilo. Zkuste to pros�m znovu.");

                }
            });
        });
    });

});





console.log("Script running!");
document.addEventListener('DOMContentLoaded', function() {
    console.log("Script running!");
    document.querySelectorAll('.star-ratings-rate-action').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var thankYouMessage = document.getElementById('rating-thankyou2');
            thankYouMessage.style.display = 'block';
            location.reload();

            // Skryjte hl�ku po 3 sekund�ch
            setTimeout(function() {
                thankYouMessage.style.display = 'none';
                
            }, 3000);
        });
    });
});


