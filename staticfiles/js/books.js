$(document).ready(function() {
    // Kód pro kliknutí na záložky
    $('.tab-links a').on('click', function(e) {
        e.preventDefault(); // Zabraňte výchozímu chování odkazu

        var currentAttrValue = $(this).attr('href'); // Získejte hodnotu href (cílový ID)

        // Skryjeme všechny sekce a odstraníme třídu 'active'
        $('.tab-content').removeClass('active');
        $(currentAttrValue).addClass('active');

        // Odstraníme 'active' třídu ze všech záložek
        $('.tab-links a').removeClass('active');
        $(this).addClass('active');
    });

    // Kód pro kliknutí na "více v obchodě"
    $('#go-to-market').on('click', function(e) {
        e.preventDefault(); // Zabránit výchozímu chování odkazu

        // Odstranit aktivní třídu z ostatních záložek
        $('.tab-links a').removeClass('active');

        // Přidat aktivní třídu na záložku "Obchod"
        $('a[href="#tab5"]').addClass('active');

        // Skrytí všech sekcí záložek a zobrazení sekce "Obchod"
        $('.tab-content').removeClass('active');
        $('#tab5').addClass('active');

        // Posunutí stránky na sekci "Obchod"
        $('#tab5')[0].scrollIntoView({
            behavior: 'smooth', 
            block: 'start'
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


