from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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
        self.fields['password2'].label = 'パスワード（確認）'
        for name, ph in (
            ('password1', '8文字以上'),
            ('password2', '確認のため再入力'),
        ):
            self.fields[name].widget.attrs.update(
                {**_W, 'placeholder': ph, 'autocomplete': 'new-password'}
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['username']
        if commit:
            user.save()
            self.save_m2m()
        return user
