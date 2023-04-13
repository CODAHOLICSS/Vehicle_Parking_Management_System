from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.db.models import signals
from django.apps import AppConfig
from django.core.validators import validate_email
import stripe
from django.conf import settings


stripe.api_key = settings.STRIPE_SECRET_KEY



class CustomerProfile(models.Model):
    full_name = models.CharField(max_length=200)
    phone_number = models.BigIntegerField()
    email = models.CharField(unique=True, max_length=200, validators=[validate_email])
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone_number']

    #def set_password(self, password):
       # self.password = make_password(password)

   # def check_password(self, password):
     #   return check_password(password, self.password)

    def __str__(self):
        return self.full_name or self.email


class CustomerVehicle(models.Model):
    user_id = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    Customervehicle_name=models.CharField(max_length=200)
    plate_number=models.CharField(max_length=10)
    color=models.CharField(max_length=20)
    is_active=models.BooleanField()
    entry_date= models.DateTimeField()
    updated_date=models.DateTimeField(null=True, blank=True)
    exit_date=models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.Customervehicle_name
    
    
class CreditCard(models.Model):
    users_id=models.ForeignKey(CustomerProfile,on_delete=models.CASCADE)
    card_number=models.BigIntegerField()
    cardholder_name=models.CharField(max_length=200)
    expiration_date=models.DateField()
    is_default=models.BooleanField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cardholder_name


class ParkingLot(models.Model):
    name=models.CharField(max_length=200)
    location=models.CharField(max_length=200)
    total_spaces=models.IntegerField()
    available_space=models.IntegerField()

    def __str__(self):
        return self.name
    


class ParkingReservation(models.Model):
    users_id = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    Customervehicle_id = models.ForeignKey(CustomerVehicle, on_delete=models.CASCADE)
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField()
    is_paid = models.BooleanField(default=False)
    
    
    
    # Define _original_is_active attribute
    _original_is_active = None

    def __init__(self, *args, **kwargs):
        super(ParkingReservation, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if self.is_active:
            # Decrease available_space of related ParkingLot by 1
            self.parking_lot.available_space -= 1
            self.parking_lot.save()
        
        elif is_new and not self.is_active:
            self.parking_lot.available_space == self.parking_lot.available_space    
        
        elif not self.is_active:
            # Increase available_space of related ParkingLot by 1 if reservation was deleted
            self.parking_lot.available_space += 1
            self.parking_lot.save()
        self._original_is_active = self.is_active

    def delete(self, *args, **kwargs):
        # Check if the instance is active before deleting it
        if self.is_active:
            # Increment available_space of related ParkingLot by 1 if reservation was deleted
            self.parking_lot.available_space += 1
            self.parking_lot.save()
        super().delete(*args, **kwargs)


    def charge_customer(self, token, amount):
        # Charge the customer using the given token and amount
        try:
            charge = stripe.Charge.create(
                amount=int(amount * 100),  # convert amount to cents
                currency="usd",
                description="Parking Reservation",
                source=token,
            )

            # update is_paid field of the model instance to True
            self.is_paid = True
            self.save()

            return True

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            print("Status is: %s" % e.http_status)
            print("Type is: %s" % err.get('type'))
            print("Code is: %s" % err.get('code'))
            # param is '' in this case
            print("Param is: %s" % err.get('param'))
            print("Message is: %s" % err.get('message'))
            return False

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            return False

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            return False

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return False

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            return False

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            return False

        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            return False

    def __str__(self):
        return f"{self.users_id.email}: {self.start_time} - {self.end_time}"
    
@receiver(post_save, sender=ParkingReservation)
def update_parking_lot(sender, instance, **kwargs):
    if instance.pk:
        # Update available_space field of the related ParkingLot model
        if kwargs['created'] or instance.is_active != instance._original_is_active:
            instance.parking_lot.available_space -= 1
            instance.parking_lot.save()

        if instance.Customervehicle_id.exit_date is not None:
            instance.parking_lot.available_space += 1
            instance.parking_lot.save()

        # Update exit_date of the related CustomerVehicle model
        if instance.Customervehicle_id.exit_date is None:
            instance.Customervehicle_id.exit_date = timezone.now()
            instance.Customervehicle_id.save()

        # Update is_paid field of the related Reservation model
        reservation_instance = ParkingReservation.objects.filter(Customervehicle_id=instance.Customervehicle_id).first()
        if reservation_instance and reservation_instance.is_paid != instance.is_paid:
            reservation_instance.is_paid = instance.is_paid
            reservation_instance.save()
        
        instance._original_is_active = instance.is_active


        
class ParkingSpaceBooking(models.Model):
    user = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    parking_reservation = models.ForeignKey(ParkingReservation, on_delete=models.CASCADE, default=None)
    is_paid = models.BooleanField(default=False)
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)

    def parking_space(self):
        # calculate the corresponding parking space based on the parking_lot field
        # and return it as a string
        return f"{self.parking_lot.name} - {self.parking_lot.available_space}/{self.parking_lot.total_spaces}"
    parking_space.short_description = 'Parking Space'

    def clean(self):
        super().clean()
        if self.parking_reservation and self.parking_reservation.users_id != self.user:
            raise ValidationError('You cannot book another user\'s reservation.')

    def save(self, *args, **kwargs):
        if self.pk:
            original_parking_space_booking = ParkingSpaceBooking.objects.get(pk=self.pk)

            if original_parking_space_booking.parking_reservation is not None:
                original_parking_reservation = ParkingReservation.objects.get(pk=original_parking_space_booking.parking_reservation.pk)
                original_parking_lot = ParkingLot.objects.get(pk=original_parking_reservation.parking_lot.pk)

                # If the parking reservation has changed, increment the available_space of the old parking lot
                if original_parking_reservation != self.parking_reservation:
                    original_parking_lot.available_space += 1
                    original_parking_lot.save()

            if self.parking_reservation is not None:
                new_parking_reservation = ParkingReservation.objects.get(pk=self.parking_reservation.pk)
                new_parking_lot = ParkingLot.objects.get(pk=new_parking_reservation.parking_lot.pk)

                # If the parking reservation has changed, decrement the available_space of the new parking lot
                if original_parking_space_booking.parking_reservation != self.parking_reservation:
                    new_parking_lot.available_space -= 1
                    new_parking_lot.save()

        super().save(*args, **kwargs)

class ParkingSpaceBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'parking_reservation', 'is_paid')

    def save_model(self, request, obj, form, change):
        if not obj.parking_reservation:
            # create a new parking reservation for the admin
            reservation = ParkingReservation.objects.create(
                parking_lot=obj.parking_lot,
                start_time=timezone.now(),
                end_time=timezone.now() + timezone.timedelta(hours=1),
                is_paid=True
            )
            obj.parking_reservation = reservation

        # check if the parking reservation for the booking belongs to the same user
        if obj.parking_reservation and obj.parking_reservation.users_id != obj.user:
            raise ValidationError('You cannot book another user\'s reservation.')

        if change:
            obj.save()
        else:
            super().save_model(request, obj, form, change)




@receiver(signals.post_save, sender=ParkingReservation)
def update_parking_reservation_booking_is_paid(sender, instance, **kwargs):
    # Get all the ParkingSpaceBooking objects that are associated with this reservation
    bookings = ParkingSpaceBooking.objects.filter(parking_reservation=instance)

    # Update the is_paid field of each booking
    for booking in bookings:
        booking.is_paid = instance.is_paid
        booking.save()



class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'parkingapp'


#class Payment(models.Model):
 #   users_id=models.ForeignKey(CustomerProfiles,on_delete=models.CASCADE)
  #  reservation_id=models.ForeignKey(ParkingReservations,on_delete=models.CASCADE)
   # card_id=models.ForeignKey(CreditCards, on_delete=models.CASCADE)
    #amount=models.FloatField()
    #is_successful=models.BooleanField()
    #created_at=models.DateTimeField(auto_now_add=True)
