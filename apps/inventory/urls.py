from django.urls import path

from . import views


app_name = "inventory"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("reports/", views.reports, name="reports"),
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.product_create, name="product_create"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),
    path("stock-levels/", views.stock_level_list, name="stock_level_list"),
    path("transfers/", views.transfer_list, name="transfer_list"),
]
