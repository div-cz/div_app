# -------------------------------------------------------------------
#                    VIEWS.EBOOKS.PY
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    OBSAH
# -------------------------------------------------------------------
# ### poznámky a todo
# ### importy
# ### konstanty
# ### funkce
# 
# download_ebook          | (stahování eknih)
# generate_div_epub       | (epub nakladatelstvi.ekultura.eu
# make_epub_download_link |
# request_epub_generation | ()
# send_ebook_paid_email   | e-mail poslaný po zaplacení - volá se v payments.py
# send_to_reader_modal    | (odesílání e-knih do čteček a na mail)
# send_to_reader          | (odesílání e-knih do čteček a na mail)
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    POZNÁMKY A TODO
# -------------------------------------------------------------------
# Vše co souvisí s eKnihami
# Tři varianty: 
# 1) PALM 
# 2) DIV (zdarma) 
# 3) DIV (placená)
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    IMPORTY 
# -------------------------------------------------------------------
# (tři skupiny - každá zvlášt abecedně)
# 1) systémové (abecedně)
# 2) interní (forms,models,views) (abecedně)
# 3) third-part (třetí strana, django, auth) (abecedně)
# -------------------------------------------------------------------
import hashlib
import os
import re
import smtplib
import requests
import tempfile
import time

from div_content.models import Book, Bookisbn, Booklisting, Bookpurchase
from div_content.utils.payments import get_mimetype_from_format

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage 
from django.core.paginator import Paginator
from django.db.models import Min

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.timezone import now
from email.message import EmailMessage


# -------------------------------------------------------------------
#                    KONSTANTY
# -------------------------------------------------------------------
EKULTURA_API_SECRET = os.getenv("EKULTURA_API_EPUB_SECRET")
API_URL = "https://nakladatelstvi.ekultura.eu/api/generate_watermarked_epub.php"


# -------------------------------------------------------------------
#                    ALL EBOOKS
# -------------------------------------------------------------------
def all_ebooks(request):
    all_isbns = Bookisbn.objects.exclude(format__isnull=True).exclude(format__exact="").select_related("book")
    books = (Book.objects.filter(bookisbn__in=all_isbns)
             .annotate(min_price=Min("bookisbn__price")))
    page_obj = paginate_books(request, books)
    return render(request, "books/ebook_list.html", {
        "page_obj": page_obj,
        "page_title": "Všechny e-knihy",
        "page_type": "all",
    })

