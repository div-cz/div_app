from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from div_content.search.es_client import es

INDEX_NAME = "books"

class Command(BaseCommand):
    help = "Create Elasticsearch index for books (simple mapping)"

    def handle(self, *args, **kwargs):
        client: Elasticsearch = es()

        if client.indices.exists(index=INDEX_NAME):
            self.stdout.write(f"Index '{INDEX_NAME}' už existuje.")
            return

        body = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "cs_simple": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "asciifolding"]
                        }
                    },
                    "normalizer": {
                        "kw_norm": {
                            "type": "custom",
                            "filter": ["lowercase", "asciifolding"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "title":      {"type": "text", "analyzer": "cs_simple"},
                    "titlecz":    {"type": "text", "analyzer": "cs_simple"},
                    "author":     {"type": "text", "analyzer": "cs_simple"},
                    "authorid":   {"type": "integer"},
                }
            }
        }

        client.indices.create(index=INDEX_NAME, body=body)
        self.stdout.write(self.style.SUCCESS(f"Vytvořen index '{INDEX_NAME}'."))
