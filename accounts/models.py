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
