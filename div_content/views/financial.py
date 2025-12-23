# -------------------------------------------------------------------
#                    ADMIN – FINANCIAL
# -------------------------------------------------------------------

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from div_content.models import Financialtransaction
from div_content.forms.financial import FinancialTransactionForm


def is_accounting(user):
    return user.groups.filter(name='accounting').exists()


@login_required
def admin_financial_list(request):

    if not is_accounting(request.user):
        messages.error(request, "Pro finanční operace musíte být členem accounting.")
        return redirect('antikvariat_home')

    qs = Financialtransaction.objects.all().order_by('-createdat')

    paginator = Paginator(qs, 25)  # <- ZÁKLAD, měnitelné
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'divkvariat/admin_financial_list.html', {
        'page_obj': page_obj,
    })


@login_required
def admin_financial_add(request):

    if not is_accounting(request.user):
        messages.error(request, "Nemáte oprávnění.")
        return redirect('admin_financial_list')

    form = FinancialTransactionForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Finanční záznam byl přidán.")
        return redirect('admin_financial_list')

    return render(request, 'divkvariat/admin_financial_form.html', {
        'form': form,
        'title': 'Přidat finanční záznam',
    })


@login_required
def admin_financial_edit(request, transaction_id):

    if not is_accounting(request.user):
        messages.error(request, "Nemáte oprávnění.")
        return redirect('admin_financial_list')

    tx = get_object_or_404(Financialtransaction, transactionid=transaction_id)
    form = FinancialTransactionForm(request.POST or None, instance=tx)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Finanční záznam byl uložen.")
        return redirect('admin_financial_list')

    return render(request, 'divkvariat/admin_financial_form.html', {
        'form': form,
        'title': 'Upravit finanční záznam',
    })
