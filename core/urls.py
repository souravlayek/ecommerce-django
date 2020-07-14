from django.urls import path
from .views import HomeView, ItemDetailView, add_to_cart, remove_from_cart, OrderSummaryView, remove_single_item_from_cart, CheckoutView, PaymentView

app_name = "core"

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('order-summary/', OrderSummaryView.as_view(), name="ordersummary"),
    path('checkout/', CheckoutView.as_view(), name="checkout"),
    path('payment/<payment_option>', PaymentView.as_view(), name="payment"),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add_to_cart/<slug>/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<slug>/', remove_from_cart, name='remove_from_cart'),
    path('remove_single_item_from_cart/<str:task>/<slug>/',
         remove_single_item_from_cart, name='remove_single_item_from_cart'),

]
