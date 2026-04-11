from datetime import date
from decimal import Decimal

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


def _summary_target_month(request):
    """クエリ ym=YYYY-MM または year/month から集計対象月（その月1日）を返す。未来月は今月に丸める。"""
    today = timezone.localdate()
    current_first = date(today.year, today.month, 1)
    ym = request.GET.get('ym')
    if ym:
        try:
            y_str, m_str = ym.split('-', 1)
            y, m = int(y_str), int(m_str)
            if 1 <= m <= 12 and 2000 <= y <= 2100:
                target = date(y, m, 1)
                if target > current_first:
                    target = current_first
                return target
        except (TypeError, ValueError):
            pass
    try:
        y = int(request.GET.get('year', today.year))
        m = int(request.GET.get('month', today.month))
        if not (1 <= m <= 12 and 2000 <= y <= 2100):
            raise ValueError
        target = date(y, m, 1)
    except (TypeError, ValueError):
        target = current_first
    if target > current_first:
        target = current_first
    return target


def _add_months(first: date, delta: int) -> date:
    y, m = first.year, first.month + delta
    while m > 12:
        m -= 12
        y += 1
    while m < 1:
        m += 12
        y -= 1
    return date(y, m, 1)


def _monthly_income_expense_balance(user, year: int, month: int):
    income_total = (
        IncomeEntry.objects.filter(user=user, date__year=year, date__month=month).aggregate(
            s=Sum('amount')
        )['s']
        or Decimal('0')
    )
    expense_total = (
        ExpenseEntry.objects.filter(user=user, date__year=year, date__month=month).aggregate(
            s=Sum('amount')
        )['s']
        or Decimal('0')
    )
    balance = income_total - expense_total
    return income_total, expense_total, balance


def _monthly_income_entries(user, year: int, month: int):
    return IncomeEntry.objects.filter(
        user=user, date__year=year, date__month=month
    )


def _monthly_expense_entries(user, year: int, month: int):
    return ExpenseEntry.objects.filter(
        user=user, date__year=year, date__month=month
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
    target = _summary_target_month(request)
    y, m = target.year, target.month
    income_total, expense_total, balance = _monthly_income_expense_balance(
        request.user, y, m
    )
    today = timezone.localdate()
    current_first = date(today.year, today.month, 1)
    prev_m = _add_months(target, -1)
    next_m = _add_months(target, 1)
    can_go_next = next_m <= current_first
    return render(
        request,
        'accounts/monthly_summary.html',
        {
            'summary_year': y,
            'summary_month': m,
            'period_label': f'{y}年{m}月',
            'month_input_value': f'{y:04d}-{m:02d}',
            'income_total': income_total,
            'expense_total': expense_total,
            'balance': balance,
            'prev_year': prev_m.year,
            'prev_month': prev_m.month,
            'next_year': next_m.year,
            'next_month': next_m.month,
            'can_go_next': can_go_next,
            'income_entries': _monthly_income_entries(request.user, y, m),
            'expense_entries': _monthly_expense_entries(request.user, y, m),
        },
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
