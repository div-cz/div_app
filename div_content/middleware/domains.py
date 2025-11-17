# -------------------------------------------------------------------
#                    MIDDLEWARE.DOMAINS.PY
# -------------------------------------------------------------------


class DomainRoutingMiddleware:
    """
    Univerzální middleware pro detekci projektu podle domény / subdomény.

    Do requestu doplní:
    - request.domain      -> 'divkvariat.cz'
    - request.root_domain -> 'divkvariat.cz'
    - request.subdomain   -> např. 'magic' / 'test' / None
    - request.project     -> název projektu (např. 'divkvariat')
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Tady se definuje mapování domény → projekt
        self.domain_map = {
            "divkvariat.cz": "divkvariat",
            "div.cz": "div",
            "fdk.cz": "fdk",
        }

    def __call__(self, request):
        # 1) hostname bez portu
        host = request.get_host().split(":")[0]

        # 2) rozpad subdomén
        parts = host.split(".")  # např. ["magic", "divkvariat", "cz"]

        if len(parts) == 2:
            # doména typu divkvariat.cz
            request.root_domain = host
            request.subdomain = None

        elif len(parts) >= 3:
            # např. magic.divkvariat.cz → root je "divkvariat.cz"
            request.subdomain = parts[0]
            request.root_domain = ".".join(parts[1:])

        else:
            request.root_domain = host
            request.subdomain = None

        # 3) identifikace projektu – podle root domény
        request.project = self.domain_map.get(request.root_domain, "default")

        # 4) přidáme i request.domain (původní)
        request.domain = host

        return self.get_response(request)
