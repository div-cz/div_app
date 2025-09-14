from django.core.management.base import BaseCommand
from elasticsearch.helpers import bulk
from div_content.search.es_client import es
from div_content.models import Book
from div_content.search.serializers import book_to_es_doc

INDEX_NAME = "books"

class Command(BaseCommand):
    help = "Reindex all Book rows into Elasticsearch"

    def handle(self, *args, **kwargs):
        client = es()

        def actions():
            for b in Book.objects.all().iterator():
                yield {
                    "_op_type": "index",
                    "_index": INDEX_NAME,
                    "_id": str(b.bookid),
                    "_source": book_to_es_doc(b),
                }

        bulk(client, actions(), chunk_size=1000)
        self.stdout.write(self.style.SUCCESS("Reindex hotový."))
