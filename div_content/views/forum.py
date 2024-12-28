from django.shortcuts import render, get_object_or_404, redirect
from div_content.models import Forumsection, Forumtopic, Forumcomment
from div_content.forms.forum import ForumTopicForm, ForumCommentForm, EditCommentForm, SearchForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta
from django.db.models import Max, OuterRef, Subquery, Count
from django.core.paginator import Paginator
from div_content.views.login import custom_login_view



# index
def forum(request):
    all_forum_sections = Forumsection.objects.all()
    return render(request, 'forum/forum_index.html', {
        "all_forum_sections": all_forum_sections,
    })

# obsah sekce s diskuzními vlákny
def forum_section_detail(request, slug):
    now = timezone.now()
    section = get_object_or_404(Forumsection, slug=slug)
    # topics = Forumtopic.objects.filter(section=section).order_by("-forumtopicid")[:10]
    # topics = Forumtopic.objects.filter(section=section).annotate(most_recent=Max("forumcomment__createdat")).order_by("-most_recent")
    
    # poslední komentář z diskuzního vlákna
    latest_comment_subquery = Forumcomment.objects.filter(
        topic=OuterRef('pk'),
        topic__section=section
    ).order_by('-createdat').values('user', 'createdat')[:1]

    # autor posledního komentáře z diskuzního vlákna
    latest_user_subquery = Forumcomment.objects.filter(
        topic=OuterRef('pk'),
        topic__section=section
    ).order_by('-createdat').values('user__username')[:1]

    # id autora posledního komentáře
    latest_user_ID_subquery = Forumcomment.objects.filter(
        topic=OuterRef('pk'),
        topic__section=section
    ).order_by('-createdat').values('user')[:1]

    topics = Forumtopic.objects.filter(
        section=section
    ).annotate(
        most_recent=Subquery(latest_comment_subquery.values('createdat')),
        latest_user=Subquery(latest_user_subquery.values('user__username')),
        latest_user_id=Subquery(latest_user_ID_subquery.values("user")),
        comment_count=Count('forumcomment')
    ).order_by('-most_recent')

    for topic in topics:
        if topic.most_recent:
            delta = now - topic.most_recent
            if delta < timedelta(minutes=1):
                topic.latest_activity = "Právě teď"
            elif delta < timedelta(hours=1):
                minutes = int(delta.total_seconds()/60)
                if minutes == 1:
                    topic.latest_activity = f"Před {minutes} minutou"
                else:
                    topic.latest_activity = f"Před {minutes} minutami"
            elif delta < timedelta(days=1):
                hours = int(delta.total_seconds()/3600)
                if hours == 1:
                    topic.latest_activity = f"Před {hours} hodinou"
                else:
                    topic.latest_activity = f"Před {hours} hodinami"
            else:
                topic.latest_activity = topic.most_recent
        else:
            topic.latest_activity = "Neznámo kdy"
    
    items_per_page = 20
    paginator = Paginator(topics, items_per_page)
    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)
    
    return render(request, "forum/forum_section_detail.html", {
        "title": section.title,
        "section": section,
        "topics": topics,
        "page": page,
    })

# přidat nové diskuzní vlákno
@login_required
def create_new_topic(request, slug):
    section = get_object_or_404(Forumsection, slug=slug)

    if request.method == "POST":
        form = ForumTopicForm(request.POST, user=request.user)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.section = section
            new_topic.save()

            Forumcomment.objects.create(
                topic=new_topic,
                user=request.user,
                body=form.cleaned_data['first_post']
            )

            return redirect("forum_topic_detail", slug=section.slug, topicurl=new_topic.topicurl)
    else:
        form = ForumTopicForm()

    return render(request, "forum/forum_create_topic.html", {
        "form": form,
        "section": section,
    })

