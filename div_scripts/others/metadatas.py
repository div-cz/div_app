from typing import Dict,List,Any
from django.views.decorators.http import require_GET
from django.db.models import QuerySet
from div_content.models import Metagenre,Bookpublisher
from django.http import JsonResponse

def search_genres(search: str) -> QuerySet[Metagenre]:
    """
    Vyhledává v Metagenre.

    Args:
        search (str): Hledaný výraz.

    Returns:
        QuerySet: Výsledný queryset po aplikaci filtrů.
    """
    search = search.strip()

    if search:
        return Metagenre.objects.filter(genrenamecz__icontains=search).order_by('genrenamecz')
    else:
        return Metagenre.objects.none()  # Nebo můžete vyvolat výjimku

@require_GET
def ajax_search_genres(request) -> JsonResponse:
    """
    AJAX view pro vyhledávání v Metagenre a Metapublisher tabulkách.

    GET Parametry:
    - search: str (hledaný výraz)
    - exclude_ids: str (volitelné, čárkami oddělené ID, která se mají vyřadit)

    Returns:
    - JsonResponse: JSON odpověď s výsledky nebo chybovou zprávou.
    """
    search: str = request.GET.get('search', '').strip()
    exclude_ids: str = request.GET.get('exclude_ids', '').strip()

    if not search:
        return JsonResponse({'error': 'Chybí parametr "search".'}, status=400)

    # Definice mapování ID polí pro vyřazení
    id_field_map: Dict[str, str] = {
        'metagenre': 'genreid',
    }

    # Vyhledávání
    queryset: QuerySet = search_genres(search)

    # Vyřazení ID, pokud jsou poskytnuta
    if exclude_ids:
        try:
            exclude_id_list: List[int] = [int(aid) for aid in exclude_ids.split(',') if aid.isdigit()]
            queryset = queryset.exclude(**{f"metagenre__in": exclude_id_list})
        except ValueError:
            return JsonResponse({'error': 'Neplatný parametr "exclude_ids".'}, status=400)

    # Omezení počtu výsledků
    queryset = queryset[:20]

    # Příprava dat pro JSON odpověď
    data: List[Dict[str, Any]] = []
    for entity in queryset:
        data.append({
            'genreid': entity.genreid,
            'genrename': entity.genrenamecz,
        })

    return JsonResponse({'results': data}, status=200)

def search_publisher(search: str) -> QuerySet[Bookpublisher]:
    """
    Vyhledává v Bookpublisher.

    Args:
        query (str): Hledaný výraz.

    Returns:
        QuerySet: Výsledný queryset po aplikaci filtrů.
    """
    search = search.strip()

    if search:
        return Bookpublisher.objects.filter(publishername__icontains=search).order_by('publishername')
    else:
        return Bookpublisher.objects.none()  # Nebo můžete vyvolat výjimku

@require_GET
def ajax_search_publisher(request) -> JsonResponse:
    """
    AJAX view pro vyhledávání v Metapublisher.

    GET Parametry:
    - search: str (hledaný výraz)

    Returns:
    - JsonResponse: JSON odpověď s výsledky nebo chybovou zprávou.
    """
    search: str = request.GET.get('search', '').strip()

    if not search:
        return JsonResponse({'error': 'Chybí parametr "query".'}, status=400)

    # Vyhledávání
    queryset: QuerySet = search_publisher(search)

    # Omezení počtu výsledků
    queryset = queryset[:20]

    # Příprava dat pro JSON odpověď
    data: List[Dict[str, Any]] = []
    for entity in queryset:
        data.append({
            'publisherid': entity.publisherid,
            'publishername': entity.publishername,
        })

    return JsonResponse({'results': data}, status=200)
