# spouštění "python3 images.py

import requests
import os

imgURL = 'https://div.cz/favicon.ico'

def download_image_from_url(url, dest_directory):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Vytvoření názvu souboru z URL
    filename = os.path.basename(url)
    dest_path = os.path.join(dest_directory, filename)

    # Uložení obrázku do souboru
    with open(dest_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

# ...

# Místo volání funkce copy_image_to_project
download_image_from_url(imgURL, '/var/www/div_app/img/site/')

