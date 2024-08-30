from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
import re
from django.views import View
import json 
from django.http import JsonResponse
from django.contrib.auth.models import User
from email_validator import validate_email, EmailNotValidError
from django.contrib import messages, auth
from django.core.mail import EmailMessage  
import threading 

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({"Username_error": "Username should only contain alphanumeric characters"}, status=400)

        if User.objects.filter(username).exists():
            return JsonResponse({"Username_error": "sorry, username in use; Choose another one"}, status=409)
        return JsonResponse({"Username_error": True})
    
class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return JsonResponse({"Email_error": "Email is invalid"}, status=400)
        
        if not email:
            return JsonResponse({"Email_error": "Email is required"}, status=400)

        if User.objects.filter(email).exists():
            return JsonResponse({"Email_error": "sorry, email in use; Choose another one"}, status=409)
        return JsonResponse({"Email_error": True})
    
class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        # GET USER DATA
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password'] 
        context = {
            'fieldValues': request.POST
        }

        # VALIDATE
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already in use')
            return render(request, 'authentication/register.html', context)

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already in use')
            return render(request, 'authentication/register.html', context)

        if len(password) < 6:
            messages.error(request, 'Password too short')
            return render(request, 'authentication/register.html', context)

        # CREATE A USER ACCOUNT
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False  # Usually set to False until the user verifies the email
        user.save()

        # Generate the activation link
        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        activation_url = f'http://{current_site.domain}{activation_link}'

        # SEND EMAIL
        email_subject = "Activate your account"
        email_body = render_to_string('authentication/activation_email.html', {
            'user': user,
            'activation_url': activation_url,
        })
        email_sender = "noreply@mailme.com"
        email_receiver = email
        
        try:
            email = EmailMessage(
                email_subject,
                email_body,
                email_sender,
                [email_receiver],
            )
            EmailThread(email).start()
        except Exception as e:
            messages.error(request, f'Error sending email: {e}')
            user.delete()  # Optionally, delete the user if email sending fails
            return render(request, 'authentication/register.html', context)

        messages.success(request, 'Account successfully created, please check your email to activate your account.')
        return render(request, 'authentication/register.html', context)  # Redirect to a page instructing the user to check their email
    
class ActivationView(View):
    def get(self, request, uidb64, token):
        context = {
            'fieldValues': request.POST
        }
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Thank you for your email confirmation. You can now log in to your account.')
            return render(request, 'authentication/login.html', context)

        else:
            messages.error(request, 'Activation link is invalid!')
            return redirect('authentication/confirmation.html')
        
class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, f'Successfully login to your account {username}.')
                    return render(request, 'expenses/index.html')
                
                messages.error(request, 'Account is not active. Please, verify your email')
                return render(request, 'authentication/login.html')
            
            messages.error(request, 'Invalid credentials, try again')
            return render(request, 'authentication/login.html')

        messages.error(request, 'Please, fill all fields')
        return render(request, 'authentication/login.html')
    

class LogoutView(View):
    def get(self, request):
        pass

    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')
    
class reset_password(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')

    def post(self, request):
        email = request.POST['email']

        context = {
            'values': request.POST
        }

        if not validate_email(email):
            messages.error(request, 'Please supply a valid email')
            return render(request, 'authentication/reset-password.html', context)
        
        user = User.objects.filter(email=email)
        current_site = get_current_site(request)

        if user.exists():
            email_contents = {
            'user': user[0],
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
            'token': default_token_generator.make_token(user[0]),
        }

            link = reverse('reset_password', kwargs={
                            'uidb64': email_contents['uid'], 'token': email_contents['token']})

            email_subject = 'Password reset instruction'

            reset_url = 'http://'+current_site.domain+link

            email = EmailMessage(
                email_subject,
                render_to_string('authentication/reset-pass-message.html', {
                    'user': user,
                    'reset_url': reset_url,
                }),
                'noreply.com',
                [email],
            )
            EmailThread(email).start()

        messages.success(request, 'We have sent you an email to reset your password')
    
        return render(request, 'authentication/reset-password.html')

      
    
class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not default_token_generator.check_token(user, token):
                messages.info(request, 'Password link is invalid, Please request a new one')
                return render(request, 'authentication/reset-password.html')

            # If token is valid, render the set new password page
            return render(request, 'authentication/set-newpassword.html', context)
        
        except User.DoesNotExist:
            messages.info(request, 'User not found')
            return render(request, 'authentication/reset-password.html', context)
        except Exception as e:
            messages.info(request, 'Something went wrong, please try again')
            return render(request, 'authentication/reset-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'The 2 passwords didn\'t match')
            return render(request, 'authentication/set-newpassword.html', context)
        
        if len(password) < 6:
            messages.error(request, 'Password too short')
            return render(request, 'authentication/set-newpassword.html', context)
        
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            messages.success(request, 'Password reset successful, login now')
            return redirect('login')
        except User.DoesNotExist:
            messages.info(request, 'User not found')
            return render(request, 'authentication/set-newpassword.html', context)
        except Exception as e:
            messages.info(request, 'Something went wrong, try again')
            return render(request, 'authentication/set-newpassword.html', context)
