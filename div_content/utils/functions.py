import re
import unicodedata

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
