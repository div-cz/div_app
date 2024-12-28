from typing import Union
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from div_content.models import Bookauthor
from ..others.helpers import get_unique_url

def verify_or_create_author(author_name:str) -> Union[int,JsonResponse]:
    """
    get author name and find ID from database or create new
    """
    try:
        author_parts = author_name.strip().split(' ')
        firstname = author_parts[0]
        lastname = author_parts[-1]
        middlename = ' '.join(author_parts[1:-1]) if len(author_parts) > 2 else ''
        if len(author_parts) < 2:
            firstname = lastname
        author = Bookauthor.objects.filter(
            firstname=firstname,
            middlename=middlename,
            lastname=lastname
        ).first()
        print(firstname,middlename,lastname)
        if author:
            return author.authorid
        else:
            unique_url = async_to_sync(get_unique_url)(author_name, 'BookAuthor', 'URL')
            author = Bookauthor.objects.create(
                firstname=firstname,
                middlename=middlename,
                lastname=lastname,
                url=unique_url
            )
            return author.authorid

    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Chyba pri zpracovani dat'}, status=500)
