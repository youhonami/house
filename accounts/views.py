import calendar
from datetime import date, timedelta
from urllib.parse import urlencode
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth

from .forms import (
    BudgetSettingsForm,
    DiaryEntryForm,
    EmailLoginForm,
    ExpenseEntryForm,
    IncomeEntryForm,
    PasswordChangeSettingsForm,
    RegisterForm,
    ScheduleEntryForm,
)
from .models import DiaryEntry, ExpenseBudget, ExpenseEntry, IncomeEntry, ScheduleEntry


def _home():
    return redirect(settings.LOGIN_REDIRECT_URL)


@login_required
def top(request):
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)
    income_total, expense_total, balance = _monthly_income_expense_balance(
        request.user, today.year, today.month
    )
    yesterday_diary_entries = list(
        DiaryEntry.objects.filter(user=request.user, date=yesterday).order_by(
            '-created_at',
            '-id',
        )
    )
    yesterday_goal_entries = [
        e for e in yesterday_diary_entries if (e.tomorrow_goals or '').strip()
    ]
    yesterday_has_any_goal = bool(yesterday_goal_entries)
    return render(
        request,
        'accounts/top.html',
        {
            'this_month_label': f'{today.year}年{today.month}月',
            'this_month_income_total': income_total,
            'this_month_expense_total': expense_total,
            'this_month_balance': balance,
            'chart_income': int(income_total),
            'chart_expense': int(expense_total),
            'yesterday_date': yesterday,
            'yesterday_diary_entries': yesterday_diary_entries,
            'yesterday_goal_entries': yesterday_goal_entries,
            'yesterday_has_any_goal': yesterday_has_any_goal,
        },
    )


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


_DAY_MIN = date(2000, 1, 1)


def _summary_target_day(request):
    """クエリ d=YYYY-MM-DD から集計対象日を返す。未来日は今日に、下限は2000-01-01。"""
    today = timezone.localdate()
    d_param = request.GET.get('d')
    if d_param:
        try:
            parts = d_param.split('-')
            if len(parts) == 3:
                y, m, day = int(parts[0]), int(parts[1]), int(parts[2])
                target = date(y, m, day)
                if target > today:
                    target = today
                if target < _DAY_MIN:
                    target = _DAY_MIN
                return target
        except (TypeError, ValueError):
            pass
    return today


def _daily_income_expense_balance(user, target: date):
    income_total = (
        IncomeEntry.objects.filter(user=user, date=target).aggregate(s=Sum('amount'))[
            's'
        ]
        or Decimal('0')
    )
    expense_total = (
        ExpenseEntry.objects.filter(user=user, date=target).aggregate(s=Sum('amount'))[
            's'
        ]
        or Decimal('0')
    )
    balance = income_total - expense_total
    return income_total, expense_total, balance


def _daily_income_entries(user, target: date):
    return IncomeEntry.objects.filter(user=user, date=target)


def _daily_expense_entries(user, target: date):
    return ExpenseEntry.objects.filter(user=user, date=target)


def _daily_expense_category_totals(user, target: date):
    """指定日の支出をカテゴリ別に集計（金額の多い順）。"""
    label_map = dict(ExpenseBudget.Category.choices)
    rows = (
        ExpenseEntry.objects.filter(user=user, date=target)
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total', 'category')
    )
    return [
        {
            'category': r['category'],
            'label': label_map.get(r['category'], r['category']),
            'total': r['total'] if r['total'] is not None else Decimal('0'),
        }
        for r in rows
    ]


