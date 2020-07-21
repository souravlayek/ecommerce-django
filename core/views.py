from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm, CouponForm, RefundForm
import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home-page.html"


class OrderSummaryView(View, LoginRequiredMixin):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
        except ObjectDoesNotExist:
            messages.error(self.request, 'You don\'t have an active order ')
            return redirect('/')

        return render(self.request, "order_summary.html", context)


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order,
            'DISPLAY_COUPON_FORM': False
        }
        return render(self.request, 'payment.html', context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total_price()) * 77
        print(amount)
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="inr",
                source=token,
                description="My First Test Charge (created for API docs)",
            )
            # payment set
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total_price()
            payment.save()

            # order set\
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()
            order.ordered = True
            order.payment = payment
            # TODO assign the ref code
            ref_code = create_ref_code()
            print(ref_code)
            order.ref_code = ref_code
            order.save()

            messages.success(self.request, "order has succesfully done")
            return redirect('/')

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            messages.error(self.request, f"{e.error.message}")

            print('Status is: %s' % e.http_status)
            print('Type is: %s' % e.error.type)
            print('Code is: %s' % e.error.code)
            # param is '' in this case
            print('Param is: %s' % e.error.param)
            print('Message is: %s' % e.error.message)

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, f"{e.error.message}")
            return redirect('/')

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.error(self.request, "Invalid Parameters")
            return redirect('/')

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Not authenticated")
            return redirect('/')

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network Error")
            return redirect('/')

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(
                self.request, "Something went wrong please try again.")
            return redirect('/')

        except Exception as e:
            # send an email to ourselves
            print(e)
            messages.error(
                self.request, "A serious error occurred, we have been notified")
            return redirect('/')


class CheckoutView(View):
    def get(self, *args, **kwargs):
        # forms
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, 'checkout.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have any active order")
            return redirect("core:checkout")

        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, 'checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                appertment_address = form.cleaned_data.get(
                    'appertment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                payment_options = form.cleaned_data.get('payment_options')
                billing_address = Address(user=self.request.user,
                                          street_address=street_address,
                                          appertment_address=appertment_address,
                                          country=country,
                                          zip=zip,
                                          address_type='B'
                                          )
                billing_address.save()
                order.billing_address = billing_address
                order.shipping_address = billing_address
                order.save()
                if payment_options == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_options == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(self.request, 'Invalid payment Option')
                    return redirect('core:checkout')

            messages.warning(self.request, 'Failed Checkout')
            return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error('You don\'t have an active order ')
            return redirect('core:checkout')


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, create = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(
                request, "This item quantity was updated to your cart")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")

    return redirect("core:product", slug=slug)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have any active order")
        return redirect("core:product", slug=slug)
    return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, task, slug):
    item = get_object_or_404(Item, slug=slug)

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False)[0]
            if task == 'add':
                order_item.quantity += 1
                order_item.save()
                messages.info(
                    request, "This item quantity was updated to your cart")
                return redirect("core:ordersummary")
            else:
                if order_item.quantity > 0:
                    order_item.quantity -= 1
                    order_item.save()
                    messages.info(
                        request, "This item quantity was updated to your cart")
                    return redirect("core:ordersummary")
                else:
                    messages.info(
                        request, "You have no item to remove.")
                    return redirect("core:ordersummary")

        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:ordersummary")
    else:
        messages.info(request, "You do not have any active order")
        return redirect("core:ordersummary")
    return redirect("core:ordersummary")


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This is not a valid coupon")
        return redirect("core:checkout")


class AddCoupon(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "successully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have any active order")
                return redirect("core:checkout")


class RequestRefund(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, 'request_refund.html', context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()
                refund = Refund()
                refund.order = order
                refund.message = message
                refund.email = email
                refund.save()
                messages.info(self.request, 'Successfully requested refund')
                return redirect('core:request-refund')

            except ObjectDoesNotExist:
                messages.info(self.request, 'this order doesnot exist')
                return redirect('core:request-refund')
        else:
            messages.info(self.request, 'given information is wrong')
            return redirect('core:request-refund')
