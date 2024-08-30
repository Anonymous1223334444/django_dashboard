from django.urls import path
from userincome import views
from django.views.decorators.csrf import csrf_exempt, csrf_protect

urlpatterns = [
    path('', views.home, name='income'),
    path('add_income', views.add_income, name='add_income'),
    path('income-edit/<int:id>', views.income_edit, name='income-edit'),
    path('delete-income/<int:id>', views.income_delete, name='income_delete'), 
    path('search-income', csrf_exempt(views.search_income), name='search_income'), 
]
