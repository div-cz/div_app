from django.db.models import Prefetch
from div_content.models import Book, Bookauthor, Bookgenre, Bookwriters, Bookisbn, Metapublisher
from rest_framework import mixins
from .serializers import BookSerializer, BookListSerializer, BookauthorSerializer, PublisherSerializer
from ..views import BaseViewSet

class BookViewSet(BaseViewSet):
    queryset = Book.objects.all()

    def apply_select_related_and_prefetch_related(self, queryset):
        return queryset.prefetch_related(
            Prefetch('bookgenre_set', queryset=Bookgenre.objects.select_related('genreid')),
            Prefetch('bookwriters_set', queryset=Bookwriters.objects.select_related('author')),
            Prefetch('bookisbn_set', queryset=Bookisbn.objects.select_related('publisherid'))
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'view': self
        })
        return context

    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer

class BookAuthorViewSet(BaseViewSet):
    serializer_class = BookauthorSerializer
    queryset = Bookauthor.objects.all()
    # .prefetch_related(
    #     Prefetch('books', queryset=Book.objects.only('title'))
    # )
    search_fields = ['firstname', 'lastname']

    # def apply_select_related_and_prefetch_related(self, queryset):
    #     return queryset.prefetch_related(
    #         Prefetch('books', queryset=Book.objects.only('authorid'))
    #     )


class BookpublisherViewSet(BaseViewSet): # mixins.CreateModelMixin):
    queryset = Metapublisher.objects.all()
    serializer_class = PublisherSerializer
    search_fields = ['publishername']