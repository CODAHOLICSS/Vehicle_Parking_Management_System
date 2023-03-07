from django.urls import path
from . import views
app_name='parkingapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('dash/', views.dash, name='dash'),
    # path('index/', views.login, name='login'),
    path('userLogin/', views.userLogin, name='userLogin'),
    # path('userLoginPage/', views.loginPage, name='user_login_page'),
    path('userPage/', views.userPage, name='user_page_view'),
    path('userSignup/', views.userSignup, name='userSignup'),


]
