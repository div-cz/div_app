$(document).ready(function () {
    // Kód pro kliknutí na záložky
    $('.tab-links a').on('click', function (e) {
        e.preventDefault();

        var currentAttrValue = $(this).attr('href');

        if ($(currentAttrValue).length) { // Kontrola existence sekce
            $('.tab-list').removeClass('active');
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

            $('.tab-list').removeClass('active');
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




console.log("Script running!");
document.addEventListener('DOMContentLoaded', function() {
    console.log("Script running!");
    document.querySelectorAll('.star-ratings-rate-action').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var thankYouMessage = document.getElementById('rating-thankyou2');
            thankYouMessage.style.display = 'block';
            location.reload();

            // Skryjte hlaku po 3 sekundach
            setTimeout(function() {
                thankYouMessage.style.display = 'none';
                
            }, 3000);
        });
    });

});