# -------------------------------------------------------------------
#                    DOWNLOAD_EBOOK
# -------------------------------------------------------------------
@login_required
def download_ebook(request, isbn, format):
    """
    Stahování e-knih – větvení podle zdroje:
    1) PALM – Palmknihy (API, externí zdroj)
    2) DIV zdarma – generický lokální soubor (pdf/epub/mobi)
    3) DIV placená – generovaný EPUB s vodoznakem (externí API)

    Práva: vždy musí být purchase ve stavu PAID nebo musí být zdarma.
    """

    try:
        bookisbn = Bookisbn.objects.get(isbn=isbn, format=format)
    except Bookisbn.DoesNotExist:
        raise Http404("E-kniha neexistuje.")
    book = bookisbn.book
    #isbntype = (bookisbn.ISBNtype or "").upper()
    sourcetype = (bookisbn.sourcetype or "").upper()

    # =============================
    # 1) PALM – Palmknihy
    # =============================
    # Stahuje se přes API Palmknihy. Práva: musí být zakoupeno (PAID).
    if sourcetype == "PALM":
        purchase = Bookpurchase.objects.filter(
            book=book,
            user=request.user,
            format=format,
            status="PAID"
        ).first()
        if not purchase:
            raise Http404("Nemáte zaplaceno nebo objednáno.")
        palmknihy_link = get_palmknihy_download_url(
            palmknihyid=bookisbn.palmknihyid,
            purchaseid=purchase.purchaseid,
            user_id=request.user.id,
            email=request.user.email,
            format=format,
            delivery_type="ebook" if format.lower() in ["epub", "pdf", "mobi"] else "audiobook"
        )
        if not palmknihy_link:
            return HttpResponse("Palmknihy - link není dostupný.", status=404)
        return redirect(palmknihy_link)

    # =============================
    # 2) MLP – přímý link
    # =============================
    if sourcetype == "MLP":
        if not bookisbn.url:
            return HttpResponse("MLP odkaz není dostupný.", status=404)

		# vynutit stáhnutí PDF (neotevirat v prohlizeci)
        #response = requests.get(bookisbn.url, stream=True)
        #if response.status_code != 200:
        #    return HttpResponse("Soubor není dostupný.", status=404)
        #filename = os.path.basename(bookisbn.url) or f"{book.url}.{format.lower()}"
        #django_response = HttpResponse(response.content, content_type="application/pdf")
        #django_response["Content-Disposition"] = f'attachment; filename="{filename}"'
        #return django_response


        # Pokud je kniha placená, kontrolujeme nákup
        if bookisbn.price and bookisbn.price > 0:
            purchase = Bookpurchase.objects.filter(
                book=book,
                user=request.user,
                format=format,
                status="PAID"
            ).first()
            if not purchase:
                raise Http404("Nemáte zaplaceno.")
        return redirect(bookisbn.url)

    # =============================
    # 2) DIV zdarma – volné stažení
    # =============================
    if sourcetype == "DIV":
    # Platí pro knihy zdarma (price == 0 nebo price None).
        if bookisbn.price == 0 or bookisbn.price is None:
            # Vytvoř purchase pokud ještě neexistuje, nebo přepni na PAID
            purchase, created = Bookpurchase.objects.get_or_create(
                book=book,
                user=request.user,
                format=format,
                defaults={
                    "status": "PAID",
                    "price": 0,
                    "paymentdate": now(),
                    "expirationdate": now().replace(year=now().year + 3),
                    "source": sourcetype,
                },
            )
            if not created and purchase.status != "PAID":
                purchase.status = "PAID"
                purchase.price = 0
                purchase.paymentdate = now()
                purchase.expirationdate = now().replace(year=now().year + 3)
                purchase.save()
            allowed = True
        else:
            # Pro placené: uživatel musí mít purchase PAID
            allowed = Bookpurchase.objects.filter(
                book=book,
                user=request.user,
                format=format,
                status="PAID"
            ).exists()

    # =============================
    # 3) DIV placená (remote EPUB)
    # =============================
    # Placený EPUB: generuje se personalizovaný EPUB na ekultura serveru.
    if allowed and sourcetype == "DIV" and bookisbn.price > 0 and format.lower() == "epub":
        purchase = Bookpurchase.objects.filter(
            book=book,
            user=request.user,
            format=format,
            status="PAID"
        ).first()
        file_url = f"https://nakladatelstvi.ekultura.eu/api/download_epub.php?file={book.url}-{purchase.purchaseid}.epub&token={os.getenv('EKULTURA_API_EPUB_SECRET')}"
        remote = requests.get(file_url)
        if remote.status_code == 200:
            response = HttpResponse(remote.content, content_type="application/epub+zip")
            response["Content-Disposition"] = f'attachment; filename="{book.url}-{purchase.purchaseid}.epub"'
            return response
        else:
            messages.error(
                request,
                "Soubor s e-knihou není aktuálně dostupný ani na serveru nakladatelství. Pokud myslíte, že je to chyba, napište na <a href='mailto:info@div.cz'>info@div.cz</a>."
            )
            print("DOWNLOAD DEBUG", book.url, purchase.purchaseid, file_url)
            return redirect("book_detail", book_url=book.url)

    # =============================
    # 4) fallback – ostatní formáty, lokální soubor
    # =============================
    if not allowed:
        raise Http404("Nemáte oprávnění k této e-knize.")

    filename = f"{book.url}.{format.lower()}"
    filepath = os.path.join(os.getenv("FREE_EBOOKS_PATH"), filename)

    if not os.path.exists(filepath):
        messages.error(
            request,
            "Soubor s e-knihou není aktuálně dostupný. Pokud myslíte, že je to chyba, napište na <a href='mailto:info@div.cz'>info@div.cz</a>."
        )
        return redirect("book_detail", book_url=book.url)

    with open(filepath, "rb") as f:
        response = HttpResponse(f.read(), content_type=get_mimetype_from_format(format)[0])
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response


# -------------------------------------------------------------------
#                    FREE EBOOKS
# -------------------------------------------------------------------
def free_ebooks(request):
    free_isbns = Bookisbn.objects.filter(price=0).exclude(format__isnull=True).exclude(format__exact="").select_related("book")
    books = (Book.objects.filter(bookisbn__in=free_isbns)
             .annotate(min_price=Min("bookisbn__price")))
    page_obj = paginate_books(request, books)
    return render(request, "books/ebook_list.html", {
        "page_obj": page_obj,
        "page_title": "E-knihy zdarma",
        "page_type": "free",
    })



