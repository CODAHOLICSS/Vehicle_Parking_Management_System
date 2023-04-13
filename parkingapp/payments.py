from stripe.api import StripeClient
from parkingapp.models import ParkingReservation

reservation = ParkingReservation.objects.get(id=1)  # get a reservation instance

# create a stripe client with your api key
stripe = StripeClient(api_key='your_stripe_secret_key')

# charge the customer using their card details
charge = stripe.charges.create(
    amount=reservation.total_price,  # amount to charge in cents
    currency='usd',  # currency of the charge
    customer=reservation.customer.stripe_customer_id,  # customer id of the reservation's customer
    source=reservation.customer.card_token,  # card token of the customer's card
    description='Parking reservation payment'  # description of the charge
)

# update the reservation status and charge id
reservation.status = 'paid'
reservation.charge_id = charge.id
reservation.save()
