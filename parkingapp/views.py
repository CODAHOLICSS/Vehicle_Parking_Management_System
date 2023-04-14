from time import sleep
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views import View
from .models import ParkingReservation, ParkingSpaceBooking, UserPayment

# Create your views here.
def homepage(request):
    return render(request, 'homepage.html')


@login_required(login_url='/login/')
def DashboardPage(request):
    return render(request, 'DashboardPage.html')


@csrf_protect
def loginadmin(request):
    return render(request, 'admin_login.html')


def LogoutPage(request):
    print("In logout bef")
    logout(request)
    print("after")
    messages.info(request, "You have successfully logged out.")
    print("In logout")
    return redirect('index')



stripe.api_key = settings.STRIPE_SECRET_KEY



@login_required(login_url='/loginadmin/')
def create_checkout_session(request):
    try:
        price = stripe.Price.create(
            unit_amount=2000,  # the price amount in cents
            currency='usd',
            product='prod_Ni17A6AIEO9uID',  # the ID of the product this price belongs to
            nickname='One-time payment',  # a description of the price
            recurring=None,  # set the price to be one-time
        )

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price.id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://127.0.0.1:8000/success.html',
            cancel_url='http://127.0.0.1:8000/cancel.html',
        )
    except Exception as e:
        return HttpResponse(str(e))

    return redirect(checkout_session.url)


def product_page(request):
    return render(request, "user_payment/product_page.html")


## use Stripe dummy card: 4242 4242 4242 4242
@login_required(login_url='/loginadmin/')
def payment_successful(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
    checkout_session_id = request.GET.get('session_id', None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    customer = stripe.Customer.retrieve(session.customer)
    user_id = request.user.id
    user_payment = UserPayment.objects.get(app_user=user_id)
    user_payment.stripe_checkout_id = checkout_session_id
    user_payment.save()
    return render(request, 'user_payment/payment_successful.html', {'customer': customer})


@login_required(login_url='/loginadmin/')
def payment_cancelled(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
    return render(request, 'user_payment/payment_cancelled.html')


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
    sleep(10)
    payload = request.body
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, settings.STRIPE_WEBHOOK_SECRET_TEST
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id', None)
        sleep(15)
        user_payment = UserPayment.objects.get(stripe_checkout_id=session_id)
        user_payment.payment_bool = True
        user_payment.save()
    return HttpResponse(status=200)
