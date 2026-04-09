import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import IncomeEntry

_LOGIN_ERR = 'メールアドレスまたはパスワードが正しくありません。'
_W = {'class': 'auth-input'}


def _email_field():
    return forms.EmailField(
        label='メールアドレス',
        widget=forms.EmailInput(
            attrs={**_W, 'placeholder': '名前を入力', 'autocomplete': 'email'}
        ),
    )


class EmailLoginForm(forms.Form):
    email = _email_field()
    password = forms.CharField(
        label='パスワード',
        strip=False,
        widget=forms.PasswordInput(
            attrs={**_W, 'placeholder': '名前を入力', 'autocomplete': 'current-password'}
        ),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        email, password = data.get('email'), data.get('password')
        if not email or not password:
            return data
        row = User.objects.filter(email__iexact=email).first()
        user = (
            authenticate(self.request, username=row.username, password=password)
            if row
            else None
        )
        if user is None:
            raise forms.ValidationError(_LOGIN_ERR, code='invalid_login')
        data['user'] = user
        return data


class RegisterForm(UserCreationForm):
    _PASSWORD_EN = re.compile(r'^[a-zA-Z]{5,}\Z')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        u = self.fields['username']
        u.label, u.help_text = 'メールアドレス', ''
        u.widget = forms.EmailInput(
            attrs={**_W, 'placeholder': '名前を入力', 'autocomplete': 'email'}
        )
        self.fields['password1'].label = 'パスワード'
        self.fields['password1'].help_text = '英字（a〜z, A〜Z）のみ、5文字以上'
        self.fields['password1'].validators = []
        self.fields['password2'].label = 'パスワード（確認）'
        self.fields['password2'].help_text = ''
        for name, ph in (
            ('password1', '英字5文字以上'),
            ('password2', '確認のため再入力'),
        ):
            self.fields[name].widget.attrs.update(
                {**_W, 'placeholder': ph, 'autocomplete': 'new-password'}
            )

    def validate_password_for_user(self, user, password_field_name='password2'):
        pw = self.cleaned_data.get(password_field_name)
        if not pw or self._PASSWORD_EN.match(pw):
            return
        self.add_error(
            password_field_name,
            ValidationError(
                'パスワードは英字（a〜z, A〜Z）のみ、5文字以上で入力してください。',
                code='password_english_min5',
            ),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['username']
        if commit:
            user.save()
            self.save_m2m()
        return user


_INC_W = {'class': 'auth-input'}


class IncomeEntryForm(forms.ModelForm):
    class Meta:
        model = IncomeEntry
        fields = ('date', 'amount', 'note')
        labels = {
            'date': '日付',
            'amount': '金額',
            'note': '内容',
        }
        widgets = {
            'date': forms.DateInput(
                attrs={**_INC_W, 'type': 'date', 'autocomplete': 'off'}
            ),
            'amount': forms.NumberInput(
                attrs={**_INC_W, 'min': 1, 'step': 1, 'inputmode': 'numeric'}
            ),
            'note': forms.TextInput(attrs={**_INC_W, 'placeholder': 'メモ'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount is not None and amount <= 0:
            raise forms.ValidationError('金額は1円以上で入力してください。')
        return amount
