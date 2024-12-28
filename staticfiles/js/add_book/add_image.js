// Pro každou záložku odesílání formuláře
document.querySelectorAll('.add-image-btn').forEach(button => {
    button.addEventListener('click', function() {
        const tab = this.getAttribute('data-tab');
        document.getElementById(`${tab}-img-file`).click();
    });
});

document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener('change', function() {
        const tab = this.id.split('-')[0];  // Získá "manual", "isbn", nebo "update" z ID
        const fileInput = this;
        const file = fileInput.files[0];
        const maxFileSize = 4 * 1024 * 1024; // 4MB v bytech
        const validImageTypes = ['image/jpeg', 'image/png', 'image/gif'];

        if (file) {
            // Zkontroluj, zda je soubor obrázek
            if (!validImageTypes.includes(file.type)) {
                alert('Vybraný soubor není obrázek. Vyberte JPEG, PNG nebo GIF.');
                fileInput.value = ''; // Vymaž input
                return;
            }

            // Zkontroluj velikost souboru
            if (file.size > maxFileSize) {
                alert('Soubor je příliš velký. Maximální velikost je 4 MB.');
                fileInput.value = ''; // Vymaž input
                return;
            }

            // Pokud soubor splňuje požadavky, zobraz název souboru v textovém poli
            document.getElementById(`${tab}-img`).value = file.name;
        }
    });
});


document.addEventListener('DOMContentLoaded', function () {
    // Funkce pro přepínání inputu pro obrázek na základě výběru a logování změn
    function toggleImageInput(tab) {
        const selectedOption = document.querySelector(`input[name="${tab}-img-option"]:checked`);
        const imgFileContainer = document.getElementById(`${tab}-img-file-container`);

        // Logování změny radio tlačítek
        console.log(`Změna v radio tlačítku pro ${tab}: Vybrána možnost "${selectedOption.value}"`);

        // Zobrazíme nebo skryjeme input pro nahrání obrázku
        if (selectedOption.value === 'upload-img') {
            imgFileContainer.style.display = 'block';
        } else {
            imgFileContainer.style.display = 'none';
        }
    }

    // Pro každou záložku (manual, isbn, update) přidáme event listener
    ['manual', 'isbn', 'update'].forEach(function (tab) {
        const uploadImgOption = document.getElementById(`${tab}-upload-img-option`);
        const googleIdOption = document.getElementById(`${tab}-google-id-option`);
        const noImgOption = document.getElementById(`${tab}-no-img-option`);

        if (uploadImgOption && googleIdOption && noImgOption) {
            uploadImgOption.addEventListener('change', function () { toggleImageInput(tab); });
            googleIdOption.addEventListener('change', function () { toggleImageInput(tab); });
            noImgOption.addEventListener('change', function () { toggleImageInput(tab); });
        }

        // Logování změn souboru při nahrání (file input)
        const fileInput = document.getElementById(`${tab}-img-file`);
        if (fileInput) {
            fileInput.addEventListener('change', function () {
                if (fileInput.files.length > 0) {
                    const file = fileInput.files[0];
                    console.log(`Změna v nahraném souboru pro ${tab}: ${file.name}, velikost: ${file.size} bytes`);
                } else {
                    console.log(`Nebyly vybrány žádné soubory pro ${tab}.`);
                }
            });
        }

        // Spuštění toggle při načtení stránky, pokud uživatel něco vybral
        toggleImageInput(tab);
    });
});