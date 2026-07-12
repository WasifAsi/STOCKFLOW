import csv

from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import redirect, render

from .forms import CategorySelectForm, ProductCreateForm, StockMovementForm
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
def reports(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)

    movement_base = StockMovement.objects.all()
    transfer_base = StockTransfer.objects.all()

    def movement_summary(queryset):
        summary = queryset.aggregate(total_quantity=Sum("quantity"), movement_count=Count("id"))
        return {
            "total_quantity": summary["total_quantity"] or 0,
            "movement_count": summary["movement_count"] or 0,
        }

    daily_movements = movement_base.filter(created_at__date=today)
    monthly_movements = movement_base.filter(created_at__date__gte=month_start)

    daily_summary = {
        "incoming": movement_summary(daily_movements.filter(movement_type__in=[StockMovement.MovementType.RECEIPT, StockMovement.MovementType.TRANSFER_IN])),
        "sales": movement_summary(daily_movements.filter(movement_type=StockMovement.MovementType.ISSUE)),
        "transfers": {
            "total_quantity": daily_movements.filter(movement_type__in=[StockMovement.MovementType.TRANSFER_IN, StockMovement.MovementType.TRANSFER_OUT]).aggregate(
                total_quantity=Sum("quantity")
            )["total_quantity"] or 0,
            "movement_count": daily_movements.filter(movement_type__in=[StockMovement.MovementType.TRANSFER_IN, StockMovement.MovementType.TRANSFER_OUT]).aggregate(
                movement_count=Count("id")
            )["movement_count"] or 0,
        },
        "stock_transfers": {
            "count": transfer_base.filter(created_at__date=today).count(),
            "total_quantity": transfer_base.filter(created_at__date=today).aggregate(total_quantity=Sum("quantity"))["total_quantity"] or 0,
        },
    }

    monthly_summary = {
        "incoming": movement_summary(monthly_movements.filter(movement_type__in=[StockMovement.MovementType.RECEIPT, StockMovement.MovementType.TRANSFER_IN])),
        "sales": movement_summary(monthly_movements.filter(movement_type=StockMovement.MovementType.ISSUE)),
        "transfers": {
            "total_quantity": monthly_movements.filter(movement_type__in=[StockMovement.MovementType.TRANSFER_IN, StockMovement.MovementType.TRANSFER_OUT]).aggregate(
                total_quantity=Sum("quantity")
            )["total_quantity"] or 0,
            "movement_count": monthly_movements.filter(movement_type__in=[StockMovement.MovementType.TRANSFER_IN, StockMovement.MovementType.TRANSFER_OUT]).aggregate(
                movement_count=Count("id")
            )["movement_count"] or 0,
        },
        "stock_transfers": {
            "count": transfer_base.filter(created_at__date__gte=month_start).count(),
            "total_quantity": transfer_base.filter(created_at__date__gte=month_start).aggregate(total_quantity=Sum("quantity"))["total_quantity"] or 0,
        },
    }

    recent_movements = StockMovement.objects.select_related("product", "warehouse", "performed_by").order_by("-created_at")[:12]
    recent_transfers = StockTransfer.objects.select_related(
        "product", "from_warehouse", "to_warehouse", "requested_by", "approved_by"
    ).order_by("-created_at")[:12]

    if request.GET.get("format") == "csv":
        detail_mode = request.GET.get("detail") == "1"
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="stockflow-movement-detail.csv"'
            if detail_mode
            else 'attachment; filename="stockflow-reports.csv"'
        )

        writer = csv.writer(response)
        if detail_mode:
            writer.writerow(["Record Type", "Date", "Reference", "Type", "Product", "Warehouse", "From Warehouse", "To Warehouse", "Quantity", "User", "Status"])

            for movement in StockMovement.objects.select_related(
                "product", "warehouse", "performed_by", "transfer", "transfer__from_warehouse", "transfer__to_warehouse"
            ).order_by("-created_at"):
                writer.writerow([
                    "Movement",
                    movement.created_at.isoformat(sep=" ", timespec="seconds"),
                    movement.reference,
                    movement.get_movement_type_display(),
                    movement.product.name,
                    movement.warehouse.name,
                    movement.transfer.from_warehouse.name if movement.transfer else "",
                    movement.transfer.to_warehouse.name if movement.transfer else "",
                    movement.quantity,
                    str(movement.performed_by),
                    "",
                ])

            for transfer in StockTransfer.objects.select_related(
                "product", "from_warehouse", "to_warehouse", "requested_by", "approved_by"
            ).order_by("-created_at"):
                writer.writerow([
                    "Transfer",
                    transfer.created_at.isoformat(sep=" ", timespec="seconds"),
                    transfer.reference,
                    transfer.get_status_display(),
                    transfer.product.name,
                    "",
                    transfer.from_warehouse.name,
                    transfer.to_warehouse.name,
                    transfer.quantity,
                    str(transfer.requested_by),
                    transfer.get_status_display(),
                ])
        else:
            writer.writerow(["Period", "Category", "Metric", "Value"])
            writer.writerow(["Daily", "Sales", "Count", daily_summary["sales"]["movement_count"]])
            writer.writerow(["Daily", "Sales", "Quantity", daily_summary["sales"]["total_quantity"]])
            writer.writerow(["Daily", "Incoming", "Count", daily_summary["incoming"]["movement_count"]])
            writer.writerow(["Daily", "Incoming", "Quantity", daily_summary["incoming"]["total_quantity"]])
            writer.writerow(["Daily", "Transfers", "Count", daily_summary["stock_transfers"]["count"]])
            writer.writerow(["Daily", "Transfers", "Quantity", daily_summary["stock_transfers"]["total_quantity"]])
            writer.writerow(["Monthly", "Sales", "Count", monthly_summary["sales"]["movement_count"]])
            writer.writerow(["Monthly", "Sales", "Quantity", monthly_summary["sales"]["total_quantity"]])
            writer.writerow(["Monthly", "Incoming", "Count", monthly_summary["incoming"]["movement_count"]])
            writer.writerow(["Monthly", "Incoming", "Quantity", monthly_summary["incoming"]["total_quantity"]])
            writer.writerow(["Monthly", "Transfers", "Count", monthly_summary["stock_transfers"]["count"]])
            writer.writerow(["Monthly", "Transfers", "Quantity", monthly_summary["stock_transfers"]["total_quantity"]])
        return response

    return render(
        request,
        "inventory/reports.html",
        {
            "today": today,
            "month_start": month_start,
            "daily_summary": daily_summary,
            "monthly_summary": monthly_summary,
            "recent_movements": recent_movements,
            "recent_transfers": recent_transfers,
        },
    )


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
def product_create(request):
    selected_category_id = request.GET.get("category")
    category_form = CategorySelectForm(request.GET or None)

    if request.method == "POST":
        selected_category_id = request.POST.get("category") or selected_category_id
        form = ProductCreateForm(request.POST, category_id=selected_category_id)
        if form.is_valid():
            product = form.save()
            return redirect("inventory:product_detail", product_id=product.id)
    else:
        form = ProductCreateForm(category_id=selected_category_id)

    return render(
        request,
        "inventory/product_form.html",
        {
            "category_form": category_form,
            "form": form,
            "show_product_form": bool(selected_category_id),
        },
    )