# -------------------------------------------------------------------
#                    GENERATE DIV EPUB
# -------------------------------------------------------------------
def generate_div_epub(book_title, user_email, order_id):
    params = {
        "base": f"{book_title}.epub",
        "email": user_email,
        "order_id": str(order_id),
        "token": EKULTURA_API_SECRET,
    }
    try:
        resp = requests.get(API_URL, params=params, timeout=30)
        if resp.status_code == 200:
            # Název souboru (+objednavka Master-KETO-Plan-123.epub)
            return f"{book_title}-{order_id}.epub"
        else:
            print("Chyba při generování EPUB:", resp.text)
            return None
    except Exception as e:
        print("Výjimka při generování EPUB:", e)
        return None


# -------------------------------------------------------------------
#                    MAKE EPUB DOWNLOAD
# -------------------------------------------------------------------
def make_epub_download_link(filename, purchaseid, email, validity_secs=3600):
    ts = int(time.time())
    expires = ts + validity_secs
    secret = os.getenv("EKULTURA_API_EPUB_SECRET")
    h = hashlib.sha256(f"{filename}{purchaseid}{email}{expires}{secret}".encode()).hexdigest()
    return (
        f"https://nakladatelstvi.ekultura.eu/api/download_epub.php"
        f"?file={filename}&pid={purchaseid}&email={email}&expires={expires}&h={h}"
    )


# -------------------------------------------------------------------
#                    PAID BOOKS
# -------------------------------------------------------------------
def paid_ebooks(request):
    paid_isbns = Bookisbn.objects.filter(price__gt=0).exclude(format__isnull=True).exclude(format__exact="").select_related("book")
    books = (Book.objects.filter(bookisbn__in=paid_isbns)
             .annotate(min_price=Min("bookisbn__price")))
    page_obj = paginate_books(request, books)
    return render(request, "books/ebook_list.html", {
        "page_obj": page_obj,
        "page_title": "E-knihy placené",
        "page_type": "paid",
    })

# -------------------------------------------------------------------
#                    PAGINATE BOOKS
# -------------------------------------------------------------------
def paginate_books(request, queryset, per_page=20):
    paginator = Paginator(queryset.distinct(), per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)

# -------------------------------------------------------------------
#                    REQUEST EPUB GENERATION
# -------------------------------------------------------------------
def request_epub_generation(book_slug, user_email, order_id):
    api_secret = os.getenv("EKULTURA_API_EPUB_SECRET")
    url = "https://nakladatelstvi.ekultura.eu/api/watermark.php"
    params = {
        "book": book_slug,  # nebo slug/filename, jak máš v PHP
        "user_email": user_email,
        "order_id": order_id,
        "token": api_secret
    }
    r = requests.get(url, params=params, timeout=60)
    if r.status_code == 200:
        print("EPUB generace úspěšná!")
        return True
    else:
        print(f"Chyba při generování EPUB: {r.text}")
        return False


# -------------------------------------------------------------------
#                    SEND EBOOK PAID EMAIL
# -------------------------------------------------------------------
def send_ebook_paid_email(purchase):
    if not purchase.user or not purchase.user.email:
        print("Chybí email u uživatele.")
        return

    subject = f"E-kniha {purchase.book.title} je připravena ke stažení"
    recipient = purchase.user.email
    account_url = f"https://div.cz/uzivatel/{purchase.user.id}/eshop/#eknihy"  

    context = {
        "user": purchase.user,
        "book": purchase.book,
        "order_id": purchase.purchaseid,
        "account_url": account_url,
    }
    html_message = render_to_string("emails/ebook_paid_confirmation_buyer.html", context)

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = os.getenv("EBOOK_SENDER_ADDRESS")
    msg['To'] = recipient
    msg.set_content("E-kniha je připravena ke stažení.")  # fallback pro text-only
    msg.add_alternative(html_message, subtype='html')

    try:
        with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
            smtp.login(os.getenv("EBOOK_SENDER_ADDRESS"), os.getenv("EBOOK_SENDER_PASSWORD"))
            smtp.send_message(msg)
        print(f"E-mail o zaplacení odeslán: {recipient}")
    except Exception as e:
        print(f"Chyba při odesílání e-mailu: {e}")


