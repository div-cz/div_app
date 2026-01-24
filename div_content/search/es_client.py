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
import os
from elasticsearch import Elasticsearch

def es():
    host = os.getenv("ELASTICSEARCH_HOST", "127.0.0.1")
    port = os.getenv("ELASTICSEARCH_PORT", "9200")
    user = os.getenv("ELASTICSEARCH_USER", "elastic")
    password = os.getenv("ELASTICSEARCH_PASSWORD", "6bS_UOy-JiuE3_fi689Y")
    ca_cert = os.getenv("ELASTICSEARCH_CA_CERT", "/var/www/div_app/http_ca.crt")

    url = f"https://{host}:{port}"

    # ✅ MAGIC
    if os.getenv("DOCKER_ENV") == "1":
        return Elasticsearch(
            url,
            basic_auth=(user, password),
            verify_certs=False,
            request_timeout=30,
            retry_on_timeout=True,
            max_retries=5
        )

    # ✅ PRODUKCE 
    return Elasticsearch(
        url,
        basic_auth=(user, password),
        ca_certs=ca_cert,
        request_timeout=30,
        retry_on_timeout=True,
        max_retries=5
    )
"""