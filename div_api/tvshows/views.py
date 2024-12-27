from django.db.models import Prefetch
from div_content.models import Tvshow,Tvgenre,Tvcrew
from .serializers import TvshowSerializer,TvshowListSerializer
from ..views import BaseViewSet


class TvshowViewSet(BaseViewSet):
    queryset = Tvshow.objects.all()
    search_fields = ['titlecz']

    def apply_select_related_and_prefetch_related(self, queryset):
        return queryset.prefetch_related(
            Prefetch('tvgenre_set', queryset=Tvgenre.objects.select_related('genreid')),
            Prefetch('tvcrew_set', queryset=Tvcrew.objects.select_related('peopleid', 'roleid'))
                                         )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'view': self
        })
        return context

    def get_serializer_class(self):
        if self.action == 'list':
            return TvshowListSerializer
        return TvshowSerializer
