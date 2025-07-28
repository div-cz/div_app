# -------------------------------------------------------------------
#                    VIEWS.BLOG.PY
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
from datetime import date

from div_content.forms.blog import Articleblogform, Articleblogpostform, Articleblogcommentform
from div_content.models import Articleblog, Articleblogpost, Articleblogcomment, Movie
from div_content.views.login import custom_login_view


from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView



def blog_add_post(request):
    if request.method == 'POST':
        form = Articleblogpostform(request.POST, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            
            blog = post.articleblog  
            # Ověření, že uživatel vlastní blog
            if blog.user != request.user:
                return HttpResponse("Nemáte oprávnění přidávat příspěvky do tohoto blogu.", status=403)

            post.user = request.user
            post.save()
            return redirect('blog_post_detail', blog_slug=post.articleblog.slug, post_slug=post.slug)
    else:
        form = Articleblogpostform(user=request.user)
    
    return render(request, 'blog/blog_add_post.html', {'form': form})


def blog_detail(request, slug):
    blog = get_object_or_404(Articleblog, slug=slug)
    # Načtení příspěvků souvisejících s blogem
    posts = Articleblogpost.objects.filter(articleblog=blog).order_by('-published_at')
    # Stránkování - 10 příspěvků na stránku
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/blog_detail.html', {'blog': blog, 'page_obj': page_obj})



def blog_post_detail(request, blog_slug, post_slug):
    post = get_object_or_404(Articleblogpost, articleblog__slug=blog_slug, slug=post_slug)
    comments = post.comments.all()
    
    if request.method == 'POST':
        comment_form = Articleblogcommentform(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.articleblogpost = post
            comment.save()
            return redirect('blog_post_detail', blog_slug=blog_slug, post_slug=post_slug)
    else:
        comment_form = Articleblogcommentform()
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'blog/blog_post_detail.html', context)



def blog_list(request):
    if request.user.is_authenticated:
        # Načtení všech blogů aktuálního uživatele
        user_blogs = Articleblog.objects.filter(user=request.user)
    else:
        user_blogs = None
    return render(request, 'blog/blog_list.html', {'user_blogs': user_blogs})


def blog_index(request):
    # Načtení dvaceti nejnovějších blogů podle typu
    # book_blogs = Articleblog.objects.filter(blog_type='book').order_by('-created_at')[:20]
    # game_blogs = Articleblog.objects.filter(blog_type='game').order_by('-created_at')[:20]
    # movie_blogs = Articleblog.objects.filter(blog_type='movie').order_by('-created_at')[:20]
    # general_blogs = Articleblog.objects.filter(blog_type='general').order_by('-created_at')[:20]

    # context = {
    #     'book_blogs': book_blogs,
    #     'game_blogs': game_blogs,
    #     'movie_blogs': movie_blogs,
    #     'general_blogs': general_blogs,
    # }
    return render(request, 'blog/blog_index.html')
    # return render(request, "blog/blog_section_menu.html")


def blog_section_detail(request, section=None):
    if section == "herni":
        game_blogs = Articleblog.objects.filter(blog_type='game').order_by('-created_at')[:20]
        return render(request, "blog/blog_section_detail.html", {
            "game_blogs": game_blogs,
            "section": section
            })
    elif section == "filmove":
        movie_blogs = Articleblog.objects.filter(blog_type='movie').order_by('-created_at')[:20]
        return render(request, "blog/blog_section_detail.html", {
            "movie_blogs": movie_blogs,
            "section": section
        })
    elif section == "knizni":
        book_blogs = Articleblog.objects.filter(blog_type='book').order_by('-created_at')[:20]
        return render(request, "blog/blog_section_detail.html", {
            "book_blogs": book_blogs,
            "section": section
            })
    elif section == "obecne":
        general_blogs = Articleblog.objects.filter(blog_type='general').order_by('-created_at')[:20]
        return render(request, "blog/blog_section_detail.html", {
            "general_blogs": general_blogs,
            "section": section
        })
    else:
        return render(request, "404.html", status=404)


def blog_new(request):
    if request.method == 'POST':
        form = Articleblogform(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.user = request.user  # Nastavíme aktuálního uživatele jako vlastníka blogu
            blog.save()
            return redirect('blog_detail', slug=blog.slug)  # Přesměrujeme na detail nového blogu
    else:
        form = Articleblogform()
    
    return render(request, 'blog/blog_new.html', {'form': form})
