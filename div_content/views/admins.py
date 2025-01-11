# VIEWS.ADMINS.PY

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from div_content.forms.admins import Moviecommentform, TaskForm, TaskCommentForm

from div_content.models import AATask, Moviecomments
from django.utils import timezone




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



@login_required
def admin_tasks(request):
    tasks = AATask.objects.filter(parentid__isnull=True).order_by('-created')
    return render(request, 'admin/admin_tasks.html', {
        'tasks': tasks
    })

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

