from rest_framework import serializers
from rest_framework.reverse import reverse
from div_content.models import Tvshow,Tvgenre
from ..serializers import BaseSerializer,BaseMediaSerializer
from ..other.serializers import GenericGenreSerializer


# Tvshow Serializer
class TvshowSerializer(BaseMediaSerializer):
    class Meta(BaseMediaSerializer.Meta):
        model = Tvshow
        fields = '__all__'

class TvshowListSerializer(serializers.ModelSerializer):
    tvshow_detail_link = serializers.SerializerMethodField()

    class Meta:
        model = Tvshow
        fields = ['tvshowid', 'title', 'titlecz', 'premieredate', 'popularity', 'tvshow_detail_link']

    def get_tvshow_detail_link(self, obj):
        request = self.context.get('request')
        url = reverse('tvshow-detail', args=[obj.pk], request=request)
        return url.replace('http://', 'https://') if request and request.is_secure() else url

# Create specific genre serializers using the generic genre serializer
TvshowgenreSerializer = GenericGenreSerializer.create_for_model(Tvgenre)