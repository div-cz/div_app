# -------------------------------------------------------------------
#                    VIEWS.ADMINS.PY
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    OBSAH
# -------------------------------------------------------------------
# ### poznámky a todo
# ### importy
# ### konstanty
# ### funkce
# 
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    POZNÁMKY A TODO
# -------------------------------------------------------------------
# Poznámky a todo
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    IMPORTY 
# -------------------------------------------------------------------
# (tři skupiny - každá zvlášt abecedně)
# 1) systémové (abecedně)
# 2) interní (forms,models,views) (abecedně)
# 3) third-part (třetí strana, django, auth) (abecedně)
# -------------------------------------------------------------------
import datetime
import json
import os
import re
import requests

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from django.shortcuts import render, redirect, get_object_or_404

from div_content.forms.admins import Moviecommentform, TaskForm, TaskCommentForm

from div_content.models import AATask, Book, Bookisbn, Bookpurchase, Moviecomments
from div_content.utils.functions import normalize_isbn, format_isbn
from div_content.utils.palmknihy import get_catalog_product, get_all_palmknihy_products, get_product_by_id

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt



# -------------------------------------------------------------------
# F:                 ADMIN INDEX
# -------------------------------------------------------------------
# Kontrola pro superadminy
"""
def is_superadmin(user):
    return user.username in ["xsilence8x", "VendaCiki", "Martin2", "Ionno"]

@user_passes_test(is_superadmin)"""
def admin_index(request):
    if request.method == 'POST':
        selected_comments = request.POST.getlist('selected_comments')
        if 'delete' in request.POST:
            Moviecomments.objects.filter(commentid__in=selected_comments).delete()
            return redirect('admin_index')
    # Načteme posledních deset komentářů
    comments = Moviecomments.objects.select_related('movieid', 'user').order_by('-dateadded')[:5]
    return render(request, 'admin/admin_index.html', {'comments': comments})


# -------------------------------------------------------------------
# F:                 ADMIN ODPRIRADIT EKNIHU
# -------------------------------------------------------------------
@csrf_exempt
@require_POST
def admin_odpriradit_eknihu(request):
    isbn = request.POST.get("isbn")
    palmknihyid = request.POST.get("palmknihyid")
    page = request.POST.get("page", "1") 
    anchor = request.POST.get("isbn_anchor", "")


    if palmknihyid:
        # Odeber vazbu na všechny formáty této eknihy z Palmknih
        Bookisbn.objects.filter(palmknihyid=palmknihyid).update(book=1)
    elif isbn:
        # Fallback: odeber jen podle ISBN (starý způsob, fallback pro nouzi)
        Bookisbn.objects.filter(isbn=isbn).update(book=1)
    print("odebírám palmknihyid:", palmknihyid, "isbn:", isbn)
    return redirect(request.META.get("HTTP_REFERER", f"/spravce/eknihy-prehled/?page={page}#{anchor or ''}"))




# -------------------------------------------------------------------
# F:                 AJAX SEARCH BOOKS
# -------------------------------------------------------------------
@require_GET
def ajax_search_books(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"results": []})

    # Hledej podle titlecz nebo title
    matches = Book.objects.filter(titlecz__icontains=query)[:10]
    results = [
        {"id": book.bookid, 
        "text": f"{book.titlecz or book.title} ({book.author})",
        "img": book.img}
        for book in matches
    ]
    return JsonResponse({"results": results})


# -------------------------------------------------------------------
# F:                 ADMIN ASSIGN BOOK
# -------------------------------------------------------------------
@csrf_exempt
def admin_assign_book(request):
    if request.method == "POST":
        data = json.loads(request.body)
        book_id = data.get("bookid")
        palmknihy_id = data.get("palmknihyid")

        if not book_id or not palmknihy_id:
            return JsonResponse({"status": "error", "message": "Chybí bookid nebo palmknihyid."})

        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Kniha nenalezena."})

        # Páruj ke všem záznamům s tímto palmknihyid (bez ohledu na typ/format)
        qs = Bookisbn.objects.filter(palmknihyid=palmknihy_id)
        if not qs.exists():
            return JsonResponse({"status": "error", "message": "Nebylo nalezeno žádné ISBN k tomuto PalmknihyID. Ulož nejprve záznam/y!"})
        qs.update(book=book)

        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error", "message": "Jen POST."})