@login_required
def product_detail(request, product_id):
    product = Product.objects.select_related("category", "supplier").prefetch_related("attribute_values__definition").get(
        id=product_id
    )
    stock_levels = product.stock_levels.select_related("warehouse")
    return render(request, "inventory/product_detail.html", {"product": product, "stock_levels": stock_levels})


@login_required
def stock_level_list(request):
    search_query = request.GET.get("q", "").strip()
    product_queryset = Product.objects.select_related("category").prefetch_related("attribute_values__definition")
    if search_query:
        product_queryset = product_queryset.filter(
            Q(name__icontains=search_query)
            | Q(sku__icontains=search_query)
            | Q(category__name__icontains=search_query)
            | Q(attribute_values__value__icontains=search_query)
            | Q(attribute_values__definition__name__icontains=search_query)
        ).distinct()

    if request.method == "POST" and request.POST.get("form_type") == "movement":
        movement_form = StockMovementForm(
            request.POST,
            product_queryset=product_queryset,
            warehouse_queryset=Warehouse.objects.all(),
        )
        if movement_form.is_valid():
            try:
                movement_form.save(performed_by=request.user)
            except Exception as exc:
                movement_form.add_error(None, exc)
            else:
                return redirect("inventory:stock_level_list")
    else:
        movement_form = StockMovementForm(
            product_queryset=product_queryset,
            warehouse_queryset=Warehouse.objects.all(),
        )

    stock_levels = StockLevel.objects.select_related("product", "warehouse").order_by("warehouse__name", "product__name")
    return render(
        request,
        "inventory/stock_level_list.html",
        {
            "movement_form": movement_form,
            "stock_levels": stock_levels,
            "search_query": search_query,
        },
    )


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
