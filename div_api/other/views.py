from div_content.models import Creator,Metagenre
from rest_framework import mixins
from .serializers import CreatorSerializer,GenreSerializer
from ..views import BaseViewSet

class CreatorViewSet(BaseViewSet):
    serializer_class = CreatorSerializer
    queryset = Creator.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

class GenreViewSet(BaseViewSet): #mixins.CreateModelMixin):
    serializer_class = GenreSerializer
    queryset = Metagenre.objects.all()
    search_fields = ['genrenamecz']