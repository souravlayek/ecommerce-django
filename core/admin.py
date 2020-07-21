from django.contrib import admin
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund


def make_refun_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refun_accepted.short_description = 'update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'billing_address', 'shipping_address', 'payment', 'coupon', 'ordered', 'being_delivered',
                    'received', 'refund_requested', 'refund_granted']
    list_display_links = [
        'user', 'billing_address', 'shipping_address', 'payment', 'coupon'
    ]
    list_filter = ['user', 'ordered', 'being_delivered',
                   'received', 'refund_requested', 'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [
        make_refun_accepted
    ]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'appertment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]

    list_filter = [
        'address_type',
        'default',
        'country'
    ]
    search_fields = [
        'user',
        'street_address',
        'appertment_address',
        'zip'
    ]


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
