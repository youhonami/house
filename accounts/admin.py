from django.contrib import admin

from .models import ExpenseBudget, ExpenseEntry, IncomeEntry


@admin.register(IncomeEntry)
class IncomeEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'amount', 'note', 'created_at')
    list_filter = ('date',)
    search_fields = ('note',)
    date_hierarchy = 'date'


@admin.register(ExpenseEntry)
class ExpenseEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'category', 'amount', 'note', 'created_at')
    list_filter = ('date',)
    search_fields = ('note',)
    date_hierarchy = 'date'


@admin.register(ExpenseBudget)
class ExpenseBudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'monthly_amount', 'updated_at')
    list_filter = ('category',)
