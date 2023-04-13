from django.contrib import admin
# Register your models here.
from .models import CustomerProfile, CustomerVehicle, CreditCard, ParkingLot, ParkingReservation, ParkingSpaceBooking
from django.utils.safestring import mark_safe

# Register your models here.
admin.site.register(CustomerProfile)
admin.site.register(CreditCard)
admin.site.register(ParkingLot)
admin.site.register(ParkingReservation)
admin.site.register(CustomerVehicle)



#from parkingapp.models import Payment

class ParkingReservationAdmin(admin.ModelAdmin):
    # existing code for the admin class
    
    def pay(self, request, queryset):
        for reservation in queryset:
            payment = Payment.objects.create(
                amount=reservation.cost,
                card_number=reservation.card_number,
                cardholder_name=reservation.cardholder_name,
                expiration_month=reservation.expiration_month,
                expiration_year=reservation.expiration_year,
                cvv=reservation.cvv
            )
            payment.charge()
            reservation.is_paid = True
            reservation.save()
    
    pay.short_description = "Mark selected reservations as paid"
    actions = [pay]

#admin.site.register(ParkingReservation, ParkingReservationAdmin)


@admin.register(ParkingSpaceBooking)
class ParkingSpaceBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'parking_space', 'is_paid')
    list_filter = ('is_paid',)
    search_fields = ('user__email', 'parking_space__name', 'Customervehicle__license_plate')
    actions = ('mark_as_paid',)

    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True)
    # Your admin options here

    


