import os
from elasticsearch import Elasticsearch

def es():
    host = os.getenv("ELASTICSEARCH_HOST", "127.0.0.1")
    port = os.getenv("ELASTICSEARCH_PORT", "9200")
    user = os.getenv("ELASTICSEARCH_USER", "elastic")
    password = os.getenv("ELASTICSEARCH_PASSWORD", "6bS_UOy-JiuE3_fi689Y")
    ca_cert = os.getenv("ELASTICSEARCH_CA_CERT", "/var/www/div_app/http_ca.crt")

    url = f"https://{host}:{port}"
    return Elasticsearch(
        url,
        basic_auth=(user, password),
        ca_certs=ca_cert,
        request_timeout=30,
        retry_on_timeout=True,
        max_retries=5
    )


#/etc/elasticsearch/certs/http_ca.crt


#sudo curl --cacert /etc/elasticsearch/certs/http_ca.crt -u elastic:NOVE_HESLO https://localhost:9200/
