from django.urls import path
from . import views

app_name='parkingapp'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('loginadmin/', views.loginadmin, name='loginadmin'),
    path('DashboardPage/',views.DashboardPage,name='DashboardPage'),
    path('product_page/', views.product_page, name='product_page'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
	path('payment_successful/', views.payment_successful, name='payment_successful'),
	path('payment_cancelled/', views.payment_cancelled, name='payment_cancelled'),
	path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
]
