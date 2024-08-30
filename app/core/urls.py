from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt, csrf_protect

urlpatterns = [
    path('', views.home, name='expenses'),
    path('add_expenses', views.add_expenses, name='add_expenses'),
    path('expense-edit/<int:id>', views.expense_edit, name='expense-edit'),
    path('delete-expense/<int:id>', views.expense_delete, name='expense_delete'), 
    path('search-expenses', csrf_exempt(views.search_expenses), name='search_expenses'), 
    path('expense_category_summary', views.expense_category_summary, name='expense_category_summary'), 
    path('stats_view', views.stats_view, name='stats'), 
    path('export_csv', views.export_csv, name='export_csv'), 
    path('export_excel', views.export_excel, name='export_excel'), 
    path('export_pdf', views.export_pdf, name='export_pdf'), 
]
