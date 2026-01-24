import requests
import json
import time
from asgiref.sync import async_to_sync
from concurrent.futures import ThreadPoolExecutor
from django.db import transaction
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from typing import Callable
from div_content.models import Book, Bookauthor, Metagenre, Bookwriters, Bookisbn, Bookgenre, Metapublisher
from ..book_authors.author_verify import verify_or_create_author
from ..others.helpers import get_unique_url,clean_character_name_sync
from ..others.proces_image import process_image

def superuser_required(view_func:Callable[...,HttpRequest]) -> Callable[...,HttpResponse]:
    #@login_required(login_url='/prihlaseni/')
    #@user_passes_test(lambda u: u.is_superuser or u.is_staff)
    def _wrapped_view(request:HttpRequest, *args, **kwargs):
        return view_func(request, *args, **kwargs)  # Přeposíláme args a kwargs správně
    return _wrapped_view

@superuser_required
def fetch_book_details(request: HttpRequest) -> JsonResponse:
    """
    get book details from google books api
    """
    start_time = time.time()

    isbn = request.GET.get('isbn')
    if isbn:
        url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key=AIzaSyDlJ9E567Xdsxi1Vb-mYdc_yBQp6kD0-mo'

        with ThreadPoolExecutor() as executor:
            future_google_books = executor.submit(requests.get, url)

            # Zpracování Google Books API response
            response_google_books = future_google_books.result()

            if response_google_books.status_code == 200:
                data = response_google_books.json()

                if 'items' in data:
                    book_info = data['items'][0]['volumeInfo']
                    book_details = {
                        'title': book_info.get('title'),
                        'author': book_info.get('authors', [])[0],
                        'year': book_info.get('publishedDate', '')[:4],
                        'pages': book_info.get('pageCount'),
                        'subtitle': book_info.get('subtitle', ''),
                        'description': book_info.get('description'),
                        'language': book_info.get('language'),
                        'googleid': data['items'][0].get('id')
                    }
                    # Fetch ISBNs
                    isbn_time = time.time()

                    book_details['isbns'] = [
                        {'identifier': identifier['identifier'], 'type': identifier['type']}
                        for identifier in book_info.get('industryIdentifiers', [])
                    ]
                    # Fetch genres from Google Books API and map to Metagenre IDs
                    genre_time = time.time()
                    google_genres = book_info.get('categories', [])
                    book_details['genres'] = []
                    for genre in google_genres:
                        try:
                            genre_obj = Metagenre.objects.get(genrename=genre)
                            book_details['genres'].append({'id': genre_obj.genreid, 'name': genre_obj.genrename})
                        except Metagenre.DoesNotExist:
                            pass

                    # Directly access the database for publisher
                    publisher_time = time.time()
                    publisher_name = book_info.get('publisher', '')
                    if publisher_name:
                        try:
                            publisher_obj = Metapublisher.objects.get(publishername=publisher_name)
                            book_details['publisher'] = {
                                'id': publisher_obj.publisherid,
                                'name': publisher_obj.publishername
                            }
                        except Bookpublisher.DoesNotExist:
                            print(f"Publisher not found: {publisher_name}")
                            book_details['publisher'] = None


                    total_time = time.time() - start_time
                    return JsonResponse(book_details)
            if response_google_books.status_code == 429:
                return JsonResponse({'error': "Já za to nemuzu, to GOOGLE ! "}, status=429)
    return JsonResponse({})
