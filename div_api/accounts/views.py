from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.generic import View
from rest_framework.views import APIView

from allauth.account.utils import user_display


class CsfrTokenView(View):
    def get(self, request, *args, **kwargs):
        """
        The frontend queries (GET) this endpoint, expecting to receive
        either a 401 if no user is authenticated, or user information.
        """
        # Needed -- so that the CSRF token is set in the response for the
        # frontend to pick up.
        get_token(request)
        if request.user.is_anonymous:
            resp = JsonResponse({})
            resp.status_code = 401
            return resp
        data = {
            "username": request.user.username,
            "id": request.user.pk,
            "display": user_display(request.user),
        }

        return JsonResponse(data)

csfr_token = CsfrTokenView.as_view()
