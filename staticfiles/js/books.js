
$(document).ready(function(){
    $('.tab-links a').on('click', function(e) {
        e.preventDefault();
        var currentAttrValue = $(this).attr('href');

        // Show/Hide Tabs
        $('.tab-content').removeClass('active');
        $(currentAttrValue).addClass('active');

        // Change/remove current tab to active
        $('.tab-links a').removeClass('active');
        $(this).addClass('active');
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