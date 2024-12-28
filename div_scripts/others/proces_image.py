from django.core.files.uploadedfile import UploadedFile
from typing import Optional
from PIL import Image
from datetime import datetime
from .helpers import clean_character_name_sync
import os

def process_image(image_file: UploadedFile, author_name: str, book_title: str,
                  instance: Optional[object] = None) -> str:
    """
    Zpracuje nahraný obrázek:
    - Změní velikost na thumbnail (400x300)
    - Uloží do složky 'thumbnails' ve stejném adresáři, kde běží tento skript
    - Pokud existuje starý obrázek, smaže ho
    - Název souboru je ve formátu {rok_mesic_autor_kniha_thum.format}

    :param image_file: Nahraný obrázek (UploadedFile)
    :param author_name: Jméno autora knihy
    :param book_title: Název knihy
    :param instance: Instance objektu, která může obsahovat odkaz na starý obrázek
    :return: Relativní cesta k novému souboru
    """
    if image_file.size > 4 * 1024 * 1024:  # 4MB limit
        raise ValueError("Soubor je příliš veliký. Maximální velikost je 4MB")

    valid_image_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
    if image_file.content_type not in valid_image_types:
        raise ValueError("Vybraný soubor není obrázek. Vyberte JPEG, PNG nebo GIF")

    # Zpracování obrázku
    with Image.open(image_file) as img:
        if img.mode != 'RGB':
            img = img.convert('RGB')  # Převedení na RGB

        img.thumbnail((400, 300), Image.Resampling.LANCZOS)  # Změna velikosti na thumbnail
        print(img)

        # Získání aktuálního roku a měsíce
        current_year = datetime.now().year
        current_month = f"{datetime.now().month:02d}"  # Doplnění nulou, pokud je měsíc jednociferný

        # Ošetření jmen autora a knihy (odstranění diakritiky a speciálních znaků)
        sanitized_author = clean_character_name_sync(author_name)
        sanitized_book_title = clean_character_name_sync(book_title)

        # Formátovaný název souboru: {rok_mesic_autor_kniha_thum.format}
        file_extension = os.path.splitext(image_file.name)[1]
        new_filename = f"{sanitized_book_title}_{sanitized_author}{file_extension}"


        # Cesta pro uložení obrázku
        script_dir = os.path.dirname(__file__)  # Získá adresář, kde je uložen skript
        thumbnails_dir = os.path.join("/var/www/div_app/staticfiles/kniha", str(current_year), current_month)
        relative_path = os.path.join(str(current_year), current_month, new_filename)
        new_path = os.path.join(thumbnails_dir, new_filename)
        print(f"Relativní cesta: {relative_path}")
        print(f"Cesta na disku: {new_path}")

        # Vytvoření složky, pokud neexistuje
        os.makedirs(thumbnails_dir, exist_ok=True)
        print("Adresář vytvořen (nebo už existuje)")

        # Uložení obrázku ve formátu JPEG
        img.save(new_path, 'JPEG', quality=85)
        print("Obrázek byl uložen")

        # Odstranění starého obrázku, pokud existuje
        if instance and instance.img and instance.img != 'noimg.png':
            old_image_path = os.path.join(thumbnails_dir, instance.img)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
                print(f"Starý obrázek smazán: {old_image_path}")

        return relative_path  # Vracíme relativní cestu