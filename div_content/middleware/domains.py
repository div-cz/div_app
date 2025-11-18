# div_content/middleware/domains.py
# -------------------------------------------------------------------
#                    MIDDLEWARE: DOMAIN ROUTING
# -------------------------------------------------------------------

class DomainRoutingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        raw = request.get_host()
        host = raw.split(':')[0]

        print("----- DOMAIN DEBUG -----")
        print("RAW HOST:", raw)
        print("PARSED HOST:", host)
        request.META["DEBUG_HOST"] = host

        # Default
        request.urlconf = "div_config.urls"
        request.site = "div"

        # DIVKVARIAT
        if host == "divkvariat.cz" or host.endswith(".divkvariat.cz"):
            print(">>> MATCH DIVKVARIAT")
            request.urlconf = "div_content.urls.divkvariat"
            request.site = "divkvariat"
        else:
            print(">>> MATCH MAIN DIV")

        print("FINAL URLCONF:", request.urlconf)
        print("FINAL SITE:", request.site)
        print("------------------------")

        return self.get_response(request)

