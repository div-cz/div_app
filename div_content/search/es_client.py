import os
from elasticsearch import Elasticsearch

def es():
    host = os.getenv("ELASTICSEARCH_HOST", "magic_elastic")
    port = os.getenv("ELASTICSEARCH_PORT", "9200")
    password = os.getenv("ELASTICSEARCH_PASSWORD")

    return Elasticsearch(
        f"http://{host}:{port}",
        basic_auth=("elastic", password),
        request_timeout=30,
        max_retries=3,
        retry_on_timeout=True,
    )


""""
#FUNKCNI MVS

import os
from elasticsearch import Elasticsearch

def es():
    host = os.getenv("ELASTICSEARCH_HOST")
    port = os.getenv("ELASTICSEARCH_PORT", "9200")
    password = os.getenv("ELASTICSEARCH_PASSWORD")

    return Elasticsearch(
        f"http://{host}:{port}",
        basic_auth=("elastic", password),
    )
"""






"""
# FUNKČNÍ PROD
# -------------------------------------------------------------------
#                    SEARCH.ES_CLIENT
# -------------------------------------------------------------------
import os
from elasticsearch import Elasticsearch

_es_client = None  # ← DŮLEŽITÉ!

def es():
    global _es_client
    if _es_client:
        return _es_client
    
    host = os.getenv("ELASTICSEARCH_HOST", "127.0.0.1")
    port = os.getenv("ELASTICSEARCH_PORT", "9200")
    user = os.getenv("ELASTICSEARCH_USER", "elastic")
    password = os.getenv("ELASTICSEARCH_PASSWORD")
    ca_cert = os.getenv("ELASTICSEARCH_CA_CERT", "/var/www/div_app/http_ca.crt")
    
    if not password:
        raise ValueError("ELASTICSEARCH_PASSWORD environment variable is not set!")
    
    url = f"https://{host}:{port}"
    
    # ✅ MAGIC / Docker
    if os.getenv("DOCKER_ENV") == "1":
        _es_client = Elasticsearch(
            url,
            basic_auth=(user, password),
            verify_certs=False,
            request_timeout=30,
            retry_on_timeout=True,
            max_retries=5,
            max_retries_per_request=3,  # ← přidej
        )
    # ✅ PRODUKCE
    else:
        _es_client = Elasticsearch(
            url,
            basic_auth=(user, password),
            ca_certs=ca_cert,
            verify_certs=True,
            request_timeout=30,
            retry_on_timeout=True,
            max_retries=5,
            max_retries_per_request=3,  # ← přidej
        )
    
    return _es_client
"""