def _monthly_expense_vs_budget_rows(user, year: int, month: int):
    """カテゴリごとの実��・目標・�と判定（over / under / on / no_budget）。"""
    actual_map = {
        row['category']: row['total']
        for row in ExpenseEntry.objects.filter(
            user=user, date__year=year, date__month=month
        )
        .values('category')
        .annotate(total=Sum('amount'))
    }
    budget_map = {
        b.category: b.monthly_amount
        for b in ExpenseBudget.objects.filter(user=user)
    }
    rows = []
    for value, label in ExpenseBudget.Category.choices:
        act = actual_map.get(value) or Decimal('0')
        bud = budget_map.get(value)
        if bud is None and act == 0:
            continue
        if bud is not None:
            diff = act - bud
            if diff > 0:
                status = 'over'
            elif diff < 0:
                status = 'under'
            else:
                status = 'on'
        else:
            diff = None
            status = 'no_budget'
        rows.append(
            {
                'category': value,
                'label': label,
                'actual': act,
                'budget': bud,
                'diff': diff,
                'status': status,
            }
        )
    return rows


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
    target = _summary_target_day(request)
    today = timezone.localdate()
    income_total, expense_total, balance = _daily_income_expense_balance(
        request.user, target
    )
    prev_d = target - timedelta(days=1)
    next_d = target + timedelta(days=1)
    can_go_prev = target > _DAY_MIN
    can_go_next = next_d <= today
    return render(
        request,
        'accounts/daily_summary.html',
        {
            'summary_date': target,
            'period_label': f'{target.year}年{target.month}月{target.day}日',
            'date_input_value': target.isoformat(),
            'date_max_value': today.isoformat(),
            'income_total': income_total,
            'expense_total': expense_total,
            'balance': balance,
            'prev_d': prev_d.isoformat(),
            'next_d': next_d.isoformat(),
            'can_go_prev': can_go_prev,
            'can_go_next': can_go_next,
            'income_entries': _daily_income_entries(request.user, target),
            'expense_entries': _daily_expense_entries(request.user, target),
            'expense_category_totals': _daily_expense_category_totals(
                request.user, target
            ),
            'expense_category_choices': ExpenseBudget.Category.choices,
        },
    )


@login_required
def monthly_summary(request):
    target = _summary_target_month(request)
    y, m = target.year, target.month
    income_total, expense_total, balance = _monthly_income_expense_balance(
        request.user, y, m
    )
    expense_budget_total = _budget_monthly_total(request.user)
    expense_budget_has_targets = expense_budget_total > 0
    expense_vs_budget = (
        expense_total - expense_budget_total if expense_budget_has_targets else None
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
            'expense_budget_total': expense_budget_total,
            'expense_budget_has_targets': expense_budget_has_targets,
            'expense_vs_budget': expense_vs_budget,
            'expense_budget_rows': _monthly_expense_vs_budget_rows(request.user, y, m),
            'balance': balance,
            'prev_year': prev_m.year,
            'prev_month': prev_m.month,
            'next_year': next_m.year,
            'next_month': next_m.month,
            'can_go_next': can_go_next,
            'income_entries': _monthly_income_entries(request.user, y, m),
            'expense_entries': _monthly_expense_entries(request.user, y, m),
            'expense_category_choices': ExpenseBudget.Category.choices,
        },
    )


def _form_errors_dict(form):
    return {field: list(msgs) for field, msgs in form.errors.items()}


@login_required
@require_http_methods(['GET', 'POST', 'DELETE'])
def monthly_income_entry(request, pk):
    entry = get_object_or_404(IncomeEntry, pk=pk, user=request.user)
    if request.method == 'GET':
        return JsonResponse(
            {
                'ok': True,
                'data': {
                    'id': entry.pk,
                    'date': entry.date.isoformat(),
                    'amount': str(int(entry.amount)),
                    'note': entry.note or '',
                },
            }
        )
    if request.method == 'DELETE':
        entry.delete()
        return JsonResponse({'ok': True})
    form = IncomeEntryForm(request.POST, instance=entry)
    if form.is_valid():
        form.save()
        return JsonResponse({'ok': True})
    return JsonResponse(
        {'ok': False, 'errors': _form_errors_dict(form)},
        status=400,
    )


