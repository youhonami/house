from django.conf import settings
from django.db import models


class IncomeEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='income_entries',
    )
    date = models.DateField('日付')
    amount = models.DecimalField('金額', max_digits=12, decimal_places=0)
    note = models.CharField('内容', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at', '-id']
        verbose_name = '収入'
        verbose_name_plural = '収入'

    def __str__(self):
        return f'{self.date} {self.amount} {self.note or ""}'


class ExpenseBudget(models.Model):
    """カテゴリ別の月間支出予算（目標）。"""

    class Category(models.TextChoices):
        RENT = 'rent', '\u5bb6\u8cc3'
        FOOD = 'food', '\u98df\u8cbb'
        UTILITIES = 'utilities', '\u5149\u71b1\u8cbb'
        SOCIAL = 'social', '\u4ea4\u969b\u8cbb'
        COMMUNICATION = 'communication', '\u901a\u4fe1\u8cbb'
        DAILY_GOODS = 'daily_goods', '\u65e5\u7528\u54c1'
        TRANSPORT = 'transport', '\u4ea4\u901a\u8cbb'
        MEDICAL = 'medical', '\u533b\u7642\u30fb\u5065\u5eb7'
        INSURANCE = 'insurance', '\u4fdd\u967a'
        EDUCATION = 'education', '\u6559\u80b2\u30fb\u7fd2\u3044\u4e8b'
        OTHER = 'other', '\u305d\u306e\u4ed6'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expense_budgets',
    )
    category = models.CharField(
        'カテゴリ',
        max_length=32,
        choices=Category.choices,
    )
    monthly_amount = models.DecimalField(
        '\u6708\u9593\u4e88\u7b97\uff08\u5186\uff09',
        max_digits=12,
        decimal_places=0,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'category'),
                name='accounts_expensebudget_user_category_uniq',
            ),
        ]
        ordering = ['category']
        verbose_name = '支出予算'
        verbose_name_plural = '支出予算'

    def __str__(self):
        return f'{self.user_id} {self.get_category_display()} {self.monthly_amount}'


class ExpenseEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expense_entries',
    )
    date = models.DateField('日付')
    amount = models.DecimalField('金額', max_digits=12, decimal_places=0)
    category = models.CharField(
        'カテゴリ',
        max_length=32,
        choices=ExpenseBudget.Category.choices,
        default=ExpenseBudget.Category.OTHER,
    )
    note = models.CharField('内容', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at', '-id']
        verbose_name = '支出'
        verbose_name_plural = '支出'

    def __str__(self):
        return f'{self.date} {self.amount} {self.note or ""}'


class DiaryEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='diary_entries',
    )
    date = models.DateField('日付')
    title = models.CharField('タイトル', max_length=200)
    events = models.TextField('出来事', blank=True)
    tomorrow_goals = models.TextField('明日の目標', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at', '-id']
        verbose_name = '日記'
        verbose_name_plural = '日記'

    def __str__(self):
        return f'{self.date} {self.title}'
