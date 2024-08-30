from django.urls import path, include
from userprefences import views

urlpatterns = [
    path('', views.index, name='preferences'),
]