"""
@require_POST
@login_required
def send_to_reader_modal(request, isbn, format):
    bookisbn = get_object_or_404(Bookisbn, isbn=isbn)
    book = bookisbn.book

    purchase = Bookpurchase.objects.filter(book=book, user=request.user, format=format, status="PAID").order_by('purchaseid').first()
    if purchase and purchase.kindlemail:
        # Pokud už byla objednávka zaplacena a máme email, POUŽIJEME VŽDY JEN TEN
        kindlemail = purchase.kindlemail
    else:
        # Nová objednávka, vezmeme z POST nebo user.email
        kindlemail = request.POST.get("kindlemail") or request.user.email
        # Nezapomeň ho i uložit do purchase při prvním stažení/zaplacení

    if not kindlemail or "@" not in kindlemail:
        # Nebudeme vůbec pokračovat, zobrazíme chybovou hlášku
        messages.error(request, "Neplatný e-mail pro odeslání do čtečky!")
        return redirect("book_detail", book_url=book.url)

    user = request.user

    # Placené knihy: kontrola zaplacení a e-mail už neměnit
    paid_purchase = Bookpurchase.objects.filter(
        book=book,
        user=user,
        format=format,
        status="PAID"
    ).order_by('purchaseid').first()

    if bookisbn.price > 0:
        if not paid_purchase:
            raise Http404("Nemáte zaplaceno.")
        # Pokud už byl e-mail uložen, NEPŘEPISUJEME ho (pole bude readonly)
        if not paid_purchase.kindlemail:
            paid_purchase.kindlemail = kindlemail
            paid_purchase.save()
        kindlemail = paid_purchase.kindlemail
    else:
        # Zdarma: povolíme vždy zadat nový e-mail, nebo použijeme existující
        purchase, created = Bookpurchase.objects.get_or_create(
            book=book,
            user=user,
            format=format,
            defaults={
                "status": "PAID",
                "price": 0,
                "paymentdate": now(),
                "expirationdate": now().replace(year=now().year + 3),
                "kindlemail": kindlemail,
                "readonly": True,
            },
        )
        # Pokud existoval, případně updatni email (u zdarma je to OK)
        if not created and purchase.kindlemail != kindlemail:
            purchase.kindlemail = kindlemail
            purchase.save()
        kindlemail = purchase.kindlemail

    # Odeslání do čtečky:
    recipient = kindlemail
    mimetype, ext = get_mimetype_from_format(format)
    filename = f"{book.url}.{ext}"
    filepath = os.path.join(os.getenv("FREE_EBOOKS_PATH"), filename)
    if not os.path.exists(filepath):
        raise Http404("Soubor nenalezen.")

    msg = EmailMessage()
    msg['Subject'] = f"E-kniha z DIV.cz: {book.title}"
    msg['From'] = os.getenv("EBOOK_SENDER_ADDRESS")
    msg['To'] = recipient
    msg.set_content("Vaše e-kniha je v příloze. Užijte si čtení.\n\n Tým DIV.cz")

    with open(filepath, 'rb') as f:
        maintype, subtype = mimetype.split('/')
        msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=filename)

    with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
        smtp.login(os.getenv("EBOOK_SENDER_ADDRESS"), os.getenv("EBOOK_SENDER_PASSWORD"))
        smtp.send_message(msg)

    messages.success(request, f"E-kniha <strong>{book.title}</strong> byla odeslána do vaší čtečky na e-mail <strong>{recipient}</strong>.")
    messages.error(
    request,
    "Soubor s e-knihou není aktuálně dostupný. Pokud myslíte, že je to chyba, napište na <a href='mailto:info@div.cz'>info@div.cz</a>."
)
    return redirect("book_detail", book_url=book.url)
"""


