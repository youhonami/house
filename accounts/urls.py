from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.top, name='top'),
    path('income/', views.income, name='income'),
    path('expense/', views.expense, name='expense'),
    path('summary/daily/', views.daily_summary, name='daily_summary'),
    path('summary/monthly/', views.monthly_summary, name='monthly_summary'),
    path(
        'summary/entry/income/<int:pk>/',
        views.monthly_income_entry,
        name='monthly_income_entry',
    ),
    path(
        'summary/entry/expense/<int:pk>/',
        views.monthly_expense_entry,
        name='monthly_expense_entry',
    ),
    path('goals/', views.goal_settings, name='goal_settings'),
    path('diary/write/', views.diary_write, name='diary_write'),
    path('diary/browse/', views.diary_browse, name='diary_browse'),
    path('settings/', views.settings_page, name='settings'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
