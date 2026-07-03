from django.urls import path

from . import views


app_name = "inventory"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("products/", views.product_list, name="product_list"),
    path("warehouses/", views.warehouse_list, name="warehouse_list"),
    path("transfers/", views.transfer_list, name="transfer_list"),
]
