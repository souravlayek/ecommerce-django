from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, OrderItem, Order
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


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
            messages.error('You don\'t have an active order ')
            return redirect('/')

        return render(self.request, "order_summary.html", context)


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"


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
