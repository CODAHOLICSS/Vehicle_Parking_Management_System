from django.urls import path
from . import views

app_name='parkingapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('loginadmin/', views.loginadmin, name='loginadmin'),
    path('userLogin/', views.userLogin, name='userLogin'),
    path('userSignup/', views.userSignup, name='userSignup'),
    path('DashboardPage/',views.DashboardPage,name='DashboardPage'),
    path('exit_vehicle/', views.exit_vehicle, name='exit_vehicle'),
    path('payment_success/', views.payment_success, name='payment_success'), # add this line
    path('reservation/<int:reservation_id>/payment/', views.payment_view, name='payment'),
]
