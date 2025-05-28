# UTILS.FUNCTION.PY
import re
import unicodedata



def normalize_isbn(isbn):
    """Odstraní pomlčky z ISBN (např. '978-80-123-4567-8' → '9788012345678')"""
    return isbn.replace('-', '') if isbn else isbn

def format_isbn(isbn):
    """Vrátí ISBN s pomlčkami (např. '9788012345678' → '978-80-123-4567-8')
    Zatím jen jednoduché oddělení (ne validní), lze vylepšit podle prefixu"""
    if not isbn or len(isbn) != 13:
        return isbn
    return f"{isbn[:3]}-{isbn[3:5]}-{isbn[5:8]}-{isbn[8:12]}-{isbn[12]}"


def krasne_url(retezec):
    # Normalizace diakritiky a převod na odpovídající znaky bez diakritiky
    retezec = unicodedata.normalize('NFKD', retezec).encode('ascii', 'ignore').decode('ascii')

    # Nahrazení mezer a jiných nepřátelských URL znaků pomlčkami
    retezec = re.sub(r'[^\w\s-]', '', retezec).strip().lower()
    retezec = re.sub(r'[-\s]+', '-', retezec)

    # Odstranění specifických frází (pokud je potřeba)
    retezec = retezec.replace('-uncredited', '')
    retezec = retezec.replace('-voice', '')
    retezec = retezec.replace('-archive-footage', '')

    return retezec

# Příklad použití
#url = krasne_url("Příklad řetězce s diakritikou a speciálními znaky!")
#print(url)  # Vypíše: "priklad-retezce-s-diakritikou-a-specialnimi-znaky"
