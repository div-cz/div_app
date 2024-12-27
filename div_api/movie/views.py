from django.db.models import Prefetch
from div_content.models import Movie,Metaindex,Moviegenre,Moviecrew,Moviecountries,Moviekeywords,Movieproductions
from .serializers import MovieSerializer,MovieListSerializer
from ..other.serializers import MetaindexSerializer
from ..views import BaseViewSet



class MovieViewSet(BaseViewSet):
    queryset = Movie.objects.all()
    search_fields = ['titlecz']

    def apply_select_related_and_prefetch_related(self, queryset):
        return queryset.prefetch_related(
            Prefetch('moviegenre_set', queryset=Moviegenre.objects.select_related('genreid')),
            Prefetch('moviecrew_set', queryset=Moviecrew.objects.select_related('peopleid', 'roleid')),
            Prefetch('moviecountries_set', queryset=Moviecountries.objects.select_related('countryid')),
            Prefetch('moviekeywords_set', queryset=Moviekeywords.objects.select_related('keywordid')),
            Prefetch('movieproductions_set', queryset=Movieproductions.objects.select_related('productionid')),
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'view': self
        })
        return context

    def get_serializer_class(self):
        if self.action == 'list':
            return MovieListSerializer
        return MovieSerializer

class TopMovieListView(BaseViewSet):
    serializer_class = MetaindexSerializer
    queryset = Metaindex.objects.filter(section="Movie")