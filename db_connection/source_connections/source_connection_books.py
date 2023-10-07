from db_connection.source_connections.source_connection import SourceConnection


class SourceConnectionBooks(SourceConnection):
    def __init__(self):
        super().__init__(data_type='Book')

    def fetch_book_ids(self):
        response = self.connect_to_source()
        if response.status_code == 200:
            books_data = response.json()
            book_ids = [item['id'] for item in books_data.get('items', [])]
            return book_ids
        else:
            print(f"Failed to retrieve books: {response.status_code}")
            return []
