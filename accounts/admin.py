from django.contrib import admin

from .models import IncomeEntry


@admin.register(IncomeEntry)
class IncomeEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'amount', 'note', 'created_at')
    list_filter = ('date',)
    search_fields = ('note',)
    date_hierarchy = 'date'