@superuser_required
@transaction.atomic
def add_book(request: HttpRequest) -> JsonResponse:
    """
    fuction for add book at book isbn/manual tab
    """
    if request.method == 'POST':
        print(request.POST)
        title = request.POST.get('title')
        author_name = request.POST.get('author')
        year = request.POST.get('year',None)
        pages = request.POST.get('pages')
        subtitle = request.POST.get('subtitle')
        description = request.POST.get('description')
        language = request.POST.get('language')
        googleid = request.POST.get('googleid')
        genres = request.POST.getlist('genres')
        publisherid = request.POST.get('publisherid')
        # Zjistíme, který z klíčů je v request.POST přítomen
        if 'manual-img-option' in request.POST:
            img_option = request.POST.get('manual-img-option', 'no-img')
        elif 'isbn-img-option' in request.POST:
            img_option = request.POST.get('isbn-img-option', 'no-img')

        if not title or not author_name:
            return JsonResponse({'error': 'Chybí povinná pole. Název knihy a Jméno autora'}, status=400)

        img_filename = 'noimg.png'  # Defaultní hodnota

        # Zpracování obrázku na základě vybrané možnosti
        if img_option == 'google-id':
            img_filename = googleid
        elif img_option == 'upload-img':
            # Pokud se nahrává vlastní obrázek, zpracujeme ho
            if 'img' in request.FILES:
                image_file = request.FILES['img']
                book_author = clean_character_name_sync(author_name)
                book_title = clean_character_name_sync(title)
                img_filename = process_image(image_file,book_author,book_title)  # Funkce pro zpracování obrázku
            else:
                return JsonResponse({'error': 'No image file provided'}, status=400)

        # Zpracování ISBNs
        isbns = request.POST.getlist('isbns')  # Očekáváme list řetězců JSON objektů
        isbns = [json.loads(isbn) for isbn in isbns]  # Převedeme je na list slovníků
        # Call your async functions here to get the URL
        unique_url = async_to_sync(get_unique_url)(title, 'Book', 'URL', year)

        try:
            with transaction.atomic():
                authorid = verify_or_create_author(author_name)
                print(authorid)
                # Create book
                book = Book.objects.create(
                    title=title,
                    author=author_name,
                    year=year if year else None,
                    pages=pages if pages else None,
                    subtitle=subtitle if subtitle else '',
                    description=description if description else '',
                    language=language if language else None,
                    img=img_filename,
                    googleid=googleid if googleid else '',
                    url=unique_url,
                    authorid=Bookauthor.objects.get(authorid=authorid),
                )
                # Log and add genres
                for genre_id in genres:
                    print(f"Adding genre ID: {genre_id} to book ID: {book.bookid}")
                    genre = Metagenre.objects.get(genreid=genre_id)
                    Bookgenre.objects.create(bookid=book, genreid=genre)

                # Log and add ISBNs
                for isbn_data in isbns:
                    if isbn_data['identifier']:
                        print(
                            f"Adding ISBN: {isbn_data['identifier']} of type {isbn_data['type']} to book ID: {book.bookid}")
                        Bookisbn.objects.create(
                            isbn=isbn_data['identifier'],
                            ISBNtype=isbn_data['type'],
                            book=book,
                            publisherid=Bookpublisher.objects.get(publisherid=publisherid) if publisherid else None
                        )

                # Log and add relationship to Bookwriters
                Bookwriters.objects.create(
                    book=book,
                    author=Bookauthor.objects.get(authorid=authorid)
                )

                # Namísto přesměrování vracíme JSON odpověď7
                return JsonResponse({'message': 'Book successfully added', 'book_id': book.bookid})

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return JsonResponse(
                {'error': 'An error occurred while adding the book. Please check the server logs for more details.'},
                status=500)

    return render(request, 'books/add_book.html')

@superuser_required
def get_book_details(request:HttpRequest, book_id:int)  -> JsonResponse:
    """
    gather book details for update book tab
    """
    print("gdfsgsd")
    try:
        book = Book.objects.prefetch_related('bookgenre_set', 'bookisbn_set', 'bookwriters_set').get(bookid=book_id)
        genres = [bg.genreid for bg in book.bookgenre_set.all()]
        isbns = [bisbn for bisbn in book.bookisbn_set.all()]
        writers = [bw for bw in book.bookwriters_set.all()]
        data = {
            'book':book_id,
            'title': book.title,
            'author': " ".join(filter(None, [book.authorid.firstname, book.authorid.middlename, book.authorid.lastname])),
            'year': book.year,
            'pages': book.pages,
            'subtitle': book.subtitle,
            'description': book.description,
            'language': book.language,
            'img': book.img,
            'googleid': book.googleid,

           'genres': [{"id":genre.genreid,
                       "name":genre.genrenamecz}
                       for genre in genres],  # Získání všech žánrů

           'isbn': [{"isbn":isbn.isbn,
                     "isbntype":isbn.ISBNtype,
                     "publisher":isbn.publisherid.publishername if isbn.publisherid else "" ,
                     "publisherid": isbn.publisherid_id if isbn.publisherid else None} for isbn in isbns ],

            'writers': [
                        {
                            "id": writer.author.authorid,
                            "name": " ".join(filter(None, [writer.author.firstname, writer.author.middlename, writer.author.lastname]))
                        }
                        for writer in writers
                        ],
                }
        return JsonResponse(data)
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)