@login_required
@require_http_methods(['GET', 'POST', 'DELETE'])
def monthly_expense_entry(request, pk):
    entry = get_object_or_404(ExpenseEntry, pk=pk, user=request.user)
    if request.method == 'GET':
        return JsonResponse(
            {
                'ok': True,
                'data': {
                    'id': entry.pk,
                    'date': entry.date.isoformat(),
                    'amount': str(int(entry.amount)),
                    'category': entry.category,
                    'note': entry.note or '',
                },
            }
        )
    if request.method == 'DELETE':
        entry.delete()
        return JsonResponse({'ok': True})
    form = ExpenseEntryForm(request.POST, instance=entry)
    if form.is_valid():
        form.save()
        return JsonResponse({'ok': True})
    return JsonResponse(
        {'ok': False, 'errors': _form_errors_dict(form)},
        status=400,
    )


def _budget_initial_for_user(user):
    rows = ExpenseBudget.objects.filter(user=user)
    return {r.category: r.monthly_amount for r in rows}


def _budget_monthly_total(user):
    total = ExpenseBudget.objects.filter(user=user).aggregate(s=Sum('monthly_amount'))['s']
    return total or Decimal('0')


def _save_budgets_from_form(user, form):
    for value, _label in ExpenseBudget.Category.choices:
        amt = form.cleaned_data.get(value)
        if amt is not None and amt > 0:
            ExpenseBudget.objects.update_or_create(
                user=user,
                category=value,
                defaults={'monthly_amount': amt},
            )
        else:
            ExpenseBudget.objects.filter(user=user, category=value).delete()


@login_required
def goal_settings(request):
    if request.method == 'POST':
        form = BudgetSettingsForm(request.POST)
        if form.is_valid():
            _save_budgets_from_form(request.user, form)
            messages.success(request, '支出予算を保存しました。')
            return redirect('accounts:goal_settings')
    else:
        form = BudgetSettingsForm(initial=_budget_initial_for_user(request.user))
    return render(
        request,
        'accounts/goal_settings.html',
        {
            'form': form,
            'budget_total': _budget_monthly_total(request.user),
        },
    )


@login_required
def diary_write(request):
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, '日記を保存しました。')
            return redirect('accounts:diary_write')
    else:
        form = DiaryEntryForm(initial={'date': timezone.localdate()})
    return render(
        request,
        'accounts/diary_write.html',
        {'form': form},
    )


def _add_month(year: int, month: int, delta: int) -> tuple[int, int]:
    month += delta
    while month > 12:
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1
    return year, month


def _calendar_month_context(request):
    today = timezone.localdate()
    try:
        cal_year = int(request.GET.get('year', today.year))
        cal_month = int(request.GET.get('month', today.month))
    except (TypeError, ValueError):
        cal_year, cal_month = today.year, today.month
    cal_month = max(1, min(12, cal_month))
    cal_year = max(1900, min(2100, cal_year))

    prev_y, prev_m = _add_month(cal_year, cal_month, -1)
    next_y, next_m = _add_month(cal_year, cal_month, 1)
    cal_obj = calendar.Calendar(firstweekday=calendar.MONDAY)

    return {
        'today': today,
        'cal_year': cal_year,
        'cal_month': cal_month,
        'calendar_weeks': cal_obj.monthdatescalendar(cal_year, cal_month),
        'prev_year': prev_y,
        'prev_month': prev_m,
        'next_year': next_y,
        'next_month': next_m,
    }


