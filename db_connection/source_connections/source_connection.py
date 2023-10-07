import os

import requests


class SourceConnection:
    def __init__(self, data_type: str):
        self.source_api_url = os.getenv('SOURCE_API_URL' + f'_{data_type}')
        # self.source_api_params = os.getenv('SOURCE_API_PARAMS' + f'_{data_type}')
        self.source_api_params = {
            'key': 'AIzaSyDlJ9E567Xdsxi1Vb-mYdc_yBQp6kD0-mo',
            'q': '*',  # Search for all books
            'orderBy': 'relevance',  # Order by relevance
            'printType': 'books',  # Only include actual books
            'maxResults': 10,  # Limit the number of results
        }

    def connect_to_source(self):
        response = requests.get(self.source_api_url,
                                self.source_api_params)
        print(response.status_code)
        return response

    def fetch_data(self):
        pass
