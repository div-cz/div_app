// Funkce pro přepínání mezi záložkami
function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed in add_book.js');

    // Automaticky otevře první záložku
    const defaultTab = document.getElementById("defaultOpen");
    if (defaultTab) {
        defaultTab.click();
    } else {
        console.log('Default tab not found');
    }

    document.querySelectorAll('input').forEach(function(input) {
        input.addEventListener('input', function() {
            if (input.value === '') {
                input.classList.add('empty-input');
                input.classList.remove('filled-input');
            } else {
                input.classList.add('filled-input');
                input.classList.remove('empty-input');
            }
        });
    });
});