# obsah diskuzního vlákna s komentáři
def forum_topic_detail(request, slug, topicurl):
    topic = get_object_or_404(Forumtopic, topicurl=topicurl)
    comments = Forumcomment.objects.filter(topic=topic).order_by("-createdat")


    if request.method == "POST":
        form = ForumCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.topic = topic
            comment.user = request.user
            comment.save()
            return redirect("forum_topic_detail", slug=slug, topicurl=topicurl)
    else:
        form = ForumCommentForm()

    items_per_page = 20
    paginator = Paginator(comments, items_per_page)
    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)

    return render(request, "forum/forum_topic_detail.html", {
        "topic": topic,
        "comments": comments,
        "form": form,
        "page": page,
    })

# edit komentáře v diskuzním vláknu
@login_required
def comment_edit(request, slug, topicurl, forumcommentid):
    topic = get_object_or_404(Forumtopic, topicurl=topicurl)
    comments = Forumcomment.objects.filter(topic=topic).order_by("-createdat")
    comment = get_object_or_404(Forumcomment, forumcommentid=forumcommentid)

    if request.user != comment.user and not request.user.is_staff:
        # return HttpResponseForbidden("Přístup odepřen.")
        return render(request, "403.html", status=403)

    if request.method == "POST":
        form = EditCommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.lasteditedat = timezone.now()
            comment.save()
            return redirect("forum_topic_detail", slug=slug, topicurl=topicurl)
    else:
        form = EditCommentForm(instance=comment)

    items_per_page = 20
    paginator = Paginator(comments, items_per_page)
    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)
    
    return render(request, "forum/forum_comment_edit.html", {
        "topic": topic,
        "comments": comments,
        "form": form,
        "page": page,
    })

# smazat komentář v diskuzním vlákně
@login_required
def comment_delete(request, slug, topicurl, forumcommentid):
    topic = get_object_or_404(Forumtopic, topicurl=topicurl)
    comments = Forumcomment.objects.filter(topic=topic).order_by("-createdat")
    comment = get_object_or_404(Forumcomment, forumcommentid=forumcommentid)
    
    if request.user != comment.user and not request.user.is_staff:
        return render(request, "403.html", status=403)

    if request.method == "POST":
        comment.secret_delete()
        return redirect("forum_topic_detail", slug=slug, topicurl=topicurl)

    return render(request, "forum/forum_comment_delete.html", {
        "topic": topic,
        "comments": comments,
        "comment_to_delete": comment,
    })


# odpovědět na komentář v diskuzním vlákně
@login_required
def comment_reply(request, slug, topicurl, forumcommentid):
    topic = get_object_or_404(Forumtopic, topicurl=topicurl)
    comments = Forumcomment.objects.filter(topic=topic).order_by("-createdat")
    comment = get_object_or_404(Forumcomment, forumcommentid=forumcommentid)

    items_per_page = 20
    paginator = Paginator(comments, items_per_page)
    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)

    if comment.parentcommentid is not None:
        return render(request, "forum/forum_topic_detail.html", {
        "topic": topic,
        "comments": comments,
        "error": "Není povoleno odpovídat na odpovědi v diskuzi",
        "page": page,
        })

    if request.method == "POST":
        form = ForumCommentForm(request.POST)
        if form.is_valid():
            reply_comment = form.save(commit=False)
            reply_comment.topic = topic
            reply_comment.user = request.user
            reply_comment.parentcommentid = comment.forumcommentid
            reply_comment.save()
            return redirect("forum_topic_detail", slug=slug, topicurl=topicurl)
    else:
        form = ForumCommentForm()


    
    return render(request, "forum/forum_comment_reply.html", {
        "topic": topic,
        "comments": comments,
        "form": form,
        "page": page,
        })


def forum_search(request):
    comments = None
    topics = None
    if 'q' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['q']
            comments = Forumcomment.objects.filter(body__icontains=query, isdeleted=False)[:20]
            topics = Forumtopic.objects.filter(title__icontains=query)[:10]
    else:
        form = SearchForm()

    return render(request, 'forum/forum_search.html', {
        'form': form, 
        'comments': comments,
        "query": query,
        "topics": topics,

        })