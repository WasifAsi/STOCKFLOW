from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.shortcuts import render

from .models import Product, StockLevel, StockMovement, StockTransfer, Warehouse


@login_required
def dashboard(request):
    low_stock_levels = (
        StockLevel.objects.select_related("product", "warehouse")
        .filter(quantity__lte=F("product__reorder_point"))
        .order_by("quantity", "product__name")[:8]
    )
    context = {
        "warehouse_count": Warehouse.objects.count(),
        "product_count": Product.objects.count(),
        "transfer_count": StockTransfer.objects.count(),
        "movement_count": StockMovement.objects.count(),
        "low_stock_levels": low_stock_levels,
        "recent_movements": StockMovement.objects.select_related("product", "warehouse", "performed_by")[:10],
        "recent_transfers": StockTransfer.objects.select_related(
            "product", "from_warehouse", "to_warehouse", "requested_by"
        )[:10],
    }
    return render(request, "inventory/dashboard.html", context)


@login_required
def product_list(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.select_related("category", "supplier").prefetch_related("attribute_values__definition")
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(sku__icontains=query)
            | Q(category__name__icontains=query)
            | Q(attribute_values__value__icontains=query)
            | Q(attribute_values__definition__name__icontains=query)
        ).distinct()
    return render(request, "inventory/product_list.html", {"products": products, "query": query})


@login_required
def warehouse_list(request):
    warehouses = Warehouse.objects.select_related("manager")
    return render(request, "inventory/warehouse_list.html", {"warehouses": warehouses})


@login_required
def transfer_list(request):
    transfers = StockTransfer.objects.select_related(
        "product", "from_warehouse", "to_warehouse", "requested_by", "approved_by"
    )
    return render(request, "inventory/transfer_list.html", {"transfers": transfers})
