from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.
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
def userLogin(request):
    return render(request,'userLogin.html')
def userLoginPage(request):
    return  render(request,'user_login_page.html')

def userPage(request):
    return render(request,'user_page_view.html')

def userSignup(request):
     if request.method=='POST':
        full_name=request.POST.get('full_name',)
        phone_number=request.POST.get('phone_number',)
        email=request.POST.get('email',)
        password=request.POST.get('password',)
        user1=UserProfiles(full_name=full_name,phone_number=phone_number,email=email,password=password)
        user1.save()
        return redirect('/')
     return render(request,'userSignup.html')
