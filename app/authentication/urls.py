from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt, csrf_protect

urlpatterns = [
    path('', views.RegistrationView.as_view(), name='register'),
    path('/login', views.LoginView.as_view(), name='login'),
    path('/logout', views.LogoutView.as_view(), name='logout'),
    path('/validate-username', csrf_exempt(views.UsernameValidationView.as_view()), name='validate-username'),
    path('/validate-email', csrf_exempt(views.EmailValidationView.as_view()), name='validate-email'),
    path('/reset-password', csrf_exempt(views.reset_password.as_view()), name='reset-password'),
    path('/activate/<uidb64>/<token>/', views.ActivationView.as_view(), name='activate'),
    path('/set-new-password/<uidb64>/<token>/', views.CompletePasswordReset.as_view(), name='reset_password'),
]
    