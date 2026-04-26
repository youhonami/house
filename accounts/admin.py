from django.contrib import admin

from .models import DiaryEntry, ExpenseBudget, ExpenseEntry, IncomeEntry, ScheduleEntry


@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'title', 'created_at')
    list_filter = ('date',)
    search_fields = ('title', 'events', 'tomorrow_goals')
    date_hierarchy = 'date'


@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'user', 'content', 'created_at')
    list_filter = ('date',)
    search_fields = ('content',)
    date_hierarchy = 'date'


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