def update_book(request):
    return render(request, "books/update_book.html")

@superuser_required
@transaction.atomic
def update_book_details(request: HttpRequest, book_id:int)  -> JsonResponse:
    """
    function for update book tab
    """
    try:
        book = Book.objects.get(bookid=book_id)
        original_title = book.title

        # 1. Aktualizace základních informací o knize
        book.title = request.POST.get('title', book.title)
        book.author = request.POST.get('author', book.author)  # Uložení hlavního autora
        authorid = verify_or_create_author(book.author)
        book.authorid = Bookauthor.objects.get(authorid=authorid)
        book.description = request.POST.get('description', book.description)
        book.year = request.POST.get('year', None)
        book.pages = request.POST.get('pages', None)
        book.subtitle = request.POST.get('subtitle', book.subtitle)
        book.language = request.POST.get('language', book.language)
        book.googleid = request.POST.get('googleid', book.googleid)

        if original_title != book.title:
            book.url = async_to_sync(get_unique_url)(book.title, 'Book', 'URL', book.year)

        # 2. Zpracování obrázku
        img_option = request.POST.get('update-img-option', 'no-img')
        img = request.FILES.get('img')  # Pokud byl nahrán soubor
        img_value = request.POST.get('img')  # Pokud je to Google ID nebo 'noimg.png'

        if img_option == 'upload-img' and img:
            # Zpracujeme nahraný obrázek
            book_author = clean_character_name_sync(book.author)
            book_title = clean_character_name_sync(book.title)
            img_filename = process_image(img, book_author, book_title)
            book.img = img_filename
        elif img_option == 'google-id' and img_value:
            # Uložíme Google ID jako obrázek
            book.img = img_value
        elif img_option == 'no-img':
            # Nastavíme výchozí obrázek
            if not book.img:
                book.img = 'noimg.png'
        else:
            # Pokud uživatel nezměnil obrázek, ponecháme původní
            pass

        # 3. Zpracování ISBNs a publisher
        existing_isbns = {isbn.isbn: isbn for isbn in book.bookisbn_set.all()}
        new_isbns = {}
        isbns = request.POST.getlist('isbns')
        for isbn_json in isbns:
            isbn_data = json.loads(isbn_json)
            isbn_value = isbn_data['identifier']
            isbn_type = isbn_data['type']
            new_isbns[isbn_value] = {'isbntype': isbn_type}

        if existing_isbns or new_isbns:  # Smazání neexistujících ISBN
            for isbn_value in set(existing_isbns) - set(new_isbns):
                existing_isbns[isbn_value].delete()

            for isbn_value, isbn_data in new_isbns.items():
                publisher_id = request.POST.get('publisherid')
                if not publisher_id or publisher_id == 'null':
                    publisher_id = None  # Nastavit na None, pokud není zadán
                if isbn_value in existing_isbns:
                    isbn_record = existing_isbns[isbn_value]
                    isbn_record.ISBNtype = isbn_data['isbntype']
                    isbn_record.publisherid_id = publisher_id
                    isbn_record.save()
                else:
                    new_isbn_record = Bookisbn(
                        isbn=isbn_value,
                        ISBNtype=isbn_data['isbntype'],
                        publisherid_id=publisher_id,
                        book=book
                    )
                    new_isbn_record.save()

        # 4. Zpracování žánrů
        existing_genres = set(book.bookgenre_set.values_list('genreid', flat=True))
        new_genres = set(request.POST.getlist('genres'))

        for genre_id in existing_genres - new_genres:
            Bookgenre.objects.filter(bookid=book_id, genreid=genre_id).delete()

        for genre_id in new_genres - existing_genres:
            Bookgenre.objects.create(bookid=book, genreid_id=genre_id)

        # 5. Zpracování autorů (vyjma hlavního autora)
        existing_authors = set(book.bookwriters_set.values_list('author_id', flat=True))
        new_authors = set(int(author_id) for author_id in request.POST.getlist('authors') if int(author_id) != book.authorid_id)

        # Smazání neexistujících autorů
        #for author_id in existing_authors - new_authors:
         #   Bookwriters.objects.filter(book=book, author_id=author_id).delete()

        # Přidání nových autorů
        for author_id in new_authors - existing_authors:
            Bookwriters.objects.create(book=book, author_id=author_id)
        # Uložení knihy
        book.save()
        return JsonResponse({'success': True})

    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
