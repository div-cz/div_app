def book_to_es_doc(book):
    """Vybere sloupce, které se budou indexovat v Elasticsearch."""
    return {
        "title": book.title or "",
        "titlecz": book.titlecz or "",
        "author": book.author or "",
        "authorid": book.authorid_id if book.authorid_id is not None else None,
    }
