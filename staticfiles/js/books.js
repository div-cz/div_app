







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