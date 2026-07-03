from django.contrib import admin

from .models import Category, Product, StockLevel, StockMovement, StockTransfer, Supplier, Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "location", "manager", "is_active")
    search_fields = ("name", "code", "location")
    list_filter = ("is_active",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_name", "email", "phone")
    search_fields = ("name", "contact_name", "email")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "supplier", "unit", "reorder_point", "is_active")
    search_fields = ("sku", "name")
    list_filter = ("is_active", "category", "supplier")


@admin.register(StockLevel)
class StockLevelAdmin(admin.ModelAdmin):
    list_display = ("product", "warehouse", "quantity", "reserved_quantity", "available_quantity")
    search_fields = ("product__name", "product__sku", "warehouse__name")
    list_filter = ("warehouse",)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("movement_type", "product", "warehouse", "quantity", "performed_by", "created_at")
    list_filter = ("movement_type", "warehouse")
    search_fields = ("product__name", "product__sku", "reference")


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ("reference", "product", "quantity", "from_warehouse", "to_warehouse", "status")
    list_filter = ("status",)
    search_fields = ("reference", "product__name", "product__sku")
