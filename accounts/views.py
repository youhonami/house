from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncMonth

from .forms import EmailLoginForm, ExpenseEntryForm, IncomeEntryForm, RegisterForm
from .models import ExpenseEntry, IncomeEntry


def _home():
    return redirect(settings.LOGIN_REDIRECT_URL)


@login_required
def top(request):
    return render(request, 'accounts/top.html')


def _stub_ctx(title_suffix: str, heading: str, note: str):
    return {'title_suffix': title_suffix, 'heading': heading, 'note': note}


def _income_monthly_totals(user):
    return (
        IncomeEntry.objects.filter(user=user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('-month')
    )


def _expense_monthly_totals(user):
    return (
        ExpenseEntry.objects.filter(user=user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('-month')
    )


@login_required
def income(request):
    if request.method == 'POST':
        form = IncomeEntryForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('accounts:income')
    else:
        form = IncomeEntryForm(initial={'date': timezone.localdate()})
    return render(
        request,
        'accounts/income.html',
        {
            'form': form,
            'monthly_totals': _income_monthly_totals(request.user),
        },
    )


@login_required
def expense(request):
    if request.method == 'POST':
        form = ExpenseEntryForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('accounts:expense')
    else:
        form = ExpenseEntryForm(initial={'date': timezone.localdate()})
    return render(
        request,
        'accounts/expense.html',
        {
            'form': form,
            'monthly_totals': _expense_monthly_totals(request.user),
        },
    )


@login_required
def daily_summary(request):
    return render(
        request,
        'accounts/placeholder.html',
        _stub_ctx('日別集計', '日別集計', 'ここに日別集計の内容を追加予定です。'),
    )


@login_required
def monthly_summary(request):
    return render(
        request,
        'accounts/placeholder.html',
        _stub_ctx('月度集計', '月度集計', 'ここに月度集計の内容を追加予定です。'),
    )


@login_required
def goal_settings(request):
    return render(
        request,
        'accounts/placeholder.html',
        _stub_ctx('目標設定', '目標設定', 'ここに目標設定の内容を追加予定です。'),
    )


@login_required
def settings_page(request):
    return render(
        request,
        'accounts/placeholder.html',
        _stub_ctx('設定', '設定', 'ここに設定画面の内容を追加予定です。'),
    )


def login_view(request):
    if request.user.is_authenticated:
        return _home()
    data = request.POST if request.method == 'POST' else None
    form = EmailLoginForm(request=request, data=data)
    if form.is_valid():
        login(request, form.cleaned_data['user'])
        return _home()
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return _home()
    data = request.POST if request.method == 'POST' else None
    form = RegisterForm(data)
    if form.is_valid():
        login(request, form.save())
        return _home()
    return render(request, 'accounts/register.html', {'form': form})
