import gzip
from datetime import datetime, timedelta

import requests

from db_connection.source_connections.source_connection import SourceConnection


class SourceConnectionMovies(SourceConnection):
    def __init__(self):
        super().__init__(
            api_dict={
                    'api_url': 'https://api.themoviedb.org/3/movie/2',
                    'api_params': {
                        'api_key': 'c4efc14c22a10ea59174b7bf4f94310b',
                        'language': 'cs-CZ'
                    }
                })

    def get_new_records(self):
        new_records_ids = self.fetch_new_movies_ids()
        return []

    def fetch_new_movies_ids(self):
        date: datetime = datetime.now() - timedelta(days=1)
        ids_file_url: str = f'http://files.tmdb.org/p/exports/movie_ids_{date.month:02d}_{date.day:02d}_{date.year}.json.gz'
        response = requests.get(ids_file_url)
        if response.status_code == 200:
            compressed_file = BytesIO(response.content)
            with gzip.GzipFile(fileobj=compressed_file, mode='rb') as content:
                ids_file_unzipped: str = content.read().decode('utf-8')
            return ids_file_unzipped[0]
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return []