# -------------------------------------------------------------------
#                    SEND TO READER MODAL (MODAL & POST)
# -------------------------------------------------------------------
@login_required
def send_to_reader_modal(request, isbn, format):
    bookisbn = get_object_or_404(Bookisbn, isbn=isbn)
    book = bookisbn.book

    # Najdi první PAID objednávku
    purchase = Bookpurchase.objects.filter(
        book=book,
        user=request.user,
        format=format,
        status="PAID"
    ).order_by('purchaseid').first()

    # Pokud není, najdi PENDING (u placené knihy), nebo vytvoř novou (jen pokud žádná není)
    if not purchase:
        purchase, created = Bookpurchase.objects.get_or_create(
            book=book,
            user=request.user,
            format=format,
            status="PENDING" if bookisbn.price > 0 else "PAID",   # free hned paid
            defaults={
                "price": bookisbn.price or 0,
                "paymentdate": now() if bookisbn.price == 0 else None,
                "expirationdate": now().replace(year=now().year + 3) if bookisbn.price == 0 else None,
                "source": (bookisbn.ISBNtype or "").upper(),
            }
        )

    # Už je uložen kindle mail? (readonly)
    kindlemail = purchase.kindlemail if purchase and purchase.kindlemail else request.user.email  # Pokud už v purchase je, použij, jinak předvyplň uživatelovým
    readonly = bool(purchase and purchase.kindlemail)  # Pokud už je v DB, už nikdy neměnit


    if request.method == "POST":
        kindlemail = request.POST.get("kindlemail")
        if not kindlemail or "@" not in kindlemail:
            messages.error(request, "Neplatný e-mail.")
            return redirect("book_detail", book_url=book.url)
        if not purchase.kindlemail:
            purchase.kindlemail = kindlemail
            purchase.save()
        recipient = purchase.kindlemail
    
        # Rozlišení
        is_free_div = (bookisbn.ISBNtype or "").upper() == "DIV" and (bookisbn.price == 0 or bookisbn.price is None)
        is_paid_div_epub = (bookisbn.ISBNtype or "").upper() == "DIV" and bookisbn.price > 0 and format.lower() == "epub"
        mimetype, ext = get_mimetype_from_format(format)
        maintype, subtype = mimetype.split('/')
    
        if is_paid_div_epub:
            file_url = f"https://nakladatelstvi.ekultura.eu/api/download_epub.php?file={book.url}-{purchase.purchaseid}.epub&token={os.getenv('EKULTURA_API_EPUB_SECRET')}"
            remote = requests.get(file_url)
            if remote.status_code == 200:
                response = HttpResponse(remote.content, content_type="application/epub+zip")
                response["Content-Disposition"] = f'attachment; filename="{book.url}-{purchase.purchaseid}.epub"'
                return response
            else:
                messages.error(request, "Soubor není dostupný pro odeslání do čtečky. Pokud myslíte, že je to chyba, napište na info@div.cz.")
                return redirect("book_detail", book_url=book.url)
        else:
            filename = f"{book.url}.{format.lower()}"
            filepath = os.path.join(os.getenv("FREE_EBOOKS_PATH"), filename)
            if not os.path.exists(filepath):
                messages.error(request, "Soubor není dostupný.")
                return redirect("book_detail", book_url=book.url)
            with open(filepath, 'rb') as f:
                file_content = f.read()
    
        # Odeslání e-mailem
        msg = EmailMessage()
        msg['Subject'] = f"E-kniha z DIV.cz: {book.title}"
        msg['From'] = os.getenv("EBOOK_SENDER_ADDRESS")
        msg['To'] = recipient
        msg.set_content("Vaše e-kniha je v příloze. Užijte si čtení.\n\n Tým DIV.cz")
        msg.add_attachment(file_content, maintype=maintype, subtype=subtype, filename=filename)
    
        with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
            smtp.login(os.getenv("EBOOK_SENDER_ADDRESS"), os.getenv("EBOOK_SENDER_PASSWORD"))
            smtp.send_message(msg)
    
        messages.success(request, f"E-kniha <strong>{book.title}</strong> byla odeslána do vaší čtečky na e-mail <strong>{recipient}</strong>.")
        return redirect("book_detail", book_url=book.url)


    # ---- GET požadavek – jen zobrazení formuláře ----------
    return render(request, "books/send_to_reader_email.html", {
        "isbn": isbn,
        "format": format,
        "user": request.user,
        "kindlemail": purchase.kindlemail or request.user.email,
        "readonly": bool(purchase.kindlemail),
    })


