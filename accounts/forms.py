import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import DiaryEntry, ExpenseBudget, ExpenseEntry, IncomeEntry, ScheduleEntry

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


class PasswordChangeSettingsForm(forms.Form):
    """ログイン中ユーザーのパスワード変更（登録時と同じ英字ルール）。"""

    _PASSWORD_EN = re.compile(r'^[a-zA-Z]{5,}\Z')

    current_password = forms.CharField(
        label='現在のパスワード',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                **_W,
                'autocomplete': 'current-password',
                'placeholder': '現在のパスワード',
            }
        ),
    )
    new_password1 = forms.CharField(
        label='新しいパスワード',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                **_W,
                'autocomplete': 'new-password',
                'placeholder': '英字5文字以上',
            }
        ),
    )
    new_password2 = forms.CharField(
        label='新しいパスワード（確認）',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                **_W,
                'autocomplete': 'new-password',
                'placeholder': '確認のため再入力',
            }
        ),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        pwd = self.cleaned_data.get('current_password')
        if pwd is None:
            return pwd
        if not self.user.check_password(pwd):
            raise forms.ValidationError(
                '現在のパスワードが正しくありません。',
                code='password_incorrect',
            )
        return pwd

    def clean_new_password1(self):
        pwd = self.cleaned_data.get('new_password1')
        if not pwd:
            return pwd
        if not self._PASSWORD_EN.match(pwd):
            raise forms.ValidationError(
                'パスワードは英字（a〜z, A〜Z）のみ、5文字以上で入力してください。',
                code='password_english_min5',
            )
        return pwd

    def clean(self):
        data = super().clean()
        p1 = data.get('new_password1')
        p2 = data.get('new_password2')
        if p1 and p2 and p1 != p2:
            self.add_error(
                'new_password2',
                ValidationError(
                    '新しいパスワードと確認用が一致しません。',
                    code='password_mismatch',
                ),
            )
        return data


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


class ExpenseEntryForm(forms.ModelForm):
    class Meta:
        model = ExpenseEntry
        fields = ('date', 'amount', 'category', 'note')
        labels = {
            'date': '日付',
            'amount': '金額',
            'category': 'カテゴリ',
            'note': '内容',
        }
        widgets = {
            'date': forms.DateInput(
                attrs={**_INC_W, 'type': 'date', 'autocomplete': 'off'}
            ),
            'amount': forms.NumberInput(
                attrs={**_INC_W, 'min': 1, 'step': 1, 'inputmode': 'numeric'}
            ),
            'category': forms.Select(attrs=_INC_W),
            'note': forms.TextInput(attrs={**_INC_W, 'placeholder': 'メモ'}),
        }
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount is not None and amount <= 0:
            raise forms.ValidationError('金額は1円以上で入力してください。')
        return amount


class DiaryEntryForm(forms.ModelForm):
    class Meta:
        model = DiaryEntry
        fields = ('date', 'title', 'events', 'tomorrow_goals')
        labels = {
            'date': '日付',
            'title': 'タイトル',
            'events': '出来事',
            'tomorrow_goals': '明日の目標',
        }
        widgets = {
            'date': forms.DateInput(
                attrs={**_INC_W, 'type': 'date', 'autocomplete': 'off'}
            ),
            'title': forms.TextInput(
                attrs={**_INC_W, 'placeholder': '今日の日記のタイトル'}
            ),
            'events': forms.Textarea(
                attrs={
                    **_INC_W,
                    'rows': 6,
                    'placeholder': '今日あったことを書きます',
                }
            ),
            'tomorrow_goals': forms.Textarea(
                attrs={
                    **_INC_W,
                    'rows': 4,
                    'placeholder': '明日の目標ややりたいことを書きます',
                }
            ),
        }


class ScheduleEntryForm(forms.ModelForm):
    class Meta:
        model = ScheduleEntry
        fields = ('date', 'time', 'content')
        labels = {
            'date': '日付',
            'time': '時間',
            'content': '予定',
        }
        widgets = {
            'date': forms.HiddenInput(),
            'time': forms.TimeInput(
                attrs={**_INC_W, 'type': 'time', 'autocomplete': 'off'}
            ),
            'content': forms.TextInput(
                attrs={**_INC_W, 'placeholder': '予定を入力してください'}
            ),
        }


_BUDGET_W = {'class': 'auth-input'}


class BudgetSettingsForm(forms.Form):
    """カテゴリごとの月間支出予算。空��は未設定として保存しません。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for value, label in ExpenseBudget.Category.choices:
            self.fields[value] = forms.DecimalField(
                label=label,
                required=False,
                min_value=0,
                max_digits=12,
                decimal_places=0,
                widget=forms.NumberInput(
                    attrs={
                        **_BUDGET_W,
                        'min': 0,
                        'step': 1,
                        'inputmode': 'numeric',
                        'placeholder': '未設定',
                    }
                ),
            )

