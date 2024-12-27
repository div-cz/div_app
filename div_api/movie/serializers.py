from rest_framework import serializers
from rest_framework.reverse import reverse
from div_content.models import Movie,Moviegenre
from ..serializers import BaseSerializer,BaseMediaSerializer
from ..other.serializers import GenericGenreSerializer

# Movie Serializer
class MovieSerializer(BaseMediaSerializer):
    class Meta(BaseMediaSerializer.Meta):
        model = Movie
        exclude = ['special', 'oldurl', 'ChangeURL', 'idcsfd', 'idimdb', 'iddiv']

class MovieListSerializer(serializers.ModelSerializer):
    movie_detail_link = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['movieid', 'title', 'titlecz', 'releaseyear', 'popularity', 'movie_detail_link']

    def get_movie_detail_link(self, obj):
        request = self.context.get('request')
        url = reverse('movie-detail', args=[obj.pk], request=request)
        return url.replace('http://', 'https://') if request and request.is_secure() else url

# Create specific genre serializers using the generic genre serializer
MoviegenreSerializer = GenericGenreSerializer.create_for_model(Moviegenre)