from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.conf import settings

class NoCountPagination(LimitOffsetPagination):
    default_limit = 10  # Nastavení výchozího limitu
    max_limit = settings.REST_FRAMEWORK.get('MAX_LIMIT', 100)  # Načtení maximálního limitu z nastavení

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

    def paginate_queryset(self, queryset, request, view=None):
        self.offset = self.get_offset(request)
        self.limit = self.get_limit(request)

        # Kontrola maximálního limitu
        if self.limit and self.max_limit and self.limit > self.max_limit:
            self.limit = self.max_limit

        # Get one extra element to check if there is a "next" page
        q = list(queryset[self.offset: self.offset + self.limit + 1])
        if not q:
            raise ValidationError({"detail": "Offset exceeds the number of available records."})

        self.count = self.offset + len(q) if len(q) else self.offset - 1
        if len(q) > self.limit:
            q.pop()

        self.request = request
        return q

    def get_paginated_response_schema(self, schema):
        ret = super().get_paginated_response_schema(schema)
        del ret["properties"]["count"]
        return ret
