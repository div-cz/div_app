from pyspark.sql import SparkSession, DataFrame

from db_connection.source_connections.source_connection import SourceConnection
from db_connection.target_connections.target_connection import TargetConnection


class DataHandler:
    def __init__(self, resource_name: str):
        self.source_connection = SourceConnectionFactory(resource_name)
        self.target_connection = TargetConnectionFactory()
        self.target_table_name: str = resource_name
        self.data_from_source = self.source_connection.fetch_data()
        self.data_from_target = self.target_connection.load_data_from_db(self.target_table_name)

    def get_max_id(self):
        if self.data_from_target and f'{self.target_table_name}ID' in self.data_from_target.columns:
            return self.data_from_target[f'{self.data_from_target}ID'].max()
        else:
            return 1

    def create_new_data_df(self):
        max_id = self.get_max_id()
        data_to_add = []
        for item in self.data_from_source.get('items', []):
            if 'id' in item and 'volumeInfo' in item:
                max_id += 1
                data_to_add.append({
                    'BookID': max_id,
                    'Title': item.get('volumeInfo', {}).get('title', ''),
                    'Author': ", ".join(item.get('volumeInfo', {}).get('authors', [])),
                    'Description': item.get('volumeInfo', {}).get('description', ''),
                    'CountryID': 0,
                    'GenreID': 0,
                    'PublisherID': 0,
                    'WorldID': 0,
                    'GoogleID': item['id']
                })
        return data_to_add