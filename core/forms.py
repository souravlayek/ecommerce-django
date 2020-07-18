from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': "1234 Main St",
        'class': 'form-control',
        'id': 'address'
    }))
    appertment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': " Apartment or suite",
        'class': 'form-control',
        'id': 'address-2'
    }))
    # class="custom-select d-block w-100" id="country"
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        'class': 'custom-select d-block w-100',
        'id': 'country'
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': "zip"
    }))
    save_billing_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_options = forms.ChoiceField(
        widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'promocode',
        'aria-label': "Recipient's username",
        'aria-describedby': "basic-addon2"
    }))