'''
@csrf_exempt
def admin_assign_book(request):
    if request.method == "POST":
        data = json.loads(request.body)
        book_id = data.get("bookid")
        palmknihy_id = data.get("palmknihyid")

        if not book_id or not palmknihy_id:
            return JsonResponse({"status": "error", "message": "Chybí bookid nebo palmknihyid."})

        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Kniha nenalezena."})

        isbns_with_palm = Bookisbn.objects.filter(palmknihyid=palmknihy_id)
        if isbns_with_palm.exists():
            isbn = isbns_with_palm.first().isbn
            # Aktualizuj všechny záznamy se stejným isbn (i staré PRINT)
            Bookisbn.objects.filter(isbn=isbn).update(book=book, palmknihyid=palmknihy_id)
        else:
            # Hledej podle PRINT ISBN (starý záznam bez palmknihyid) a doplň palmknihyid + book
            # Můžeš doplnit palmknihyid pro všechny formáty, pokud mají stejné ISBN
            isbn = request.POST.get("isbn") or data.get("isbn")
            if isbn:
                Bookisbn.objects.filter(isbn=isbn).update(book=book, palmknihyid=palmknihy_id)
            else:
                # fallback – nepodařilo se najít ISBN
                return JsonResponse({"status": "error", "message": "Nepodařilo se najít ISBN."})

        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error", "message": "Jen POST."})
'''




# -------------------------------------------------------------------
# F:                 ADMIN COMMENTS
# -------------------------------------------------------------------
#@user_passes_test(is_superadmin)
def admin_comments(request):
    if request.method == 'POST':
        selected_comments = request.POST.getlist('selected_comments')
        if 'delete' in request.POST and selected_comments:
            deleted_count, _ = Moviecomments.objects.filter(commentid__in=selected_comments).delete()
            messages.success(request, f'Smazáno {deleted_count} komentářů.')
            return redirect('admin_comments')
    # Načteme posledních 50 komentářů
    comments100 = Moviecomments.objects.select_related('movieid', 'user').order_by('-dateadded')[:50]
    return render(request, 'admin/admin_comments.html', {'comments100': comments100})



