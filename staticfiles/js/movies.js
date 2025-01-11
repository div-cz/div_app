$(document).ready(function() {
    // Initialize DataTable
    var table = $('#moviesTable').DataTable();

    // Apply the filter
    $('#genresFilter, #ratingFilter').on('change', function() {
        table.draw();
    });

    // Custom filtering function
    $.fn.dataTable.ext.search.push(
        function(settings, data, dataIndex) {
            var genres = $('#genresFilter').val();
            var minRating = $('#ratingFilter').val();

            var rowGenres = data[2]; // Genres is in the second column
            var rowRating = parseInt(data[3].split('/')[0]); // Extract rating from format "X/10"

            if ((genres === "" || genres === rowGenres) && (minRating === "0" || rowRating >= minRating)) {
                return true; // Show row
            }
            return false; // Hide row
        }
    );
});

$('#moviesTable').DataTable({
    "language": {
        "lengthMenu": "Zobrazit _MENU_ záznamů",
        "zeroRecords": "Žádné záznamy nebyly nalezeny",
        "info": "Strana _PAGE_ z _PAGES_",
        "infoEmpty": "Žádné záznamy k dispozici",
        "infoFiltered": "(vyfiltrováno z celkem _MAX_ záznamů)",
        "search": "Hledat:",
        "paginate": {
            "first":      "První",
            "last":       "Poslední",
            "next":       "Další",
            "previous":   "Předchozí"
        },
    },

    "order": [[ 0, "desc" ]], 
    "pageLength": 25
});

$(document).ready(function(){
    $('#image-slider').slick({
        infinite: true,
        slidesToShow: 1,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 3000,
        dots: true,
        arrows: false, // Skryjeme šipky, pokud nejsou potřeba
        fade: true,
        cssEase: 'linear'
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

            // Skryjte hlášku po 3 sekundách
            setTimeout(function() {
                thankYouMessage.style.display = 'none';
                
            }, 3000);
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    document.querySelectorAll('.btn-action').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            var movieId = button.getAttribute('data-movie-id');
            var listType = button.getAttribute('data-list-type');
            var thankYouMessage = document.getElementById('add-thankyou');
            var userIsAuthenticated = button.getAttribute('data-user-authenticated') === 'true';

            if (userIsAuthenticated) {
                fetch("/film/add-to-list/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({
                        media_id: movieId,
                        list_type: listType,
                        media_type: "movie"
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

                        setTimeout(function() {
                            thankYouMessage.style.display = 'none';
                        }, 2000);
                    } else {
                        alert("Něco se pokazilo. Zkuste to prosím znovu.");
                    }
                });
            } else {
                thankYouMessage.textContent = button.getAttribute('data-message');
                thankYouMessage.style.display = 'block';

                setTimeout(function() {
                    thankYouMessage.style.display = 'none';
                    //location.reload();
                }, 2000);
            }
        });
    });
});



$(document).ready(function () {
    // Kód pro kliknutí na záložky
    $('.tab-links a').on('click', function (e) {
        e.preventDefault();

        var currentAttrValue = $(this).attr('href');

        if ($(currentAttrValue).length) { // Kontrola existence sekce
            $('.tab-content').removeClass('active');
            $(currentAttrValue).addClass('active');

            $('.tab-links a').removeClass('active');
            $(this).addClass('active');
        } else {
            console.error('Sekce neexistuje: ', currentAttrValue);
        }
    });

    // Kód pro kliknutí na "další..."
    $('#go-to-characters').on('click', function (e) {
        e.preventDefault();

        var targetTab = '#tab2';

        if ($(targetTab).length) { // Kontrola existence sekce
            $('.tab-links a').removeClass('active');
            $('a[href="' + targetTab + '"]').addClass('active');

            $('.tab-content').removeClass('active');
            $(targetTab).addClass('active');

            $(targetTab)[0].scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        } else {
            console.error('Sekce neexistuje: ', targetTab);
        }
    });
});



// RATING
document.addEventListener('DOMContentLoaded', () => {
    const ratingElement = document.querySelector('.rating');
    const ratingValue = 90; // Změňte na hodnotu hodnocení

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

    // Nastavení barvy a hodnoty na ::after pomocí inline stylu
    ratingElement.style.setProperty('--gradient-color', gradientColor);
    ratingElement.style.setProperty('--gradient-value', gradientValue);

    // Nastavení textu hodnocení
    const ratingInner = document.querySelector('.rating-inner');
    ratingInner.innerHTML = `${ratingValue}<span>%</span>`;
});