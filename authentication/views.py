from django.shortcuts import render,redirect
from django.views import View
from django.contrib.auth.models import User
import json
from validate_email import validate_email
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode 
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading
import datetime
# Create your views here.
class EmailThread(threading.Thread):
    def __init__(self,email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        self.email.send(fail_silently=False)

class EmailValidationView(View):
    def post(self,request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error':'Email is invalid'},status=400)
        try:
            if User.objects.filter(email=email).exists():
                return JsonResponse({'email_error':'Sorry email exists use another one'},status=409)
        except:
            pass
        return JsonResponse({'email_valid':True})



class UsernameValidationView(View):
    def post(self,request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error':'username should only contain alphanumeric characters'},status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'Already exists use another one'},status=409)
        return JsonResponse({'username_valid':True})
class RegistrationView(View):
    def get(self,request):
        return render(request,'authentication/register.html')
    def post(self,request):
        #GET USER DATA
        #VALIDATE
        #Create  a user account
        context ={
            'fieldValues':request.POST
        }
        post_data = request.POST
        username = post_data['username']
        email = post_data['email']
        password = post_data['password']
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password)<6:
                    messages.error(request,'Password too short')
                    return render(request,'authentication/register.html',context)

                user = User.objects.create_user(username=username,email=email)
                user.set_password(password)
                user.is_active=False
                user.save()
                #path_to_view
                #relative url to verification
                #encode ui
                #token used only once
                uidb64=urlsafe_base64_encode(force_bytes(user.pk))

                domain = get_current_site(request).domain
                link = reverse('activate',kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})
                activate_url = 'http://'+domain+link
                email_subject = 'Activate your account'
                email_body = 'Hi '+user.username+"Please use this link to verify your account\n"+activate_url
                email = EmailMessage(
                    email_subject,
                    email_body,
                    'jnaneshdana@gmail.com',
                    [email],                    
                )
                EmailThread(email).start()
                messages.success(request,'Account successfully created')
                return render(request,'authentication/register.html')
        return render(request,'authentication/register.html')

class VerificationView(View):
    def get(self,request,uidb64,token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            if not token_generator.check_token(user,token):
                return redirect('login'+'?message='+'User already activated')
            if(user.is_active):
                return redirect('login')
            user.is_active=True
            user.save()
            messages.success(request,'Account activated successfully')
            return redirect('login')
        except Exception as e:
            pass

class LoginView(View):
    def get(self,request):
        return render(request,'authentication/login.html')
    def post(self,request):
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            user = auth.authenticate(username=username,password=password)

            if user:
                if user.is_active:
                    auth.login(request,user)
                    messages.success(request,'Welcome, '+user.username+' you are now logged in')
                    return redirect('expenses')
                messages.error(request,'Account is not active,please check your email')
                return render(request,'authentication/login.html')
            else:
                messages.error(request,'Invalid credentials try again')
                return render(request,'authentication/login.html')
        messages.error(request,'Fill all the fields')
        return render(request,'authentication/login.html')
class LogoutView(View):
    def post(self,request):
        auth.logout(request)
        messages.success(request,'You have been logged out')
        return redirect('login')
class RequestPasswordResetEmail(View):
    def get(self,request):
        return render(request,'authentication/reset-password.html')
    def post(self,request):
        email=request.POST['email']
        context={
            'values': request.POST
        }
        if not validate_email(email):
            messages.error(request,"Enter a valid email")
            return render(request,'authentication/reset-password.html',context)
        user=User.objects.filter(email=email)
        if user.exists():
            uidb64=urlsafe_base64_encode(force_bytes(user[0].pk))
            domain = get_current_site(request).domain
            link = reverse('set-new-password',kwargs={'uidb64':uidb64,'token':default_token_generator.make_token(user[0])})
            reset_url = 'http://'+domain+link
            email_subject = 'Password Reset link'
            email_body = "Hi there\nPlease use this link to reset the password \n"+reset_url
            email = EmailMessage(
                email_subject,
                email_body,
                'jnaneshdana@gmail.com',
                [email],                    
            )
            EmailThread(email).start()
            return render(request,'authentication/reset-password.html')

        messages.success(request,"We have sent you an email to reset the password")
        return render(request,'authentication/reset-password.html')
class CompletePasswordReset(View):
    def get(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            print(type(user),token_generator.check_token(user,token),token)
            if not default_token_generator.check_token(user, token):
                messages.info(request,'Password link is invalid,request a new one')
                return render(request,"authentication/reset-password.html")
        except Exception as e:
            messages.info(request,'Something went wrong Try again')            
            return render(request,'authentication/reset-password.html',context)
        
        
        return render(request,'authentication/set-new-password.html',context)
    def post(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        password = request.POST['password']
        password2 = request.POST['password2']
        if password!=password2:
            messages.error(request,'Passwords do not match')            
            return render(request,'authentication/set-new-password.html',context)
        if len(password)<6:
            messages.error(request,'Password is too small')            
            return render(request,'authentication/set-new-password.html',context)
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset successful, login with your new password")
            return redirect('login')
        except Exception as e:
            messages.info(request,'Something went wrong Try again')            
            return render(request,'authentication/set-new-password.html',context)
        
        