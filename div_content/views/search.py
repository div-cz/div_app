# -------------------------------------------------------------------
#                    VIEWS.SEARCH.PY
# -------------------------------------------------------------------

from django.http import JsonResponse

from div_content.search.es_client import es
from django.conf import settings
from typing import Dict, Any, List

INDEX_NAME = getattr(settings, "BOOKS_INDEX", "books")

def search_books_service(
    q: str,
    page:  int = 1,
    size: int = 20,
    ) -> Dict[str, Any]:
    q = (q or "").strip()
    page = max(int(page or 1), 1)
    size = min(max(int(size or 20), 1), 100)
    frm = (page - 1) * size

    if not q:
        return JsonResponse({"total": 0, "results": []})

    client = es()
    res = client.search(
        index=INDEX_NAME,
        from_=frm,
        size=size,
        query={
            "multi_match": {
                "query": q,
                "fields": ["title^3", "titlecz^3", "subtitle^2", "author^2"],
                "operator": "and"
            }
        }
    )

    hits = []
    for h in res["hits"]["hits"]:
        src = h["_source"]
        hits.append({
            "id": h["_id"],
            "score": h["_score"],
            "title": src.get("title"),
            "titlecz": src.get("titlecz"),
            "author": src.get("author"),
            "authorid": src.get("authorid")
        })

    return {
        "total": res["hits"]["total"]["value"],
        "page": page,
        "size": size,
        "results": hits
    }


    