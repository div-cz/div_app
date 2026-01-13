function moveCarousel(carouselId, direction) {
    const carousel = document.getElementById(`${carouselId}-carousel`).querySelector('.carousel-track-index');
    const items = carousel.querySelectorAll('.carousel-item-index');
    const itemWidth = items[0].offsetWidth;
    const totalItems = items.length;

    let currentOffset = parseInt(carousel.getAttribute('data-offset') || '0', 10);
    currentOffset += direction * itemWidth;

    if (currentOffset < 0) {
        currentOffset = (totalItems - 1) * itemWidth;
    } else if (currentOffset >= totalItems * itemWidth) {
        currentOffset = 0;
    }

    carousel.style.transition = 'transition-property opacity';
    carousel.style.transform = `translateX(-${currentOffset}px)`;
    carousel.style.opacity = '0.5';  // Začátek prolínání

    setTimeout(() => {
        carousel.style.opacity = '1';  // Konec prolínání
    }, 250);

    carousel.setAttribute('data-offset', currentOffset);
}

// Automatické přehrávání každých xx sekund
setInterval(() => {
    moveCarousel('films', 1);
}, 5000);

// <![CDATA[  <-- For SVG support
if ('WebSocket' in window) {
    (function () {
        function refreshCSS() {
            var sheets = [].slice.call(document.getElementsByTagName("link"));
            var head = document.getElementsByTagName("head")[0];
            for (var i = 0; i < sheets.length; ++i) {
                var elem = sheets[i];
                var parent = elem.parentElement || head;
                parent.removeChild(elem);
                var rel = elem.rel;
                if (elem.href && typeof rel != "string" || rel.length == 0 || rel.toLowerCase() == "stylesheet") {
                    var url = elem.href.replace(/(&|\?)_cacheOverride=\d+/, '');
                    elem.href = url + (url.indexOf('?') >= 0 ? '&' : '?') + '_cacheOverride=' + (new Date().valueOf());
                }
                parent.appendChild(elem);
            }
        }
        var protocol = window.location.protocol === 'http:' ? 'ws://' : 'wss://';
        var address = protocol + window.location.host + window.location.pathname + '/ws';
        var socket = new WebSocket(address);
        socket.onmessage = function (msg) {
            if (msg.data == 'reload') window.location.reload();
            else if (msg.data == 'refreshcss') refreshCSS();
        };
        if (sessionStorage && !sessionStorage.getItem('IsThisFirstTime_Log_From_LiveServer')) {
            console.log('Live reload enabled.');
            sessionStorage.setItem('IsThisFirstTime_Log_From_LiveServer', true);
        }
    })();
}
else {
    console.error('Upgrade your browser. This Browser is NOT supported WebSocket for Live-Reloading.');
}
// ]]>



// RATING
document.addEventListener('DOMContentLoaded', () => {
    // Najdeme všechny elementy s třídou .rating
    const ratingElements = document.querySelectorAll('.rating-index');

    ratingElements.forEach(ratingElement => {
        // Získáme hodnotu hodnocení z datového atributu nebo DOM
        const ratingValue = parseInt(ratingElement.getAttribute('data-rating')) || 0;

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

        // Nastavení vlastností CSS proměnných pro každý element
        ratingElement.style.setProperty('--gradient-color', gradientColor);
        ratingElement.style.setProperty('--gradient-value', gradientValue);

        // Nastavení textu hodnocení uvnitř elementu
        const ratingInner = ratingElement.querySelector('.rating-index-inner');
        if (ratingInner) {
            ratingInner.innerHTML = `${ratingValue}<span>%</span>`;
        }
    });
});