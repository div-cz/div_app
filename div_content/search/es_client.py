import os
from elasticsearch import Elasticsearch

def es():
    host = os.getenv("ELASTICSEARCH_HOST", "127.0.0.1")
    port = os.getenv("ELASTICSEARCH_PORT", "9200")
    user = os.getenv("ELASTICSEARCH_USER", "elastic")
    password = os.getenv("ELASTICSEARCH_PASSWORD", "h+UaViSXtI_LVz8rfFqh")

    url = f"https://{host}:{port}"
    return Elasticsearch(
        url,
        basic_auth=(user, password),
        request_timeout=30,
        retry_on_timeout=True,
        max_retries=5
    )
