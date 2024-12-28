from typing import List, Dict
from django.views.decorators.http import require_GET
from django.db.models.functions import Concat, Coalesce
from django.db.models import Q, Value, CharField, QuerySet
from django.http import JsonResponse,HttpRequest
from div_content.models import Bookauthor
def search_authors(query:str) -> QuerySet[Bookauthor]:
    terms = query.strip().split()
    if not terms:
        return Bookauthor.objects.none()  # Return an empty queryset if no terms

    queryset = Bookauthor.objects.annotate(
        full_name=Concat(
            'firstname',
            Value(' '),
            Coalesce('middlename', Value('')),
            Value(' '),
            'lastname',
            output_field=CharField()
        )
    )

    filters = Q()
    for term in terms:
        filters &= Q(full_name__icontains=term)

    queryset = queryset.filter(filters).order_by('lastname', 'firstname')
    return queryset

@require_GET
def ajax_search_authors(request:HttpRequest) -> JsonResponse:
    query = request.GET.get('search', '').strip()
    exclude_authors = request.GET.get('exclude_authors', '')
    exclude_author_ids = [int(aid) for aid in exclude_authors.split(',') if aid.isdigit()]

    if not query:
        return JsonResponse({'results': []})

    authors = search_authors(query)

    if exclude_author_ids:
        authors = authors.exclude(authorid__in=exclude_author_ids)

    authors = authors[:20]

    data: List[Dict[str,str]] = [
        {
            'authorid': author.authorid,
            'full_name': f"{author.firstname} {author.middlename or ''} {author.lastname}".strip(),
            'birthyear': author.birthyear,
        }
        for author in authors
    ]

    return JsonResponse({'results': data})