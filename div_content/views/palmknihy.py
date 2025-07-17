# -------------------------------------------------------------------
#                    VIEWS.PALMKNIHY.PY
# -------------------------------------------------------------------



### Views pro napojenĂ­ na API Palmknihy

# Obsah:
# -------
# 1. đebooks_bestsellers_view - vypis bestsellery na hlavni strane
# 2. đebook_detail_view - detail e-knihy (z API)
# 3. đebook_search_view - pripadneĂ hledaniĂ­
# 4. đpomocne funkce pro konverzi a filtrovani


from div_content.utils import palmknihy



def get_palmknihy_ebooks(limit=100):
    try:
        return palmknihy.get_catalog_product(limit=limit, available=True)
    except Exception as e:
        print(f"E: Chyba při načítání e-knih: {e}")
        return []

