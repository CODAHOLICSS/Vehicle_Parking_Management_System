from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import ParkingReservation, ParkingSpaceBooking
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.utils import timezone






# Create your views here.
def index(request):
    return render(request,'adminPage.html')


@login_required(login_url='login')
def DashboardPage(request):
    return render(request,'DashboardPage.html')

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


@login_required
def parking_checkout(request, reservation_id):
    reservation = get_object_or_404(ParkingReservation, id=reservation_id)
    if reservation.paid:
        messages.warning(request, 'This reservation has already been paid for.')
        return HttpResponseRedirect(reverse('admin:parking_parkingreservation_changelist'))
    else:
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': reservation.calculate_total_price(),
                        'product_data': {
                            'name': f'Parking reservation {reservation_id}',
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "reservation_id": reservation_id
            },
            mode='payment',
            success_url=YOUR_DOMAIN + reverse('parking_payment_success', args=[reservation_id]),
            cancel_url=YOUR_DOMAIN + reverse('parking_payment_cancel', args=[reservation_id]),
        )
        return JsonResponse({
            'id': checkout_session.id
        })

"""
@login_required
def payment_view(request, reservation_id):
    reservation = get_object_or_404(ParkingReservation, id=reservation_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Create a Payment object and save it
            payment = form.save(commit=False)
            payment.reservation = reservation
            payment.amount = reservation.calculate_total_price()
            payment.save()
            # Mark the reservation as paid
            reservation.paid = True
            reservation.save()
            # Redirect to a success page
            return redirect('payment_success')
    else:
        form = PaymentForm()
        return render(request, 'payment.html', {'form': form, 'reservation': reservation})
"""


def payment_success(request):
    return render(request, 'payment_success.html')


def payment_view(request, reservation_id):
    reservation = get_object_or_404(ParkingReservation, id=reservation_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.reservation = reservation
            payment.amount = reservation.calculate_total_price()
            payment.save()
            reservation.charge_customer(payment.amount) # assuming you already have this method implemented
            messages.success(request, 'Payment made successfully!')
            return HttpResponseRedirect(reverse('admin:parking_parkingreservation_changelist'))
    else:
        form = PaymentForm()
    return render(request, 'payment_form.html', {'form': form, 'reservation': reservation})




def exit_vehicle(request):
    # get all active parking reservations
    reservations = ParkingReservation.objects.filter(is_active=True)
    
    # check if a vehicle has been selected for exit
    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')
        reservation = ParkingReservation.objects.get(pk=reservation_id)
        # set the exit_date of the vehicle to the current time
        reservation.vehicle_id.exit_date = timezone.now()
        reservation.vehicle_id.save()
        # mark the parking reservation as inactive
        reservation.is_active = False
        reservation.save()
        # redirect to the same page to display updated list of vehicles
        return redirect('exit_vehicle')

    context = {'reservations': reservations}
    return render(request, 'exit_vehicle.html', context)

def userSignup(request):
      print("hello inside usersignup")
      if request.method == 'POST':
        print("hello inside POST")
        username=request.POST['user_name']
        full_name = request.POST['full_name']
        email = request.POST['email']
        password = request.POST['password']
        print("HELLO THE CREDENTIALS ARE")
        print(full_name,email,password)
        # Create a new user object
        user = User.objects.create_user(username=username,first_name=full_name, email=email,password=password)
        # user.full_name = full_name
        # user.phone_number = phone_number
        user.save()
        # Authenticate the user and log them in
        user = authenticate(request, username=email, password=password)
        if user is not None and hasattr(user, '_meta'):
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect('Veh_App:DashboardPage')

      messages.error(request, "Unsuccessful registration. Invalid information.")
      return render(request, 'userSignup.html')
#$#########
def userLogin(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('password')
        print(username,pass1)
        user=authenticate(request,username=username,password=pass1)
        print(user)
        if user is not None:
            login(request,user)
            messages.info(request, f"You are now logged in as {username}.")
            return redirect('Veh_App:DashboardPage')
        else:
            context = {'error': 'Invalid credentials'}
            return render(request, 'userlogin.html', context)
    else:
        return render(request, 'userLogin.html')



def book_parking_space(request, space_id):
    space = ParkingSpaceBooking.objects.get(id=space_id)

    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        payment_method = request.POST.get('payment_method')
        card_number = request.POST.get('card_number')
        cardholder_name = request.POST.get('cardholder_name')
        expiration_date = request.POST.get('expiration_date')

        # Validate payment information
        if not payment_method or not card_number or not cardholder_name or not expiration_date:
            return HttpResponse('Invalid payment information')

        # Calculate the price for the booking
        duration_hours = (end_time - start_time).total_seconds() / 3600
        price_per_hour = space.price_per_hour
        total_price = duration_hours * price_per_hour

        # Charge the payment using Stripe
        stripe.api_key = "your_stripe_api_key"
        try:
            charge = stripe.Charge.create(
                amount=int(total_price * 100),
                currency="usd",
                source=card_number,
                description="Parking space booking payment"
            )
            is_paid = True
        except stripe.error.CardError as e:
            is_paid = False

        # Create a new booking object
        booking = ParkingSpaceBooking.objects.create(
            user=request.user,
            parking_space=space,
            start_time=start_time,
            end_time=end_time,
            is_paid=is_paid
        )

        # Update the space status if payment is successful
        if is_paid:
            space.is_available = False
            space.save()

        return render(request, 'booking_success.html', {'booking': booking})

    return render(request, 'book_parking_space.html', {'space': space})

