from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme

def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next')  # Získání parametru next z POST
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Ověření, zda je URL bezpečná a povolená
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return HttpResponseRedirect(next_url)
            
            # Pokud není 'next', přesměrování na domovskou stránku
            return redirect('home')  # Změňte 'home' na cílovou stránku po přihlášení
        else:
            messages.error(request, 'Neplatné přihlašovací údaje')

    # Pokud je požadavek GET (zobrazení přihlašovacího formuláře)
    next_url = request.GET.get('next', '/')
    return render(request, 'account/login.html', {'next': next_url})