@login_required
def diary_browse(request):
    user = request.user
    calendar_context = _calendar_month_context(request)
    today = calendar_context['today']
    cal_year = calendar_context['cal_year']
    cal_month = calendar_context['cal_month']

    date_str = request.GET.get('date')
    selected_date = None
    if date_str:
        try:
            selected_date = date.fromisoformat(date_str)
        except ValueError:
            selected_date = None

    shown = request.GET.get('shown') == '1'

    month_entries = DiaryEntry.objects.filter(
        user=user,
        date__year=cal_year,
        date__month=cal_month,
    )
    dates_with_entries = set(month_entries.values_list('date', flat=True).distinct())

    entries = []
    open_entry_id = None
    if shown and selected_date:
        entries = list(
            DiaryEntry.objects.filter(user=user, date=selected_date).order_by(
                '-created_at',
                '-id',
            )
        )
        entry_raw = request.GET.get('entry')
        if entry_raw:
            try:
                want_pk = int(entry_raw)
                if any(e.pk == want_pk for e in entries):
                    open_entry_id = want_pk
            except (ValueError, TypeError):
                pass

    return render(
        request,
        'accounts/diary_browse.html',
        {
            **calendar_context,
            'dates_with_entries': dates_with_entries,
            'selected_date': selected_date,
            'shown': shown,
            'entries': entries,
            'open_entry_id': open_entry_id,
        },
    )


@login_required
@require_http_methods(['POST'])
def diary_delete(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    d = entry.date
    entry.delete()
    messages.success(request, '日記を削除しました。')
    q = urlencode(
        {
            'year': d.year,
            'month': d.month,
            'date': d.isoformat(),
            'shown': '1',
        }
    )
    return redirect(f'{reverse("accounts:diary_browse")}?{q}')


@login_required
def schedule_write(request):
    selected_date = None
    if request.method == 'POST':
        form = ScheduleEntryForm(request.POST)
        date_str = request.POST.get('date')
        if date_str:
            try:
                selected_date = date.fromisoformat(date_str)
            except ValueError:
                selected_date = None
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, '予定を保存しました。')
            q = urlencode(
                {
                    'year': obj.date.year,
                    'month': obj.date.month,
                    'date': obj.date.isoformat(),
                }
            )
            return redirect(f'{reverse("accounts:schedule_write")}?{q}')
    else:
        date_str = request.GET.get('date')
        if date_str:
            try:
                selected_date = date.fromisoformat(date_str)
            except ValueError:
                selected_date = None
        form = ScheduleEntryForm(initial={'date': selected_date})

    return render(
        request,
        'accounts/schedule_calendar.html',
        {
            **_calendar_month_context(request),
            'title': '予定を記入する',
            'lead': 'カレンダーの日付をクリックすると、時間と予定を入力できます。',
            'calendar_url_name': 'accounts:schedule_write',
            'selected_date': selected_date,
            'form': form,
            'is_schedule_write': True,
        },
    )


@login_required
def schedule_browse(request):
    calendar_context = _calendar_month_context(request)
    cal_year = calendar_context['cal_year']
    cal_month = calendar_context['cal_month']
    selected_date = None
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = date.fromisoformat(date_str)
        except ValueError:
            selected_date = None

    schedule_entries = []
    if selected_date:
        schedule_entries = list(
            ScheduleEntry.objects.filter(user=request.user, date=selected_date).order_by(
                'time',
                'id',
            )
        )
    schedule_date_counts = list(
        ScheduleEntry.objects.filter(
            user=request.user,
            date__year=cal_year,
            date__month=cal_month,
        )
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    return render(
        request,
        'accounts/schedule_calendar.html',
        {
            **calendar_context,
            'title': '予定を確認する',
            'lead': 'カレンダーの日付をクリックすると、その日の予定を確認できます。',
            'calendar_url_name': 'accounts:schedule_browse',
            'selected_date': selected_date,
            'schedule_entries': schedule_entries,
            'schedule_date_counts': schedule_date_counts,
            'is_schedule_write': False,
            'is_schedule_browse': True,
        },
    )


@login_required
def settings_page(request):
    if request.method == 'POST':
        form = PasswordChangeSettingsForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'パスワードを変更しました。')
            return redirect('accounts:settings')
    else:
        form = PasswordChangeSettingsForm(request.user)
    return render(
        request,
        'accounts/settings.html',
        {'form': form},
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
