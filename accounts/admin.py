from django.contrib import admin

from .models import ExpenseEntry, IncomeEntry


@admin.register(IncomeEntry)
class IncomeEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'amount', 'note', 'created_at')
    list_filter = ('date',)
    search_fields = ('note',)
    date_hierarchy = 'date'


@admin.register(ExpenseEntry)
class ExpenseEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'amount', 'note', 'created_at')
    list_filter = ('date',)
    search_fields = ('note',)
    date_hierarchy = 'date'
