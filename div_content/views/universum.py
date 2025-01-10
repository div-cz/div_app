# views/universum.py

from django.shortcuts import render, get_object_or_404
from div_content.models import Book, Metauniversum, Movie 

def universum_list(request):
    universa = Metauniversum.objects.all().order_by('-divrating')[:30]
    return render(request, 'universum/universum_list.html', {'universa': universa})

def universum_detail(request, universum_url):
    universum = get_object_or_404(Metauniversum, universumurl=universum_url)  
    movies = Movie.objects.filter(universumid=universum)[:30]  # Limit to 30 movies
    books = Book.objects.filter(universumid=universum)[:30]  # Limit to 30 movies
    return render(request, 'universum/universum_detail.html', {'universum': universum, 'movies': movies, 'books': books})
