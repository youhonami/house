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