# -------------------------------------------------------------------
# F:                 ADMIN EDIT COMMENT
# -------------------------------------------------------------------
"""@user_passes_test(is_superadmin)"""
def admin_edit_comment(request, commentid):
    comment = get_object_or_404(Moviecomments, pk=commentid)
    if request.method == 'POST':
        form = Moviecommentform(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('admin_index')
    else:
        form = Moviecommentform(instance=comment)
    
    return render(request, 'admin/admin_edit_comment.html', {'form': form, 'comment': comment})



# -------------------------------------------------------------------
# F:                 ADMIN TASKS
# -------------------------------------------------------------------
@login_required
def admin_tasks(request):
    tasks = AATask.objects.filter(parentid__isnull=True).order_by('-created')
    return render(request, 'admin/admin_tasks.html', {
        'tasks': tasks
    })


# -------------------------------------------------------------------
# F:                 ADMIN TASK DETAIL
# -------------------------------------------------------------------
@login_required
def admin_task_detail(request, task_id):
    task = get_object_or_404(AATask, id=task_id)
    
    if request.method == "POST":
        comment_form = TaskCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.cleaned_data['comment']
            # Přidáme nový komentář k existujícím
            new_comments = f"{task.comments or ''}\n\n{request.user.username} ({timezone.now().strftime('%d.%m.%Y %H:%M')}):\n{comment}"
            task.comments = new_comments
            task.save()
            messages.success(request, 'Komentář byl přidán')
            return redirect('admin_task_detail', task_id=task.id)
    else:
        comment_form = TaskCommentForm()

    return render(request, 'admin/admin_task_detail.html', {
        'task': task,
        'comment_form': comment_form
    })

@login_required
def admin_task_edit(request, task_id=None):
    if task_id:
        task = get_object_or_404(AATask, id=task_id)
    else:
        task = None

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            if not task_id:
                task.Creator = request.user.username
                task.IPaddress = request.META.get('REMOTE_ADDR')
            task.save()
            messages.success(request, 'Úkol byl uložen')
            return redirect('admin_task_detail', task_id=task.id)
    else:
        form = TaskForm(instance=task)

    return render(request, 'admin/admin_task_edit.html', {
        'form': form,
        'task': task
    })


# -------------------------------------------------------------------
# F:                 RECENT PAYMENTS
# -------------------------------------------------------------------
def recent_payments(request):
    payments = Bookpurchase.objects.filter(status="PAID").order_by("-paymentdate")[:50]

    if not request.user.is_superuser:
        raise Http404("Nepovolený přístup.")

    token = os.getenv("FIO_TOKEN")
    today = datetime.date.today()
    ninety_days_ago = today - datetime.timedelta(days=90)
    from_date = ninety_days_ago.strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    url = f"https://fioapi.fio.cz/v1/rest/periods/{token}/{from_date}/{to_date}/transactions.json"
    response = requests.get(url, timeout=10)
    fio_status = response.status_code
    fio_text = response.text[:1000]

    try:
        data = response.json()
    except Exception:
        data = None

    fio_raw = repr(data) if data else ""
    credits = []
    if data:
        transactions = data.get("accountStatement", {}).get("transactionList", {}).get("transaction", [])
        for tx in transactions:
            try:
                amount = float(str(tx.get("column1", {}).get("value", "0")).replace(",", "."))
                if amount > 0:
                    credits.append(tx)
            except Exception:
                pass
    else:
        credits = []

    return render(request, "admin/payments.html", {
        "transactions": credits,
        "fio_url": url,
        "fio_status": fio_status,
        "fio_text": fio_text,
        "fio_token": token,
        "fio_raw": fio_raw,
        "payments": payments,
    })


# -------------------------------------------------------------------
# F:                 ADMIN PALMKNIHY PREVIEW
# -------------------------------------------------------------------
def admin_palmknihy_preview(request):
    page = int(request.GET.get("page", 1))
    raw_books = get_catalog_product(limit=50, page=page)

    existing_isbns = set(normalize_isbn(i) for i in Bookisbn.objects.values_list("isbn", flat=True))
    unknown_book = Book.objects.get(pk=1)

    ebooks = []

    for book in raw_books:
        title = book.get("title", "-")
        price_data = book.get("current_valid_price") or {}
        price_value = price_data.get("price") or price_data.get("retail_price")
        if price_value is None:
            price_value = price_data.get("retail_price")
        
        if price_value == 0:
            price_str = "Zdarma"
        elif price_value is not None:
            price_str = f"{price_value} Kč"
        else:
            price_str = "-"


        author_name = "Neznámý autor"  # protože authors nemá name
        if book.get("publisher", {}).get("name"):
            author_name = book["publisher"]["name"]
        elif book.get("distributions"):
            author_name = book["distributions"][0].get("distributor_name", "Neznámý autor")


        isbn_parts = []
        for fmt in ["epub", "mobi", "pdf"]:
            field = f"spec_isbn-{fmt}"
            if field in book and book[field]:
                isbn_parts.append(f"{book[field]} ({fmt.upper()})")

        # fallback: hlavní ISBN, pokud není žádný formát
        if not isbn_parts and book.get("isbn"):
            isbn_parts.append(book["isbn"])

        book["raw"] = json.dumps(book, ensure_ascii=False)  # NE indent, NE ascii  # pro popup

        formats = []
        for fmt in ["epub", "mobi", "pdf"]:
            isbn = normalize_isbn(book.get(f"spec_isbn-{fmt}"))
            palmknihyid = None
            dist_price = None
            db_price = None
            if isbn:
                # Cena z API/distribuce
                for dist in book.get("distributions", []):
                    if isbn == dist.get("isbn"):
                        dist_price = dist.get("price") or dist.get("retail_price")
                        break
        
                # Cena z DB
                try:
                    rec = Bookisbn.objects.get(isbn=isbn)
                    palmknihyid = rec.palmknihyid
                    db_price = rec.price
                except Bookisbn.DoesNotExist:
                    palmknihyid = None
                    db_price = None
        
                formats.append({
                    "format": fmt.upper(),
                    "isbn": format_isbn(isbn),
                    "exists": isbn in existing_isbns,
                    "price": dist_price,      # <<<<<< Cena z API
                    "db_price": db_price,     # <<<<<< Cena z DB
                    "palmknihyid": palmknihyid,
                })


        if not formats and book.get("isbn"):
            isbn_clean = normalize_isbn(book.get("isbn"))
            palmknihyid = None
            db_price = None
            try:
                rec = Bookisbn.objects.get(isbn=isbn_clean)
                palmknihyid = rec.palmknihyid
                db_price = rec.price
            except Bookisbn.DoesNotExist:
                palmknihyid = None
                db_price = None
        
            formats.append({
                "format": "PRINT",
                "isbn": format_isbn(isbn_clean),
                "exists": isbn_clean in existing_isbns,
                "price": None,
                "db_price": db_price,
                "palmknihyid": palmknihyid,
            })



        main_isbn_clean = normalize_isbn(book.get("isbn"))
        main_in_db = None
        main_has_palmknihyid = None
        if main_isbn_clean:
            try:
                rec = Bookisbn.objects.get(isbn=main_isbn_clean)
                main_in_db = True
                main_has_palmknihyid = bool(rec.palmknihyid)
            except Bookisbn.DoesNotExist:
                main_in_db = False
                main_has_palmknihyid = False


        ebooks.append({
            "title": title,
            "author": author_name,
            "format": ", ".join(fmt.upper() for fmt in ["epub", "mobi", "pdf"] if book.get(f"spec_isbn-{fmt}")),
            "price": price_str,
            "price_raw": price_value,
            "main_isbn": format_isbn(book.get("isbn", "-")) if book.get("isbn") else "",
            "isbn_list": ", ".join(
                f"{f['isbn']} ({f['format']}, {f['price']} Kč)" if f["price"] else f"{f['isbn']} ({f['format']})"
                for f in formats
            ),
            "raw": book["raw"],
            "palmknihyid": book.get("id"),
            "formats": formats,
            "main_has_palmknihyid": main_has_palmknihyid,
        })

    for book in ebooks:
        # Získej normalizované ISBN pro párování (odeber pomlčky, mezery)
        isbn_main = normalize_isbn(book.get("main_isbn") or "")
        book["isbn_normalized"] = isbn_main
        if isbn_main:
            isbns = Bookisbn.objects.filter(isbn=isbn_main).exclude(book_id=1)
        else:
            isbns = Bookisbn.objects.none()
        if isbns.exists():
            assigned = isbns.first()
            assigned_book = assigned.book
            book["bookid"] = assigned_book.bookid
            book["book_url"] = assigned_book.url
            book["book_titlecz"] = assigned_book.titlecz or assigned_book.title
            book["book_format"] = assigned.format
            book["has_palmknihyid"] = bool(assigned.palmknihyid)
            book["book_author"] = assigned_book.author  

        else:
            # Nové: když není PRINT, zkus podle palmknihyid
            palmknihyid_api = book.get("palmknihyid")
            isbns_by_pkid = Bookisbn.objects.filter(palmknihyid=palmknihyid_api).exclude(book_id=1)
            if isbns_by_pkid.exists():
                assigned = isbns_by_pkid.first()
                assigned_book = assigned.book
                book["bookid"] = assigned_book.bookid
                book["book_url"] = assigned_book.url
                book["book_titlecz"] = assigned_book.titlecz or assigned_book.title
                book["book_format"] = assigned.format
                book["has_palmknihyid"] = bool(assigned.palmknihyid)
                book["book_author"] = assigned_book.author
            else:
                book["bookid"] = None
                book["book_url"] = ""
                book["book_titlecz"] = ""
                book["book_format"] = ""
                book["has_palmknihyid"] = False



    return render(request, "admin/palmknihy_preview.html", {
        "ebooks": ebooks,
        "page": page
    })


# -------------------------------------------------------------------
# F:                 ADMIN STORE EBOOK
# -------------------------------------------------------------------
@csrf_exempt
def admin_store_ebook(request):
    if request.method == "POST":
        palmknihyid = request.POST.get("palmknihyid")
        if not palmknihyid:
            return redirect("admin_palmknihy_preview")

        response = get_product_by_id(palmknihyid)
        if not response or "data" not in response:
            return redirect("admin_palmknihy_preview")

        book_data = response["data"]
        unknown_book = Book.objects.get(pk=1)

        # Ulož hlavní ISBN jako PRINT (i když nejsou žádné formáty)
        isbn_main = normalize_isbn(book_data.get("isbn"))
        if isbn_main:
            # Opravíme existující "sirotek" PRINT záznam (book=1 a/nebo palmknihyid is NULL)
            Bookisbn.objects.filter(
                isbn=isbn_main
            ).filter(
                book=1
            ).update(
                palmknihyid=palmknihyid,
                format="PRINT",
                language=book_data.get("language", "cs"),
                description=book_data.get("description", "")[:500]
            )
        # Pokud neexistuje vůbec žádný, teprve vytvoř!
        if not Bookisbn.objects.filter(isbn=isbn_main).exists():
            Bookisbn.objects.create(
                book=unknown_book,
                isbn=isbn_main,
                format="PRINT",
                language=book_data.get("language", "cs"),
                price=None,
                description=book_data.get("description", "")[:500],
                palmknihyid=palmknihyid,
                ISBNtype="PALM"
            )

        # Ulož formáty EPUB, MOBI, PDF
        for fmt in ["epub", "mobi", "pdf"]:
            isbn = normalize_isbn(book_data.get(f"spec_isbn-{fmt}"))
            if isbn and not Bookisbn.objects.filter(isbn=isbn).exists():
                Bookisbn.objects.create(
                    book=unknown_book,
                    isbn=isbn,
                    format=fmt.upper(),
                    language=book_data.get("language", "cs"),
                    price=book_data.get("current_valid_price", {}).get("price"),
                    description=book_data.get("description", "")[:500],
                    palmknihyid=palmknihyid,
                    ISBNtype="PALM"
                )

    return redirect("admin_palmknihy_preview")





# -------------------------------------------------------------------
# F:                 ADMIN STORE EBOOK
# -------------------------------------------------------------------
@csrf_exempt
def admin_store_ebook(request):
    if request.method == "POST":
        palmknihyid = request.POST.get("palmknihyid")
        if not palmknihyid:
            return redirect("admin_palmknihy_preview")

        response = get_product_by_id(palmknihyid)
        if not response or "data" not in response:
            return redirect("admin_palmknihy_preview")

        book_data = response["data"]
        unknown_book = Book.objects.get(pk=1)

        # Ulož PRINT (hlavní), pouze pokud ISBN existuje
        isbn_main = normalize_isbn(book_data.get("isbn"))
        if isbn_main:
            Bookisbn.objects.update_or_create(
                isbn=isbn_main,
                defaults={
                    "book": unknown_book,
                    "format": "PRINT",
                    "language": book_data.get("language", "cs"),
                    "price": None,
                    "description": book_data.get("description", "")[:500],
                    "palmknihyid": palmknihyid,
                    "ISBNtype": "PALM"
                }
            )

        # Ulož formáty EPUB, MOBI, PDF (každý jen pokud ISBN je)
        for fmt in ["epub", "mobi", "pdf"]:
            isbn = normalize_isbn(book_data.get(f"spec_isbn-{fmt}"))
            if isbn:
                Bookisbn.objects.update_or_create(
                    isbn=isbn,
                    defaults={
                        "book": unknown_book,
                        "format": fmt.upper(),
                        "language": book_data.get("language", "cs"),
                        "price": book_data.get("current_valid_price", {}).get("price"),
                        "description": book_data.get("description", "")[:500],
                        "palmknihyid": palmknihyid,
                        "ISBNtype": "PALM"
                    }
                )

    # Zachovej návrat na stejnou stránku
    page = request.POST.get("page")
    if page:
        return redirect(f"/spravce/eknihy-prehled/?page={page}")
    return redirect("admin_palmknihy_preview")






# -------------------------------------------------------------------
# F:                 ADMIN STORE PAGE
# -------------------------------------------------------------------
@csrf_exempt
def admin_store_page(request):
    if request.method == "POST":
        ids = request.POST.getlist("palmknihyids")
        unknown_book = Book.objects.get(pk=1)

        for palmknihyid in ids:
            response = get_product_by_id(palmknihyid)
            if not response or "data" not in response:
                continue

            book_data = response["data"]
            if not book_data:
                continue

            # Ulož PRINT (hlavní), pouze pokud ISBN existuje
            isbn_main = normalize_isbn(book_data.get("isbn"))
            if isbn_main:
                Bookisbn.objects.update_or_create(
                    isbn=isbn_main,
                    defaults={
                        "book": unknown_book,
                        "format": "PRINT",
                        "language": book_data.get("language", "cs"),
                        "price": None,
                        "description": book_data.get("description", "")[:500],
                        "palmknihyid": palmknihyid,
                        "ISBNtype": "PALM"
                    }
                )

            # Ulož formáty EPUB, MOBI, PDF (každý jen pokud ISBN je)
            for fmt in ["epub", "mobi", "pdf"]:
                isbn = normalize_isbn(book_data.get(f"spec_isbn-{fmt}"))
                if isbn:
                    Bookisbn.objects.update_or_create(
                        isbn=isbn,
                        defaults={
                            "book": unknown_book,
                            "format": fmt.upper(),
                            "language": book_data.get("language", "cs"),
                            "price": book_data.get("current_valid_price", {}).get("price"),
                            "description": book_data.get("description", "")[:500],
                            "palmknihyid": palmknihyid,
                            "ISBNtype": "PALM"
                        }
                    )
    return redirect(request.META.get("HTTP_REFERER", "admin_palmknihy_preview"))
'''
@csrf_exempt
def admin_store_page(request):
    if request.method == "POST":
        ids = request.POST.getlist("palmknihyids")
        unknown_book = Book.objects.get(pk=1)

        for palmknihyid in ids:
            response = get_product_by_id(palmknihyid)
            if not response or "data" not in response:
                continue

            book_data = response["data"]
            if not book_data:
                continue

            # Hlavní ISBN (PRINT)
            isbn_main = normalize_isbn(book_data.get("isbn"))
            if isbn_main:
                try:
                    rec = Bookisbn.objects.get(isbn=isbn_main)
                    rec.book = unknown_book
                    rec.format = "PRINT"
                    rec.language = book_data.get("language", "cs")
                    rec.price = None
                    rec.description = book_data.get("description", "")[:500]
                    rec.palmknihyid = palmknihyid
                    rec.save()
                except Bookisbn.DoesNotExist:
                    Bookisbn.objects.create(
                        book=unknown_book,
                        isbn=isbn_main,
                        format="PRINT",
                        language=book_data.get("language", "cs"),
                        price=None,
                        description=book_data.get("description", "")[:500],
                        palmknihyid=palmknihyid
                    )

            # Formáty EPUB, MOBI, PDF
            for fmt in ["epub", "mobi", "pdf"]:
                isbn = normalize_isbn(book_data.get(f"spec_isbn-{fmt}"))
                if isbn:
                    try:
                        rec = Bookisbn.objects.get(isbn=isbn)
                        rec.book = unknown_book
                        rec.format = fmt.upper()
                        rec.language = book_data.get("language", "cs")
                        rec.price = book_data.get("current_valid_price", {}).get("price")
                        rec.description = book_data.get("description", "")[:500]
                        rec.palmknihyid = palmknihyid
                        rec.save()
                    except Bookisbn.DoesNotExist:
                        Bookisbn.objects.create(
                            book=unknown_book,
                            isbn=isbn,
                            format=fmt.upper(),
                            language=book_data.get("language", "cs"),
                            price=book_data.get("current_valid_price", {}).get("price"),
                            description=book_data.get("description", "")[:500],
                            palmknihyid=palmknihyid
                        )

    return redirect(request.META.get("HTTP_REFERER", "admin_palmknihy_preview"))
'''


# -------------------------------------------------------------------
#                    KONEC
# -------------------------------------------------------------------