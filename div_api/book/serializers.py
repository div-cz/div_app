from rest_framework import serializers
from rest_framework.reverse import reverse
from div_content.models import Book, Bookauthor, Bookgenre, Bookisbn, Bookwriters, Metapublisher
from ..serializers import BaseSerializer
from ..other.serializers import GenericGenreSerializer

# Define Book Serializer
class BookSerializer(BaseSerializer):
    ####
    # genres = serializers.SerializerMethodField()
    # isbns = serializers.SerializerMethodField()
    # writers = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = '__all__'

    def get_genres(self, obj):
        if hasattr(obj, 'bookgenre_set'):
            return [genre.genreid.genrename for genre in obj.bookgenre_set.all()]
        return []

    def get_isbns(self, obj):
        if hasattr(obj, 'bookisbn_set'):
            return [{"isbn":isbn.isbn,"isbn_type":isbn.ISBNtype,"publisher":isbn.publisherid.publishername if isbn.publisherid else []} for isbn in obj.bookisbn_set.all()]
        return []

    def get_writers(self, obj):
        if hasattr(obj, 'bookwriters_set'):
            return [" ".join(filter(None,(author.author.firstname,author.author.middlename,author.author.lastname))) for author in obj.bookwriters_set.all()]
        return []

    ###Upravene zobrazeni reprezentace related_search veci, ktere je pridano na konec
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        metadatas = ['genres', 'isbns', 'writers']
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

        return representation

class BookListSerializer(serializers.ModelSerializer):
    book_detail_link = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['bookid', 'title', 'author', 'language', 'book_detail_link']

    def get_book_detail_link(self, obj):
        request = self.context.get('request')
        url = reverse('book-detail', args=[obj.pk], request=request)
        return url.replace('http://', 'https://') if request and request.is_secure() else url

# Define Publisher Serializer
class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metapublisher
        fields = ['publisherid','publishername']

# Define Bookauthor Serializer
class BookauthorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    books = serializers.SerializerMethodField()

    class Meta:
        model = Bookauthor
        fields = ['authorid', 'full_name','books']

    def get_full_name(self, obj):
        return f"{obj.firstname} {obj.lastname}"

    def get_books(self, obj):
        if hasattr(obj, 'book_set'):
            books = obj.book_set.all()
            return (book.title for book in books)


# Create specific genre serializers using the generic genre serializer
BookgenreSerializer = GenericGenreSerializer.create_for_model(Bookgenre)