# -------------------------------------------------------------------
#                    SEND TO READER 
# -------------------------------------------------------------------
@login_required
def send_to_reader(request, isbn, format):
    bookisbn = get_object_or_404(Bookisbn, isbn=isbn)
    book = bookisbn.book
    # 1) PALM – stáhni a pošli
    # 2) DIV zdarma – lokální soubor
    # 3) DIV placená EPUB – stáhni z ekultura, pošli remote file_content
    # 4) fallback
    if request.method == "POST":
        kindlemail = request.POST.get("kindlemail") or request.user.email
        purchase, created = Bookpurchase.objects.get_or_create(
            book=book,
            user=request.user,
            format=format,
            defaults={
                "status": "PAID" if bookisbn.price == 0 else "PENDING",
                "price": bookisbn.price or 0,
                "paymentdate": now() if bookisbn.price == 0 else None,
                "expirationdate": now().replace(year=now().year + 3) if bookisbn.price == 0 else None,
                "kindlemail": kindlemail
            }
        )
        if not created and not purchase.kindlemail:
            purchase.kindlemail = kindlemail
            purchase.save()
    else:
        return render(request, "books/send_to_reader_email.html", {"isbn": isbn, "format": format, "user": request.user})

    recipient = purchase.kindlemail

    # PALMKNIHY: stáhni přes API, přilož do mailu
    if bookisbn.ISBNtype == "PALM":
        palmknihy_link = get_palmknihy_download_url(
            palmknihyid=bookisbn.palmknihyid,
            purchaseid=purchase.purchaseid,
            user_id=request.user.id,
            email=request.user.email,
            format=format,
            delivery_type="ebook"
        )
        if not palmknihy_link:
            messages.error(
                request,
                "Link není dostupný. Pokud je to chyba, napište na <a href='mailto:info@div.cz'>info@div.cz</a> nebo zkontrolujte svou objednávku v DIV.cz."
            )
            return redirect("book_detail", book_url=book.url)
        import tempfile, requests
        resp = requests.get(palmknihy_link)
        if resp.status_code != 200:
            messages.error(
                request,
                "Palmknihy - soubor není dostupný. Pokud je to chyba, napište na <a href='mailto:info@div.cz'>info@div.cz</a>."
            )
            return redirect("book_detail", book_url=book.url)
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmp:
            tmp.write(resp.content)
            tmp_path = tmp.name
        file_to_attach = tmp_path
    else:
        filename = f"{book.url}.{format.lower()}"
        filepath = os.path.join(os.getenv("FREE_EBOOKS_PATH"), filename)
        if not os.path.exists(filepath):
            messages.error(
                request,
                "Soubor s e-knihou není aktuálně dostupný. Pokud myslíte, že je to chyba, napište na <a href='mailto:info@div.cz'>info@div.cz</a>."
            )
            return redirect("book_detail", book_url=book.url)
        file_to_attach = filepath


        ### DIV ePub
        # pro EPUB/DIV/placená použij remote
        if purchase and bookisbn.ISBNtype == "DIV" and bookisbn.price > 0 and format.lower() == "epub":
            file_url = f"https://nakladatelstvi.ekultura.eu/api/download_epub.php?file={book.url}-{purchase.purchaseid}.epub&token={os.getenv('EKULTURA_API_EPUB_SECRET')}"
            remote = requests.get(file_url)
            if remote.status_code == 200:
                file_content = remote.content
                filename = f"{book.url}-{purchase.purchaseid}.epub"
            else:
                messages.error(request, "Soubor není dostupný pro odeslání do čtečky. Pokud myslíte, že je to chyba, napište na info@div.cz.")
                return redirect("book_detail", book_url=book.url)
        else:
            # fallback – tvůj původní lokální soubor (pro zdarma, PALM atd.)
            filename = f"{book.url}.{format.lower()}"
            filepath = os.path.join(os.getenv("FREE_EBOOKS_PATH"), filename)
            if not os.path.exists(filepath):
                messages.error(request, "Soubor není dostupný.")
                return redirect("book_detail", book_url=book.url)
            with open(filepath, 'rb') as f:
                file_content = f.read()
        # Posíláš file_content jako attachment


    # Odeslání e-mailem (společné pro oba případy)
    msg = EmailMessage()
    msg['Subject'] = f"E-kniha z DIV.cz: {book.title}"
    msg['From'] = os.getenv("EBOOK_SENDER_ADDRESS")
    msg['To'] = recipient
    msg.set_content("Vaše e-kniha je v příloze. Užij si čtení a nezapomeň ohodnotit na DIV.cz.\n\n Tým DIV.cz")

    with open(file_to_attach, 'rb') as f:
        mimetype, ext = get_mimetype_from_format(format)
        maintype, subtype = mimetype.split('/')
        msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(file_to_attach))

    with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
        smtp.login(os.getenv("EBOOK_SENDER_ADDRESS"), os.getenv("EBOOK_SENDER_PASSWORD"))
        smtp.send_message(msg)

    # Smaž temp soubor, pokud byl PALM
    if bookisbn.ISBNtype == "PALM" and file_to_attach:
        os.unlink(file_to_attach)

    # Úspěšná hláška vždy
    messages.success(
        request,
        f"E-kniha <strong>{book.title}</strong> byla odeslána do vaší čtečky na e-mail <strong>{recipient}</strong>."
    )
    return redirect("book_detail", book_url=book.url)


# -------------------------------------------------------------------
#                    KONEC
#           Catalog DIV.cz by eKultura
# -------------------------------------------------------------------