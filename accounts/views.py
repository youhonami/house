from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import EmailLoginForm, RegisterForm


def _home():
    return redirect(settings.LOGIN_REDIRECT_URL)


@login_required
def top(request):
    return render(request, 'accounts/top.html')


def _stub_ctx(title_suffix: str, heading: str, note: str):
    return {'title_suffix': title_suffix, 'heading': heading, 'note': note}


@login_required
def income(request):
    return render(
        request,
        'accounts/placeholder.html',
        _stub_ctx('収入入力', '収入入力', 'ここに収入入力の内容を追加予定です。'),
    )


@login_required
def expense(request):
    return render(
        request,
        'accounts/placeholder.html',
        _stub_ctx('支出入力', '支出入力', 'ここに支出入力の内容を追加予定です。'),
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
