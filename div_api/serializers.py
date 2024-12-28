from rest_framework import serializers
from rest_framework.reverse import reverse


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        # fields = '__all__'
        pass

def create_serializer(model, exclude_fields=[], related_fields={}, detail_url_name=None):
    meta_class = type('Meta', (object,), {'model': model, 'exclude': tuple(exclude_fields) if exclude_fields else ()})
    serializer_fields = {'Meta': meta_class}

    for field_name, field_serializer in related_fields.items():
        serializer_fields[field_name] = serializers.SerializerMethodField()

        def get_related_field(self, obj, field_name=field_name, field_serializer=field_serializer):
            related_objects = getattr(obj, field_name).all()
            return field_serializer(related_objects, many=True).data

        serializer_fields[f'get_{field_name}'] = get_related_field

    if detail_url_name:
        serializer_fields['detail_url'] = serializers.SerializerMethodField()

        def get_detail_url(self, obj):
            request = self.context.get('request')
            url = reverse(detail_url_name, args=[obj.pk], request=request)
            return url.replace('http://', 'https://') if request and request.is_secure() else url

        serializer_fields['get_detail_url'] = get_detail_url

    return type(f'{model.__name__}Serializer', (BaseSerializer,), serializer_fields)


# Base serializer for both Movie and Tvshow
class BaseMediaSerializer(BaseSerializer):

    ###Base methoda na zobrazeni relatedkeys, ale je na zacatku poradi

    # genres = serializers.SerializerMethodField()
    # directors = serializers.SerializerMethodField()
    # actors = serializers.SerializerMethodField()
    # countries = serializers.SerializerMethodField()
    # keywords = serializers.SerializerMethodField()

    def get_genres(self, obj):
        if hasattr(obj, 'moviegenre_set'):
            # Use preloaded related objects to avoid additional queries
            return [mg.genreid.genrename for mg in obj.moviegenre_set.all()]
        elif hasattr(obj, 'tvgenre_set'):
            return [tg.genreid.genrename for tg in obj.tvgenre_set.all()]
        return []

    ### dodělat tvshows, az budou pridane
    def get_countries(self, obj):
        if hasattr(obj, 'moviecountries_set'):
            return [mc.countryid.countrynamecz for mc in obj.moviecountries_set.all()]
        else:
            return []

    ### dodělat tvshows, az budou pridane
    def get_keywords(self, obj):
        if hasattr(obj, 'moviekeywords_set'):
            return [mk.keywordid.keyword for mk in obj.moviekeywords_set.all()]
        else:
            return []

    ### dodělat tvshows, az budou pridane
    def get_production(self, obj):
        if hasattr(obj, 'movieproductions_set'):
            return [mp.productionid.name for mp in obj.movieproductions_set.all()]
        else:
            return []

    ### dodělat tvshows, az budou pridane
    def get_collection(self, obj):
        if obj.universumid:
            return [] if obj.universumid.universumid == 1 else obj.universumid.universumname
        else:
            return []

    def get_directors(self, obj):
        if hasattr(obj, 'moviecrew_set'):
            directors = [crew for crew in obj.moviecrew_set.all() if crew.roleid.rolename == 'Director']
        elif hasattr(obj, 'tvcrew_set'):
            directors = [crew for crew in obj.tvcrew_set.all() if crew.roleid.rolename == 'Director']
        else:
            directors = []

        return [f"{director.peopleid.firstname} {director.peopleid.lastname}" for director in directors]

    def get_actors(self, obj):
        if hasattr(obj, 'moviecrew_set'):
            actors = [crew for crew in obj.moviecrew_set.all() if crew.roleid.rolename == 'Actor']
        elif hasattr(obj, 'tvcrew_set'):
            actors = [crew for crew in obj.tvcrew_set.all() if crew.roleid.rolename == 'Actor']
        else:
            actors = []

        return [f"{actor.peopleid.firstname} {actor.peopleid.lastname}" for actor in actors]

    ###Upravene zobrazeni reprezentace related_search veci, ktere je pridano na konec
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        metadatas = ['genres', 'directors', 'actors', 'countries', 'keywords','production']
        # Odstranění klíčů z reprezentace
        for metadata in metadatas:
            representation.pop(metadata, None)

            # Přidání nových hodnot do reprezentace
        for metadata in metadatas:
            # Získání metody na základě jména
            meta_method = getattr(self, f'get_{metadata}')
            # Zavolání metody a uložení výsledku
            meta_value = meta_method(instance)
            # Přidání výsledku do reprezentace
            representation[metadata] = meta_value

        representation['collection'] = self.get_collection(instance)

        return representation






