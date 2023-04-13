from django.contrib import messages
from django.contrib.messages import get_messages
from .forms import SignUpForm,LoginForm
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from .models import UserProfiles
def index(request):
    return render(request, 'adminPage.html')

@csrf_protect
def login(request):
    return render(request, 'admin_login.html')
def dash(request):
    return render(request,'dash.html')


from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import UserProfiles

def userLogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print('from loginhtml page',email,password)
        try:
            user_profile = UserProfiles.objects.get(email=email)
            user = authenticate(request, username=email, password=password)
            print("from database  ",user_profile.email,user_profile.password)
            print(user)
            testuser = authenticate(username='sim@example.com', password='sim')
            print(testuser)
            if user is not None:
                login(request, user)
                messages.success(request, 'You have been logged in successfully.')
                return redirect('/DashboardPage.html')
            else:
                error_message='Invalid email or password. Please try again.'
                messages.error(request, error_message)
        except UserProfiles.DoesNotExist:
            error_message='Invalid email or password. Please try again.'
            messages.error(request, error_message)

    return render(request, 'userLogin.html')
# def userLogin(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         user = authenticate(request,customuser=UserProfiles.objects.get(email=email),password=password)
#         if user is not None:
#             login(request, user)
#             print("hai")
#             messages.success(request, 'You have been logged in successfully.')
#             print(messages.get_messages(request))
#             return redirect('/DashboardPage.html')
#         else:
#             error_message='Invalid email or password. Please try again.'
#             return render(request,'userLogin.html',{'error_message':error_message})
#
#     else:
#         return render(request, 'userLogin.html')
    # return render(request,'userLogin.html')
def userLoginPage(request):
    return  render(request,'user_login_page.html')

def userPage(request):
    return render(request,'user_page_view.html')

def userSignup(request):
     if request.method=='POST':
         form=SignUpForm(request.POST)
         if form.is_valid():
             post=UserProfiles(
                full_name=form.cleaned_data['full_name'],
                phone_number=form.cleaned_data['phone_number'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
             )
             post.save()
             messages.success(request,"Your account has been created successfully")
             return redirect('/')
     else:
         form=SignUpForm()
     return render(request,'userSignup.html',{'form':form})
