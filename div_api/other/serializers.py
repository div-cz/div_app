from rest_framework import serializers
from rest_framework.reverse import reverse
from ..serializers import create_serializer
from div_content.models import Metagenre,Metaindex,Creator,Creatorrole,Charactermeta

# Define Genre Serializer
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metagenre
        fields = ['genreid','genrename']

# Define Generic Genre Serializer for both Movie and Tvshow genres
class GenericGenreSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(source='genre', required=False)

    class Meta:
        fields = ['genreid', 'genre']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('view', None) and self.context['view'].action != 'retrieve':
            representation.pop('genre', None)
        return representation

    @classmethod
    def create_for_model(cls, model):
        meta_class = type('Meta', (object,), {'model': model, 'fields': cls.Meta.fields})
        return type(f'{model.__name__}Serializer', (cls,), {'Meta': meta_class})

# Define Crew Serializer
class CrewSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        fields = ['name']

    def get_name(self, obj):
        return f"{obj.peopleid.firstname} {obj.peopleid.lastname}"

# Use the function to create serializers
MetaindexSerializer = create_serializer(Metaindex)
CreatorSerializer = create_serializer(Creator, detail_url_name='creator-detail')
CharactermetaSerializer = create_serializer(Charactermeta)
CreatorroleSerializer = create_serializer(Creatorrole)
