from django.contrib import admin
from .models import CustomerProfile, CustomerVehicle, CreditCard, ParkingLot, ParkingReservation, ParkingSpaceBooking
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.html import format_html


# Register your models here.
admin.site.register(CustomerProfile)
admin.site.register(CreditCard)
admin.site.register(ParkingLot)
admin.site.register(CustomerVehicle)


class ParkingReservationAdmin(admin.ModelAdmin):
    list_display = ('users_id', 'Customervehicle_id', 'parking_lot', 'start_time', 'end_time', 'is_active', 'is_paid', 'custom_button')
    
    def custom_button(self, obj):
        url = reverse('parkingapp:create_checkout_session')
        return format_html('<a class="button" href="{}">Pay</a>', url)
    
    custom_button.short_description = 'Pay'


admin.site.register(ParkingReservation, ParkingReservationAdmin)


@admin.register(ParkingSpaceBooking)
class ParkingSpaceBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'parking_reservation', 'is_paid', 'parking_lot')
    list_filter = ('is_paid',)
    search_fields = ('user__email', 'parking_space__name', 'Customervehicle__license_plate')
    actions = ('mark_as_paid',)

    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True)
    # Your admin options here
